import logging

from twisted.internet import reactor

from peek_platform.sw_install.PappSwInstallManagerBase import PappSwInstallManagerBase
from peek_worker.sw_install.PeekSwInstallManager import peekSwInstallManager

logger = logging.getLogger(__name__)

class PappSwInstallManager(PappSwInstallManagerBase):
    def notifyOfPappVersionUpdate(self, pappName, targetVersion):
        logger.info("%s software update to %s complete", pappName, targetVersion)
        reactor.callLater(1.0, peekSwInstallManager.restartProcess)


pappSwInstallManager = PappSwInstallManager()
