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
import subprocess

import os

from peek_server.api.client.ClientGridHandler import clientGridHandler
from rapui import LoggingSetup
from rapui.util.Directory import DirSettings
from rapui.vortex.VortexForkParent import killAllChildProcs

LoggingSetup.setup()

import logging

from twisted.internet import reactor, defer

import rapui
from peek_server.core.orm.ModelSet import getOrCreateModelSet
from peek_server.core.queue_processesors import DispQueueIndexer
from peek_server.core.queue_processesors import GridKeyQueueCompiler
from peek_server.core.queue_processesors.DispQueueIndexer import dispQueueCompiler
from peek_server.core.queue_processesors.GridKeyQueueCompiler import gridKeyQueueCompiler
from rapui import addMetaTag
from rapui.site.Site import setupSite

rapui.DESCRIPTION = "Peek"
rapui.TITLE = "Peek"

addMetaTag(name="apple-mobile-web-app-capable", content="yes")
addMetaTag(name="apple-mobile-web-app-app-title", content="Peek")
addMetaTag(name="apple-mobile-web-app-status-bar-style", content="black")
addMetaTag(name="viewport", content="initial-scale=1")
addMetaTag(name="format-detection", content="telephone=no")

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# Set the parallelism of the database and reactor

from peek_server.core import orm
from peek_server.core.orm import getNovaOrmSession

reactor.suggestThreadPoolSize(10)
orm.SynSqlaConn.dbEngineArgs = {
    'pool_size': 20,  # Number of connections to keep open
    'max_overflow': 50,  # Number that the pool size can exceed when required
    'pool_timeout': 60,  # Timeout for getting conn from pool
    'pool_recycle': 600  # Reconnect?? after 10 minutes
}

defer.setDebugging(True)


def main():
    # defer.setDebugging(True)
    # sys.argv.remove(DEBUG_ARG)
    # import pydevd
    # pydevd.settrace(suspend=False)

    from peek_server.AppConfig import appConfig

    # Set paths for the Directory object
    DirSettings.defaultDirChmod = appConfig.defaultDirChmod
    DirSettings.tmpDirPath = appConfig.tmpPath

    # Set default logging level
    logging.root.setLevel(appConfig.loggingLevel)

    # Force model migration
    session = getNovaOrmSession()

    # Ensure that the model set exists
    agentName = "PowerOn Fusion"
    getOrCreateModelSet(session, agentName)
    session.close()

    clientGridHandler.start()
    dispQueueCompiler.start()
    gridKeyQueueCompiler.start()

    sitePort = 8000
    setupSite(sitePort, debug=True)
    # setupSite(8000, debug=True, protectedResource=AuthSessionWrapper())

    reactor.run()


if __name__ == '__main__':
    main()
