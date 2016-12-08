

from papp_base.worker.PeekWorkerProviderABC import PeekWorkerProviderABC


class PeekWorkerApi(PeekWorkerProviderABC):
    # @property
    # def celeryApp(self):
    #     from peek_platform.CeleryApp import celeryApp
    #     return celeryApp

    def configureCeleryApp(self, pappCeleryApp):
        from peek_platform import configureCeleryApp
        configureCeleryApp(pappCeleryApp)

    @property
    def dbEngine(self):
        from papp_base.worker.CeleryDbConn import getDbEngine
        return getDbEngine()

    @property
    def dbSession(self):
        from papp_base.worker.CeleryDbConn import getDbSession
        return getDbSession()