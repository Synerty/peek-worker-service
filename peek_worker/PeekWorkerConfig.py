'''
 *
 *  Copyright Synerty Pty Ltd 2013
 *
 *  This software is proprietary, you are not free to copy
 *  or redistribute this code in any format.
 *
 *  All rights to this software are reserved by 
 *  Synerty Pty Ltd
 *
 * Website : http://www.synerty.com
 * Support : support@synerty.com
 *
'''
import logging

from peek_platform.file_config.PeekFileConfigABC import PeekFileConfigABC
from peek_platform.file_config.PeekFileConfigPeekServerClientMixin import \
    PeekFileConfigPeekServerClientMixin
from peek_platform.file_config.PeekFileConfigPlatformABC import \
    PeekFileConfigPlatformABC
from peek_platform.file_config.PeekFileConfigSqlAlchemyMixin import \
    PeekFileConfigSqlAlchemyMixin

logger = logging.getLogger(__name__)


class PeekWorkerConfig(PeekFileConfigABC,
                       PeekFileConfigPeekServerClientMixin,
                       PeekFileConfigPlatformABC,
                       PeekFileConfigSqlAlchemyMixin):
    """
    This class creates a basic worker configuration
    """

    @property
    def platformVersion(self):
        import peek_worker
        return peek_worker.__version__


peekWorkerConfig = PeekWorkerConfig()
