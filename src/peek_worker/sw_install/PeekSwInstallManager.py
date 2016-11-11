from peek_worker.papp.PappWorkerLoader import pappWorkerLoader
from peek_platform.sw_install.PeekSwInstallManagerBase import PeekSwInstallManagerBase

__author__ = 'synerty'


class PeekSwInstallManager(PeekSwInstallManagerBase):

    def _stopCode(self):
        pappWorkerLoader.unloadAllPapps()

    def _upgradeCode(self):
        pass

    def _startCode(self):
        pappWorkerLoader.loadAllPapps()


peekSwInstallManager = PeekSwInstallManager()
