#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/5 下午5:34
# @Author  : Hanley
# @File    : celeryconfig.py.py
# @Desc    :

from __future__ import absolute_import

import os

from celery.schedules import crontab
from kombu import Queue

project_root_path = os.path.dirname(os.path.abspath(__file__))
database = os.path.join(project_root_path, 'celery_beat_database')

# 消息代理队列
BROKER_URL = 'amqp://guest:guest@127.0.0.1:5672//'

# 任务结果存储
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/3'

# 引入模块
CELERY_IMPORTS = (
    'async_tasks.tasks'
)

# 时区
CELERY_TIMEZONE = 'Asia/Shanghai'

# 启动时区设置
CELERY_ENABLE_UTC = True

# 任务序列化使用方案
CELERY_TASK_SERIALIZER = 'msgpack'

# 任务结果序列化方案
CELERY_RESULT_SERIALIZER = 'json'

# 任务限制执行频率(指定任务)
# CELERY_ANNOTATIONS = {'async_celery.tasks.add':{'rate_limit':'10/s'}}

# 任务限制执行频率(所有任务)
# CELERY_ANNOTATIONS = {'*':{'rate_limit':'10/s'}}

# def my_on_failure(exc, task_id, args, kwargs, einfo):
#     print('task failed')
# 任务执行失败后处理
# CELERY_ANNOTATIONS = {'*':{'on_failure':my_on_failure}}

# 并发worker数量，机器核心数量
CELERYD_CONCURRENCY = 4

# 每次去队列取任务的数量
CELERYD_PREFETCH_MULTIPLIER = 4

# 每个worker最多执行200个任务就会被销毁，可防止内存泄露
CELERYD_MAX_TASKS_PER_CHILD = 200

# 任务结果过期时间
CELERY_TASK_RESULT_EXPIRES = 60 * 60 * 24

# 单个任务执行时间限制
CELERY_TASK_TIME_LIMIT = 60

# 关闭限速
CELERY_DISABLE_RATE_LIMITS = True

# 任务发送完成是否需要确认
CELERY_ACKS_LATE = False

# 压缩方案(zlib, bzip2)
CELERY_MESSAGE_COMPRESSION = 'zlib'

# 指定接受的内容类型
CELERY_ACCEPT_CONTENT = ['json', 'msgpack']

# 定时任务存放数据文件
CELERYBEAT_SCHEDULE_FILENAME = database

# 默认队列
CELERY_DEFAULT_QUEUE = 'default'

# 设置队列绑定routing_key
CELERY_QUEUES = [
    Queue(name='queue_one', routing_key='queue_one', exchange='one')
]

# 任务加入到队列，并设置routing_key
CELERY_ROUTES = {
    'async_tasks.tasks.async_method': {
        'queue': 'queue_one',
        'routing_key': 'queue_one'
    }
}

# 定时任务
CELERYBEAT_SCHEDULE = {
    "crontab_001": {
        "task": "async_tasks.tasks.crontab_method",
        "schedule": crontab(minute='*/1'),
    }
}
