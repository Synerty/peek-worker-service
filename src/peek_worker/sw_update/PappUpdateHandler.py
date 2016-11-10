'''
Created on 09/07/2014

@author: synerty
'''
from copy import copy

from peek_agent.PeekVortexClient import sendPayloadToPeekServer
from peek_agent.sw_update.AgentSwUpdateManager import AgentSwUpdateManager
from rapui.vortex.Payload import Payload
from rapui.vortex.PayloadEndpoint import PayloadEndpoint
from twisted.internet.defer import Deferred

__author__ = 'peek'
import logging

logger = logging.getLogger(__name__)

# -------------------------------------
# Software Update Handler for data from agents

# The filter we listen on
agentSwUpdateFilt = {'key': "c.s.p.agent.sw_update.check"}  # LISTEN / SEND


class PappUpdateHandler(object):
    def __init__(self):
        self._startupDeferred = Deferred()

    def start(self):
        from peek_agent.AgentConfig import AgentConfig
        agentConfig = AgentConfig()

        if not agentConfig.agentAutoUpdate:
            logger.info("Auto updates disabled by config")
            return

        self._ep = PayloadEndpoint(agentSwUpdateFilt, self._process)

        # Whenever the vortex connects, it will check the software update version
        from peek_agent.PeekVortexClient import addReconnectPayload
        filt = copy(agentSwUpdateFilt)
        filt["name"] = agentConfig.agentName
        sendPayloadToPeekServer(Payload(filt=filt))

        return self._startupDeferred

    def _process(self, payload, vortexUuid, **kwargs):
        assert not payload.result # Means success

        from peek_agent.AgentConfig import AgentConfig
        agentConfig = AgentConfig()

        name = payload.filt["name"]
        if name != agentConfig.agentName:
            logger.debug("Recieved update for agent name %s, we're %s",
                         name, agentConfig.agentName)
            return

        version = payload.filt["version"]

        logger.info("Recieved update for agent new version is %s, we're %s",
                    version, agentConfig.agentVersion)

        if version == agentConfig.agentVersion:
            logger.info("No update required")
            if self._startupDeferred:
                self._startupDeferred.callback(True)
                self._startupDeferred = None
            return

        if self._startupDeferred:
            self._startupDeferred.errback(
                Exception("Startup stopped, Agent will update and restart"))
            self._startupDeferred = None

        AgentSwUpdateManager().update(version)


agentSwUpdateHandler = PappUpdateHandler()
