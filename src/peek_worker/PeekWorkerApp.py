from __future__ import absolute_import

import signal
import os

from celery import Celery
from twisted.internet import reactor

from peek_worker.papp.PappWorkerLoader import pappWorkerLoader

peekWorkerApp = Celery('celery')


def configureCeleryApp(app, pappIncludes=[]):
    # Optional configuration, see the application user guide.
    app.conf.update(
        BROKER_URL='amqp://',
        CELERY_RESULT_BACKEND='redis://localhost',

        CELERY_TASK_RESULT_EXPIRES=3600,
        CELERY_TASK_SERIALIZER='json',
        CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
        CELERY_RESULT_SERIALIZER='json',
        CELERY_ENABLE_UTC=True,
    )


def start(*args):
    configureCeleryApp(peekWorkerApp)

    pappIncludes = pappWorkerLoader.celeryAppIncludes

    peekWorkerApp.conf.update(
        # DbConnection MUST BE FIRST, so that it creates a new connection
        CELERY_INCLUDE=['peek_worker.DbConnectionInit'] + pappIncludes,
    )

    peekWorkerApp.worker_main()

