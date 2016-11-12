from celery.signals import worker_shutdown

import logging
from time import sleep

from peek_worker.papp.PappWorkerLoader import pappWorkerLoader
from peek_platform.sw_install.PeekSwInstallManagerBase import PeekSwInstallManagerBase

__author__ = 'synerty'

logger = logging.getLogger(__name__)


class PeekSwInstallManager(PeekSwInstallManagerBase):
    def _stopCode(self):
        pappWorkerLoader.unloadAllPapps()

    def _upgradeCode(self):
        pass

    def _startCode(self):
        pappWorkerLoader.loadAllPapps()

    def restartProcess(self):
        # When we receive this signal, the processes have already been instructed
        # to shutdown
        @worker_shutdown.connect
        def twistedShutdown(sender, signal):
            logger.info("Restarting process")
            PeekSwInstallManagerBase.restartProcess(self)

        from peek_worker.PeekWorkerApp import peekWorkerApp
        logger.info("Shutting down celery workers")
        peekWorkerApp.control.broadcast('shutdown')

        # Give it time to shutdown
        sleep(2)


peekSwInstallManager = PeekSwInstallManager()
