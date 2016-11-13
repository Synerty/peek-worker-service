import logging
from time import sleep

from celery.signals import worker_shutdown

import run_peek_worker
from peek_platform.sw_install.PeekSwInstallManagerBase import PeekSwInstallManagerBase
from peek_worker.papp.PappWorkerLoader import pappWorkerLoader

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

        run_peek_worker.peekWorkerRestarting = True

        from peek_platform.CeleryApp import celeryApp
        logger.info("Shutting down celery workers")
        celeryApp.control.broadcast('shutdown')

        # Give it time to shutdown
        sleep(2)


peekSwInstallManager = PeekSwInstallManager()
