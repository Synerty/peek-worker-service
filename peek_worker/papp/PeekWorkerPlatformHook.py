from typing import overload

from papp_base.worker.PeekWorkerPlatformHookABC import PeekWorkerPlatformHookABC


class PeekWorkerPlatformHook(PeekWorkerPlatformHookABC):

    def getOtherPappApi(self, pappName:str):
        """ Get Other Papp API
        """
        raise Exception("Workers don't share APIs")
