import platform

try:
    import win32serviceutil
    import win32service
    import win32event
    import servicemanager
    # import socket
except ImportError as e:
    if platform.system() is "Windows":
        raise

from twisted.internet import reactor

from peek_worker import run_peek_worker


class PeekSvc(win32serviceutil.ServiceFramework):
    _svc_name_ = "peek_worker"
    _svc_display_name_ = "Peek Worker"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        # socket.setdefaulttimeout(120)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        reactor.callLater(0, reactor.stop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        run_peek_worker.main()


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(PeekSvc)
