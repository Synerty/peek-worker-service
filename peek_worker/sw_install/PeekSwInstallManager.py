import logging

from peek_platform.sw_install.PeekSwInstallManagerBase import PeekSwInstallManagerBase
from peek_worker.plugin.WorkerPluginLoader import workerPluginLoader

__author__ = 'synerty'

logger = logging.getLogger(__name__)


class PeekSwInstallManager(PeekSwInstallManagerBase):

    def __init__(self):
        PeekSwInstallManagerBase.__init__(self)
        self._restarting  = False

    def _stopCode(self):
        workerPluginLoader.unloadAllPlugins()

    def _upgradeCode(self):
        pass

    def _startCode(self):
        workerPluginLoader.loadAllPlugins()

    def restartProcess(self):
        # When we receive this signal, the processes have already been instructed
        # to shutdown

        self._restarting = True

        from peek_platform.CeleryApp import celeryApp
        logger.info("Shutting down celery workers")
        celeryApp.control.broadcast('shutdown')


    @property
    def restartTriggered(self):
        return self._restarting

    def realyRestartProcess(self):
        PeekSwInstallManagerBase.restartProcess(self)


peekSwInstallManager = PeekSwInstallManager()
