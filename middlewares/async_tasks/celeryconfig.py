#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/5 下午5:34
# @Author  : Hanley
# @File    : celeryconfig.py.py
# @Desc    :


from __future__ import absolute_import

from celery.schedules import crontab

REDIS_URL = 'redis://{0}:{1}'.format("127.0.0.1", 6379)
BROKER_URL = '{0}/{1}'.format(REDIS_URL, 9)
CELERY_RESULT_BACKEND = '{0}/{1}'.format(REDIS_URL, 8)

CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'Asia/Shanghai'
CELERYD_FORCE_EXECV = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']

CELERY_TASK_RESULT_EXPIRES = 60 * 60
# CELERY_EVENT_QUEUE_EXPIRES=10
CELERYD_CONCURRENCY = 2  # 设置并行的worker数
CELERYD_PREFETCH_MULTIPLIER = 1  # celery worker 每次去取任务的数量，我这里预取了4个慢慢执行,因为任务有长有短没有预取太多
# CELERYD_MAX_TASKS_PER_CHILD = 200    # 每个worker最多执行万100个任务就会被销毁，可防止内存泄露
# CELERYD_TASK_TIME_LIMIT = 60    # 单个任务的运行时间不超过此值，否则会被SIGKILL 信号杀死 
# CELERY_DISABLE_RATE_LIMITS = True   # 任务发出后，经过一段时间还未收到acknowledge , 就将任务重新交给其他worker执行

CELERY_INCLUDE = (
    'async_tasks.tasks',
)

CELERY_IMPORTS = [
    "async_tasks.tasks",
]

# 需要执行任务的配置
CELERYBEAT_SCHEDULE = {
    "remind_order": {  # 提醒发货
        "task": "async_tasks.tasks.remind",
        # "schedule": timedelta(seconds=1),   # 监控当天数据更新情况
        "schedule": crontab(minute=0, hour=8),  # 监控当天数据更新情况
        "args": ()
    },
}
