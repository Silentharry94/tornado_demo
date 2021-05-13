from __future__ import absolute_import

import os

from celery import platforms

from commons.common import Common

rbd_config = Common.yaml_config('redis')
host = rbd_config["host"]
port = rbd_config["port"]
if rbd_config.get("password"):
    password = rbd_config["password"]
    REDIS_URL = 'redis://:{2}@{0}:{1}'.format(host, port, password)
else:
    REDIS_URL = 'redis://{0}:{1}'.format(host, port)

mq_config = Common.yaml_config('rabbitmq')
BROKER_URL = 'pyamqp://{0}:{1}@{2}:{3}/{4}'.format(
    mq_config["user"], mq_config["password"],
    mq_config["host"], mq_config["port"],
    mq_config["vhost"])
CELERY_RESULT_BACKEND = '{0}/{1}'.format(REDIS_URL, rbd_config["db"])

platforms.C_FORCE_ROOT = True
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERYD_FORCE_EXECV = True
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']

CELERY_TASK_RESULT_EXPIRES = 60 * 60
CELERY_ACKS_LATE = True
CELERYD_CONCURRENCY = os.cpu_count()  # 设置并行的worker数
CELERYD_PREFETCH_MULTIPLIER = os.cpu_count()  # celery worker 每次去取任务的数量
CELERYD_MAX_TASKS_PER_CHILD = 200  # 每个worker最多执行完100个任务就会被销毁，可防止内存泄露

CELERY_INCLUDE = (
    'async_tasks.tasks',
)

CELERY_IMPORTS = [
    "async_tasks.tasks",
]

CELERY_QUEUES = ()

# 需要执行任务的配置
CELERYBEAT_SCHEDULE = {}
