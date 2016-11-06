from __future__ import absolute_import

from celery import Celery

peekWorkerApp = Celery('celery',
                       broker='amqp://',
                       backend='redis://localhost',
                       # DbConnection MUST BE FIRST, so that it creates a new connection
             include=['celery.DbConnectionInit',
                      # These are in a peek app
                      # 'celery.DispQueueIndexerTask',
                      # 'celery.GridKeyQueueCompilerTask'
                      ])

# Optional configuration, see the application user guide.
peekWorkerApp.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],  # Ignore other content
    CELERY_RESULT_SERIALIZER='json',
    CELERY_ENABLE_UTC=True,
)

