from celery import Celery
import platform
import logging

from peek_platform import PeekPlatformConfig
from peek_platform.ConfigCeleryApp import configureCeleryApp
from peek_platform.file_config.PeekFileConfigWorkerMixin import (
    PeekFileConfigWorkerMixin,
)

logger = logging.getLogger(__name__)

celeryApp = Celery("celery")


def start(workerConfig: PeekFileConfigWorkerMixin):
    configureCeleryApp(celeryApp, workerConfig)

    pluginIncludes = PeekPlatformConfig.pluginLoader.celeryAppIncludes

    celeryApp.conf.update(
        # DbConnection MUST BE FIRST, so that it creates a new connection
        include=[
            "peek_platform.ConfigCeleryApp",
            # Load the vortex serialisation
            "peek_plugin_base.worker.CeleryDbConnInit",
        ]
        + pluginIncludes,
    )

    # Create and set this attribute so that the CeleryDbConn can use it
    # Worker is passed as sender to @worker_init.connect
    celeryApp.peekDbConnectString = PeekPlatformConfig.config.dbConnectString
    celeryApp.peekDbEngineArgs = PeekPlatformConfig.config.dbEngineArgs

    # prefork not working with skia library from
    #  peek-plugin-diagram-pdf-exporter
    #
    #  wait for celery to support spawn on macOS, which fixes from root cause
    #  https://github.com/celery/celery/issues/6036
    if platform.system() == "Darwin" and any(
        [
            p.startswith("peek_plugin_diagram_pdf_exporter")
            for p in pluginIncludes
        ]
    ):
        logger.error("Enabling celery worker solo mode due to skia library"
            " used by peek_plugin_diagram_pdf_exporter on macos")
        # workaround with solo
        #  runs tasks in the main process, without any worker processes.
        # celeryApp.worker_main()
        celeryApp.worker_main(["worker", "--pool", "solo"])
    else:
        # use default worker pool with type prefork
        celeryApp.worker_main()
