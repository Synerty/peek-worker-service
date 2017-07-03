

from celery import Celery

from peek_platform import PeekPlatformConfig
from peek_platform.ConfigCeleryApp import configureCeleryApp

celeryApp = Celery('celery')


def start():
    configureCeleryApp(celeryApp)

    pluginIncludes = PeekPlatformConfig.pluginLoader.celeryAppIncludes

    celeryApp.conf.update(
        # DbConnection MUST BE FIRST, so that it creates a new connection
        CELERY_INCLUDE=['peek_plugin_base.worker.CeleryDbConnInit'] + pluginIncludes,
    )

    # Create and set this attribute so that the CeleryDbConn can use it
    # Worker is passed as sender to @worker_init.connect
    celeryApp.peekDbConnectString = PeekPlatformConfig.config.dbConnectString

    celeryApp.worker_main()
