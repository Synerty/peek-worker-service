"""
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
import logging
import shutil
import sys
import tarfile
import tempfile
import urllib

import os
from os.path import expanduser
from twisted.internet import reactor, defer
from twisted.internet.defer import inlineCallbacks

from rapui.DeferUtil import printFailure, deferToThreadWrap
from rapui.util.Directory import Directory
from rapui.util.RapuiHttpFileDownloader import rapuiHttpFileDownloader

logger = logging.getLogger(__name__)


class PappUpdateManager:
    def __init__(self):
        pass

    @inlineCallbacks
    def update(self, targetVersion):
        logger.info("Updating to %s", targetVersion)

        from peek_agent.AgentConfig import AgentConfig
        agentConfig = AgentConfig()

        url = ('http://%(ip)s:%(port)s/peek.agent.sw_update.download?'
               ) % {"ip": agentConfig.peekServerHost,
                    "port": agentConfig.peekServerPort}

        args = {"name": agentConfig.agentName}
        if targetVersion:
            args["version"] = str(targetVersion)

        url += urllib.urlencode(args)

        (dir, file) = yield rapuiHttpFileDownloader(url)
        if file.size == 0:
            logger.warning("Peek server doesn't have any updates for agent %s, version %s",
                           agentConfig.agentName, targetVersion)
            return

        yield self._blockingInstallUpdate(targetVersion, dir, file)

        defer.returnValue(targetVersion)

    @deferToThreadWrap
    def _blockingInstallUpdate(self, targetVersion, dir, file):
        dir._unused = True  # Ingore unused, and we need to hold a ref or it deletes

        from peek_agent.AgentConfig import AgentConfig
        agentConfig = AgentConfig()

        if not tarfile.is_tarfile(file.realPath):
            raise Exception("Agent update download is not a tar file")

        directory = Directory()
        tarfile.open(file.realPath).extractall(directory.path)
        directory.scan()

        runAgentPyc = filter(lambda f: f.name == 'run_peek_agent.pyc', directory.files)
        if len(runAgentPyc) != 1:
            raise Exception("Uploaded archive does not contain Peek Agent software"
                            ", Expected 1 run_peek_agent.pyc, got %s" % len(runAgentPyc))
        runAgentPyc = runAgentPyc[0]

        if '/' in runAgentPyc.path:
            raise Exception("Expected run_peek_agent.pyc to be one level down, it's at %s"
                            % runAgentPyc.path)

        home = expanduser("~")
        newPath = os.path.join(home, runAgentPyc.path)

        if os.path.exists(newPath):
            oldPath = tempfile.mkdtemp(dir=home, prefix=runAgentPyc.path)
            shutil.move(newPath, oldPath)

        shutil.move(os.path.join(directory.path, runAgentPyc.path), newPath)

        self._synlinkTo(home, agentConfig.agentSymlinkName, newPath)

        agentConfig.agentVersion = targetVersion

        reactor.callLater(1.0, self.restartAgent)

    def _synlinkTo(self, home, symlinkName, newPath):
        symLink = os.path.join(home, symlinkName)
        try:
            os.remove(symLink)
        except:
            pass
        os.symlink(newPath, symLink)

    @classmethod
    def restartAgent(self):
        """Restarts the current program.
        Note: this function does not return. Any cleanup action (like
        saving data) must be done before calling this function."""
        python = sys.executable
        argv = list(sys.argv)
        argv.insert(0,"-u")
        os.execl(python, python, *argv)
