from __future__ import absolute_import

from papp_base.PeekWorkerApiBase import PeekWorkerApiBase


class PeekWorkerApi(PeekWorkerApiBase):
    @property
    def celeryApp(self):
        from peek_worker.PeekWorkerApp import peekWorkerApp
        return peekWorkerApp

    def configureCeleryApp(self, pappCeleryApp):
        from peek_worker.PeekWorkerApp import configureCeleryApp
        configureCeleryApp(pappCeleryApp)

