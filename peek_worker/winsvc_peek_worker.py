import logging


# import peek_worker

import win32serviceutil
import win32service
import win32event

from twisted.internet import reactor
from twisted.internet.defer import Deferred

logger = logging.getLogger(__name__)

class PeekSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "peek_worker"
    _svc_display_name_ = "Peek Worker " #+ peek_worker.__version__

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

        reactor.addSystemEventTrigger('after', 'shutdown', self._notifyOfStop)

    def _notifyOfStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def _notifyOfStart(self):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

        # Shutting down celery workers
        from peek_worker.CeleryApp import celeryApp
        celeryApp.control.broadcast('shutdown')

    def SvcDoRun(self):
        try:
            from peek_worker import run_peek_worker

            # # Setup service status notifiers
            # self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
            # reactor.callLater(1, self._notifyOfStart)

            # # Prioritise this import to ensure configureCeleryLogging is registered
            # # as the first celery worker signal
            # from peek_platform import ConfigCeleryApp
            # ConfigCeleryApp.__unused = False

            # from peek_plugin_base.worker import CeleryDbConnInit
            # CeleryDbConnInit.__unused = False
        
            # # Patch the restart method for windows services
            # class _Restart:
            #     def _restartProcess(self):
            #         from peek_worker.CeleryApp import celeryApp
            #         celeryApp.control.broadcast('shutdown')

            # # Patch the restart call for windows
            # from peek_worker.sw_install.PeekSwInstallManager import PeekSwInstallManager
            # PeekSwInstallManager.restartProcess = _Restart._restartProcess

            # from peek_platform.util.LogUtil import setupServiceLogOutput
            # setupServiceLogOutput(PeekSvc._svc_name_)

            run_peek_worker.main()

        except Exception as e:
            logger.exception(e)
            raise




# end patch

def main():
    win32serviceutil.HandleCommandLine(PeekSvc)


if __name__ == '__main__':
    main()
