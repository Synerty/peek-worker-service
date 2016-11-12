import imp
import logging
import sys
from _collections import defaultdict

import os

from peek_worker.PeekWorkerConfig import peekWorkerConfig
from peek_worker.papp.PeekWorkerApi import PeekWorkerApi
from peek_platform.papp.PappLoaderBase import PappLoaderBase
from rapui.site.ResourceUtil import removeResourcePaths, registeredResourcePaths
from rapui.vortex.PayloadIO import PayloadIO
from rapui.vortex.Tuple import removeTuplesForTupleNames, \
    registeredTupleNames, tupleForTupleName

logger = logging.getLogger(__name__)


class _CeleryLoaderMixin:
    ''' Celery Loader Mixin

    Separate some logic out into this class

    '''
    @property
    def celeryAppIncludes(self):
        includes = []
        for pappWorkerMain in self._loadedPapps.values():
            includes.extend(pappWorkerMain.celeryAppIncludes)
        return includes


class PappWorkerLoader(PappLoaderBase, _CeleryLoaderMixin):
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert cls._instance is None, "PappWorkerLoader is a singleton, don't construct it"
        cls._instance = cls()
        return cls._instance

    def __init__(self):
        PappLoaderBase.__init__(self)

        from peek_worker.PeekWorkerConfig import peekWorkerConfig
        self._pappPath = peekWorkerConfig.pappSoftwarePath

        self._rapuiTupleNamesByPappName = defaultdict(list)

    def unloadPapp(self, pappName):
        oldLoadedPapp = self._loadedPapps.get(pappName)

        if not oldLoadedPapp:
            return

        # Remove the registered tuples
        removeTuplesForTupleNames(self._rapuiTupleNamesByPappName[pappName])
        del self._rapuiTupleNamesByPappName[pappName]

        self._unloadPappPackage(pappName, oldLoadedPapp)

    def loadPapp(self, pappName):
        self.unloadPapp(pappName)

        pappDirName = peekWorkerConfig.pappDir(pappName)

        if not pappDirName:
            logger.warning("Papp dir name for %s is missing, loading skipped",
                           pappName)
            return

        # Make note of the initial registrations for this papp
        endpointInstancesBefore = set(PayloadIO().endpoints)
        resourcePathsBefore = set(registeredResourcePaths())
        tupleNamesBefore = set(registeredTupleNames())

        # Everyone gets their own instance of the papp API
        workerPlatformApi = PeekWorkerApi()

        srcDir = os.path.join(self._pappPath, pappDirName, 'pypy')
        sys.path.append(srcDir)

        modPath = os.path.join(srcDir, pappName, "PappWorkerMain.py")
        if not os.path.exists(modPath) and os.path.exists(modPath + u"c"):  # .pyc
            PappWorkerMainMod = imp.load_compiled('%s.PappWorkerMain' % pappName,
                                                  modPath + u'c')
        else:
            PappWorkerMainMod = imp.load_source('%s.PappWorkerMain' % pappName,
                                                modPath)

        peekClient = PappWorkerMainMod.PappWorkerMain(workerPlatformApi)


        self._loadedPapps[pappName] = peekClient

        # Configure the celery app in the worker
        # This is not the worker that will be started, it allows the worker to queue tasks

        from peek_worker.PeekWorkerApp import configureCeleryApp
        configureCeleryApp(peekClient.celeryApp)

        peekClient.start()
        sys.path.pop()

        # Make note of the final registrations for this papp
        if set(PayloadIO().endpoints) - endpointInstancesBefore:
            raise Exception("Workers should not be registering endpoints")

        if set(registeredResourcePaths()) - resourcePathsBefore:
            raise Exception("Workers should not be registering http resources")

        self._rapuiTupleNamesByPappName[pappName] = list(
            set(registeredTupleNames()) - tupleNamesBefore)

        self.sanityCheckWorkerPapp(pappName)

    def sanityCheckWorkerPapp(self, pappName):
        ''' Sanity Check Papp

        This method ensures that all the things registed for this papp are
        prefixed by it's pappName, EG papp_noop
        '''

        # all tuple names must start with their pappName
        for tupleName in self._rapuiTupleNamesByPappName[pappName]:
            TupleCls = tupleForTupleName(tupleName)
            if not tupleName.startswith(pappName):
                raise Exception("Tuple name does not start with '%s', %s (%s)"
                                % (pappName, tupleName, TupleCls.__name__))

    def notifyOfPappVersionUpdate(self, pappName, pappVersion):
        logger.info("Received PAPP update for %s version %s", pappName, pappVersion)
        return self.loadPapp(pappName)


pappWorkerLoader = PappWorkerLoader()
