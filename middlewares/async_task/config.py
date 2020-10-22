#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/5 下午5:34
# @Author  : Hanley
# @File    : config.py.py
# @Desc    :

from __future__ import absolute_import

from celery import platforms
from celery.schedules import crontab
from kombu import Queue

from commons.common import Common, DealEncrypt

rbd_config = Common.get_config_value('redis')
host = rbd_config["host"]
port = rbd_config["port"]
if rbd_config.get("password", None):
    password = DealEncrypt.crypto_decrypt(rbd_config["password"])
    REDIS_URL = 'redis://:{2}@{0}:{1}'.format(host, port, password)
else:
    REDIS_URL = 'redis://{0}:{1}'.format(host, port)

mq_config = Common.get_config_value('rabbitmq')
BROKER_URL = 'pyamqp://{0}:{1}@{2}:{3}/{4}'.format(
    mq_config["user"], mq_config["password"],
    mq_config["host"], mq_config["port"],
    mq_config["vhost"])
# BROKER_URL = 'pyamqp://hanley-test:123456@localhost:5672/test'
CELERY_RESULT_BACKEND = '{0}/{1}'.format(REDIS_URL, rbd_config["db"])

platforms.C_FORCE_ROOT = True
CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERYD_FORCE_EXECV = True
CELERY_TASK_SERIALIZER = 'pickle'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['pickle', 'json']

CELERY_TASK_RESULT_EXPIRES = 60 * 60
CELERYD_CONCURRENCY = 1
CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_MAX_TASKS_PER_CHILD = 200

CELERY_INCLUDE = (
    'async_task.tasks',
)

CELERY_IMPORTS = [
    "async_task.tasks",
]

CELERY_QUEUES = (
    Queue('default'),
    Queue('log', routing_key="log",
          queue_arguments={'x-max-priority': 7},
          consumer_arguments={"x-priority": 7}),
    Queue('schedule_task', routing_key="schedule",
          queue_arguments={'x-max-priority': 2},
          consumer_arguments={"x-priority": 2})
)

# 需要执行任务的配置
CELERYBEAT_SCHEDULE = {
    "monitor": {
        "task": "async_task.tasks.monitor",
        "schedule": crontab(hour='*/1', minute=0),
        "args": ()
    }
}
