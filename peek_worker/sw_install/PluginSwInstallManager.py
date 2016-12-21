import logging

from twisted.internet import reactor

from peek_platform import PeekPlatformConfig
from peek_platform.sw_install.PluginSwInstallManagerBase import PluginSwInstallManagerBase

logger = logging.getLogger(__name__)


class PluginSwInstallManager(PluginSwInstallManagerBase):
    def notifyOfPluginVersionUpdate(self, pluginName, targetVersion):
        logger.info("%s software update to %s complete", pluginName, targetVersion)
        reactor.callLater(1.0, PeekPlatformConfig.peekSwInstallManager.restartProcess)
