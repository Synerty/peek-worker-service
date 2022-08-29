from typing import overload

from peek_plugin_base.worker.PeekWorkerPlatformHookABC import (
    PeekWorkerPlatformHookABC,
)


class PeekWorkerPlatformHook(PeekWorkerPlatformHookABC):
    def getOtherPluginApi(self, pluginName: str):
        """Get Other Plugin API"""
        raise Exception("Workers don't share APIs")

    @property
    def serviceId(self) -> str:
        import socket

        return "worker|" + socket.gethostname()

    @property
    def peekServerSSL(self) -> bool:
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config.peekServerUseSSL

    @property
    def peekServerSSLEnableMutualTLS(self) -> bool:
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config.peekServerSSLEnableMutualTLS

    @property
    def peekServerSSLClientBundleFilePath(self) -> str:
        from peek_platform import PeekPlatformConfig

        return PeekPlatformConfig.config.peekServerSSLClientBundleFilePath

    @property
    def peekServerSSLClientMutualTLSCertificateAuthorityBundleFilePath(
        self,
    ) -> str:
        from peek_platform import PeekPlatformConfig

        return (
            PeekPlatformConfig.config.peekServerSSLClientMutualTLSCertificateAuthorityBundleFilePath
        )
