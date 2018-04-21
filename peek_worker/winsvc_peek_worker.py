import platform

import peek_worker
from peek_platform.util.LogUtil import setupServiceLogOutput

try:
    import win32serviceutil
    import win32service
    import win32event
except ImportError as e:
    if platform.system() is "Windows":
        raise

from twisted.internet import reactor
from twisted.internet.defer import Deferred

from peek_worker import run_peek_worker


class PeekSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "peek_worker"
    _svc_display_name_ = "Peek Worker " + peek_worker.__version__

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

        reactor.addSystemEventTrigger('after', 'shutdown', self._notifyOfStop)

    def _notifyOfStop(self, _):
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def _notifyOfStart(self, _):
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

        # Shutting down celery workers
        from peek_worker.CeleryApp import celeryApp
        celeryApp.control.broadcast('shutdown')

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        d = Deferred()
        d.addBoth(self._notifyOfStart)

        run_peek_worker.main(d)


# Patch the restart method for windows services
class _Restart:
    def _restartProcess(self):
        win32serviceutil.RestartService(PeekSvc._svc_name_)


# Patch the restart call for windows

from peek_worker.sw_install.PeekSwInstallManager import PeekSwInstallManager
PeekSwInstallManager.restartProcess = _Restart._restartProcess


# end patch

def main():
    setupServiceLogOutput(PeekSvc._svc_name_)
    win32serviceutil.HandleCommandLine(PeekSvc)


if __name__ == '__main__':
    main()
