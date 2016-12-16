#!/usr/bin/env python
"""

  Copyright Synerty Pty Ltd 2013

  This software is proprietary, you are not free to copy
  or redistribute this code in any format.

  All rights to this software are reserved by
  Synerty Pty Ltd

"""

import logging
import threading
from threading import Thread

import celery
from celery.signals import worker_shutdown
from pytmpdir.Directory import DirSettings
from twisted.internet import reactor
from txhttputil.site.FileUploadRequest import FileUploadRequest
from txhttputil.util.DeferUtil import printFailure
from txhttputil.util.LoggingUtil import setupLogging

setupLogging()

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Set the parallelism of the database and reactor
reactor.suggestThreadPoolSize(10)


# Allow the twisted reactor thread to restart the worker process


@celery.signals.after_setup_logger.connect
def configureLogging(*args, **kwargs):
    # Set default logging level
    from peek_worker.PeekWorkerConfig import peekWorkerConfig
    logging.root.setLevel(peekWorkerConfig.loggingLevel)

    if peekWorkerConfig.loggingLevel != "DEBUG":
        for name in ("celery.worker.strategy", "celery.app.trace", "celery.worker.job"):
            logging.getLogger(name).setLevel(logging.WARNING)


def setupPlatform():
    from peek_platform import PeekPlatformConfig
    PeekPlatformConfig.componentName = "peek_worker"

    # Tell the platform classes about our instance of the pluginSwInstallManager
    from peek_worker.sw_install.PluginSwInstallManager import pluginSwInstallManager
    PeekPlatformConfig.pluginSwInstallManager = pluginSwInstallManager

    # Tell the platform classes about our instance of the PeekSwInstallManager
    from peek_worker.sw_install.PeekSwInstallManager import peekSwInstallManager
    PeekPlatformConfig.peekSwInstallManager = peekSwInstallManager

    # Tell the platform classes about our instance of the PeekLoaderBase
    from peek_worker.plugin.WorkerPluginLoader import workerPluginLoader
    PeekPlatformConfig.pluginLoader = workerPluginLoader

    # The config depends on the componentName, order is important
    from peek_worker.PeekWorkerConfig import peekWorkerConfig
    PeekPlatformConfig.config = peekWorkerConfig

    # Set default logging level
    logging.root.setLevel(peekWorkerConfig.loggingLevel)

    # Initialise the txhttputil Directory object
    DirSettings.defaultDirChmod = peekWorkerConfig.DEFAULT_DIR_CHMOD
    DirSettings.tmpDirPath = peekWorkerConfig.tmpPath
    FileUploadRequest.tmpFilePath = peekWorkerConfig.tmpPath


def twistedMain():
    # defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    # Load server_fe restart handler handler
    from peek_platform import PeekServerRestartWatchHandler
    PeekServerRestartWatchHandler.__unused = False

    # First, setup the Vortex Worker
    from peek_platform.PeekVortexClient import peekVortexClient
    d = peekVortexClient.connect()
    d.addErrback(printFailure)

    # Start Update Handler,
    from peek_platform.sw_version.PeekSwVersionPollHandler import peekSwVersionPollHandler
    # Add both, The peek client_fe might fail to connect, and if it does, the payload
    # sent from the peekSwUpdater will be queued and sent when it does connect.
    d.addBoth(lambda _: peekSwVersionPollHandler.start())

    # Load all Plugins
    logger.info("Loading all Peek Apps")
    from peek_worker.plugin.WorkerPluginLoader import workerPluginLoader
    d.addBoth(lambda _: workerPluginLoader.loadAllPlugins())

    # Log Exception, convert the errback to callback
    d.addErrback(lambda f: logger.exception(f.value))

    # Log that the reactor has started
    from peek_worker.PeekWorkerConfig import peekWorkerConfig
    d.addCallback(lambda _:
                  logger.info('Peek Worker is running, version=%s',
                              peekWorkerConfig.platformVersion))

    # Unlock the mutex
    d.addCallback(lambda _: twistedPluginsLoadedMutex.release())

    d.addErrback(printFailure)

    # Run the reactor in a thread
    reactor.callLater(0, logger.info, "Reactor started")

    reactor.run(installSignalHandlers=False)


def celeryMain():
    # Load all Plugins
    logger.info("Starting Celery")
    from peek_platform import CeleryApp
    CeleryApp.start()


# Create the startup mutex, twisted has to load the plugins before celery starts.
twistedPluginsLoadedMutex = threading.Lock()
assert twistedPluginsLoadedMutex.acquire()


def setPeekWorkerRestarting():
    global peekWorkerRestarting
    peekWorkerRestarting = True


def main():
    setupPlatform()

    # Initialise and run all the twisted stuff in another thread.
    twistedMainLoopThread = Thread(target=twistedMain)
    twistedMainLoopThread.start()

    # Block until twisted has released it's lock
    twistedPluginsLoadedMutex.acquire()

    # Start the celery blocking main thread
    celeryMain()
    logger.info("Celery has shutdown")

    from peek_worker.sw_install.PeekSwInstallManager import peekSwInstallManager

    if peekSwInstallManager.restartTriggered:

        logger.info("Restarting Peek Worker")
        peekSwInstallManager.realyRestartProcess()

    else:
        # Tell twisted to stop
        logger.info("Shutting down twisted reactor.")
        reactor.callFromThread(reactor.stop)

    # Wait for twisted to stop
    twistedMainLoopThread.join()

    logger.info("Reactor shutdown complete.")


if __name__ == '__main__':
    main()