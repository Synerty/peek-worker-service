import logging
from typing import Type

from papp_base.PappCommonEntryHookABC import PappCommonEntryHookABC
from papp_base.worker.PappWorkerEntryHookABC import PappWorkerEntryHookABC
from peek_platform.papp import PappLoaderABC
from peek_worker.papp.PeekWorkerPlatformHook import PeekWorkerPlatformHook

logger = logging.getLogger(__name__)


# class _CeleryLoaderMixin:
#     ''' Celery Loader Mixin
#
#     Separate some logic out into this class
#
#     '''
#
#     @property
#     def celeryAppIncludes(self):
#         includes = []
#         for pappWorkerMain in list(self._loadedPapps.values()):
#             includes.extend(pappWorkerMain.celeryAppIncludes)
#         return includes


class PappWorkerLoader(PappLoaderABC):#, _CeleryLoaderMixin):
    _instance = None

    def __new__(cls, *args, **kwargs):
        assert cls._instance is None, "PappWorkerLoader is a singleton, don't construct it"
        cls._instance = PappLoaderABC.__new__(cls)
        return cls._instance

    @property
    def _entryHookFuncName(self) -> str:
        return "peekWorkerEntryHook"

    @property
    def _entryHookClassType(self):
        return PappWorkerEntryHookABC

    @property
    def _platformServiceNames(self) -> [str]:
        return ["worker"]

    def _loadPappThrows(self, pappName: str, EntryHookClass: Type[PappCommonEntryHookABC],
                        pappRootDir: str) -> None:

        # Everyone gets their own instance of the papp API
        platformApi = PeekWorkerPlatformHook()

        pappMain = EntryHookClass(pappName=pappName,
                                  pappRootDir=pappRootDir,
                                  platform=platformApi)

        # Load the papp
        pappMain.load()

        # Configure the celery app in the worker
        # This is not the worker that will be started, it allows the worker to queue tasks
        from peek_platform.CeleryApp import configureCeleryApp
        configureCeleryApp(pappMain.celeryApp)

        # Start the Papp
        pappMain.start()


        self._loadedPapps[pappName] = pappMain


pappWorkerLoader = PappWorkerLoader()
