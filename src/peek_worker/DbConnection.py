import logging

from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker

logger = logging.getLogger(__name__)

_dbEngine = None
_Session = None


def getEngine():
    global _dbEngine
    if not _dbEngine:
        from peek_server.AppConfig import appConfig
        _dbEngine = create_engine(
            appConfig.dbConnectString,
            echo=False,
            pool_size=1,  # Number of connections to keep open
            max_overflow=50,  # Number that the pool size can exceed when required
            pool_timeout=60,  # Timeout for getting conn from pool
            pool_recycle=600  # Reconnect?? after 10 minutes
        )

    return _dbEngine


def getSession():
    global _Session
    if not _Session:
        _Session = sessionmaker(bind=getEngine())
    return _Session()
