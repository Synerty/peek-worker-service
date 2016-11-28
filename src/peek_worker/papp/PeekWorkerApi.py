

from papp_base.worker.PeekWorkerApiBase import PeekWorkerApiBase


class PeekWorkerApi(PeekWorkerApiBase):
    @property
    def celeryApp(self):
        from peek_platform.CeleryApp import celeryApp
        return celeryApp

    def configureCeleryApp(self, pappCeleryApp):
        from peek_platform.CeleryApp import configureCeleryApp
        configureCeleryApp(pappCeleryApp)

    @property
    def dbEngine(self):
        from papp_base.worker.CeleryDbConn import dbEngine
        return dbEngine

    @property
    def dbSession(self):
        from papp_base.worker.CeleryDbConn import dbSession
        return dbSession