from peek_worker.papp.PappWorkerLoader import pappWorkerLoader
from peek_platform.sw_install.PappSwInstallManagerBase import PappSwInstallManagerBase


class PappSwInstallManager(PappSwInstallManagerBase):
    def notifyOfPappVersionUpdate(self, pappName, targetVersion):
        pappWorkerLoader.loadPapp(pappName)


pappSwInstallManager = PappSwInstallManager()
