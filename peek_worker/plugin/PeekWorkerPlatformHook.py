from typing import overload

from peek_plugin_base.worker.PeekWorkerPlatformHookABC import PeekWorkerPlatformHookABC


class PeekWorkerPlatformHook(PeekWorkerPlatformHookABC):

    def getOtherPluginApi(self, pluginName:str):
        """ Get Other Plugin API
        """
        raise Exception("Workers don't share APIs")
