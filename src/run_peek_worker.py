#!/usr/bin/env python
"""
 * synnova.py
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by
 *  Synerty Pty Ltd
 *
"""
import celery
from celery.signals import worker_shutdown

from rapui import LoggingSetup

LoggingSetup.setup()

from twisted.internet import reactor

from rapui import RapuiConfig
from rapui.DeferUtil import printFailure
from rapui.util.Directory import DirSettings

RapuiConfig.enabledJsRequire = False

import logging
from threading import Thread

# EXAMPLE LOGGING CONFIG
# Hide messages from vortex
# logging.getLogger('rapui.vortex.VortexClient').setLevel(logging.INFO)

# logging.getLogger('peek_worker_pof.realtime.RealtimePollerEcomProtocol'
#                   ).setLevel(logging.INFO)

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Set the parallelism of the database and reactor
reactor.suggestThreadPoolSize(10)

# Enable this for PYPY
from psycopg2cffi import compat

compat.register()


# Allow the twisted reactor thread to restart the worker process


def platformSetup():
    from peek_platform import PeekPlatformConfig
    PeekPlatformConfig.componentName = "peek_worker"

    # Tell the platform classes about our instance of the pappSwInstallManager
    from peek_worker.sw_install.PappSwInstallManager import pappSwInstallManager
    PeekPlatformConfig.pappSwInstallManager = pappSwInstallManager

    # Tell the platform classes about our instance of the PeekSwInstallManager
    from peek_worker.sw_install.PeekSwInstallManager import peekSwInstallManager
    PeekPlatformConfig.peekSwInstallManager = peekSwInstallManager

    # The config depends on the componentName, order is important
    from peek_worker.PeekWorkerConfig import peekWorkerConfig
    PeekPlatformConfig.config = peekWorkerConfig

    # Initialise the rapui Directory object
    DirSettings.defaultDirChmod = peekWorkerConfig.DEFAULT_DIR_CHMOD
    DirSettings.tmpDirPath = peekWorkerConfig.tmpPath

@celery.signals.after_setup_logger.connect
def configureLogging(*args, **kwargs):

    # Set default logging level
    from peek_worker.PeekWorkerConfig import peekWorkerConfig
    logging.root.setLevel(peekWorkerConfig.loggingLevel)

def twistedMain():
    # defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    # Load server restart handler handler
    from peek_platform.PeekServerRestartWatchHandler import PeekServerRestartWatchHandler
    PeekServerRestartWatchHandler.__unused = False

    # First, setup the Vortex Worker
    from peek_platform.PeekVortexClient import peekVortexClient
    d = peekVortexClient.connect()
    d.addErrback(printFailure)

    # Start Update Handler,
    from peek_platform.sw_version.PeekSwVersionPollHandler import peekSwVersionPollHandler
    # Add both, The peek client might fail to connect, and if it does, the payload
    # sent from the peekSwUpdater will be queued and sent when it does connect.
    d.addBoth(lambda _: peekSwVersionPollHandler.start())

    # Load all Papps
    logger.info("Loading all Peek Apps")
    from peek_worker.papp.PappWorkerLoader import pappWorkerLoader
    d.addBoth(lambda _: pappWorkerLoader.loadAllPapps())

    # Log that the reactor has started
    from peek_worker.PeekWorkerConfig import peekWorkerConfig
    d.addCallback(lambda _:
                  logger.info('Peek Worker is running, version=%s',
                              peekWorkerConfig.platformVersion))

    d.addErrback(printFailure)

    # Run the reactor in a thread
    reactor.callLater(0, logger.info, "Reactor started")

    reactor.run(installSignalHandlers=False)


def celeryMain():
    # Load all Papps
    logger.info("Starting Celery")
    from peek_worker import PeekWorkerApp
    PeekWorkerApp.start()


@worker_shutdown.connect
def twistedShutdown(sender, signal):
    logger.info("Reactor stopping, Celery pool is shutting down.")
    reactor.callFromThread(reactor.stop)


if __name__ == '__main__':
    platformSetup()

    # Initialise and run all the twisted stuff in another thread.
    Thread(target=twistedMain).start()

    celeryMain()
