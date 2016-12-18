import logging

from twisted.internet import reactor

from peek_platform.sw_install.PluginSwInstallManagerABC import PluginSwInstallManagerABC
from peek_worker.sw_install.PeekSwInstallManager import peekSwInstallManager

logger = logging.getLogger(__name__)

class PluginSwInstallManager(PluginSwInstallManagerABC):
    def notifyOfPluginVersionUpdate(self, pluginName, targetVersion):
        logger.info("%s software update to %s complete", pluginName, targetVersion)
        reactor.callLater(1.0, peekSwInstallManager.restartProcess)


pluginSwInstallManager = PluginSwInstallManager()
