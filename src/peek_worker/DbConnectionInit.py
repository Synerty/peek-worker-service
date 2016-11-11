import logging

from celery.signals import worker_process_init, worker_process_shutdown

from peek_worker import DbConnection

logger = logging.getLogger(__name__)

# from psycopg2cffi import compat
# compat.register()


@worker_process_init.connect
def init_worker(**kwargs):
    print "db init INIT"

@worker_process_init.connect
def init_worker(**kwargs):
    reload(DbConnection)
    logger.info('Reloaded database connection for worker.')



@worker_process_shutdown.connect
def shutdown_worker(**kwargs):
    if DbConnection._dbEngine:
        logger.info('Closing database connectionn for worker.')
        DbConnection._dbEngine.dispose()