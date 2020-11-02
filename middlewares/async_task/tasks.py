#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/5 下午5:34
# @Author  : Hanley
# @File    : tasks.py.py
# @Desc    :


from __future__ import absolute_import, unicode_literals
from celery import Task

import os
import sys

from commons.initlog import logging
from utils.database_util import MongodbConnect, RedisConnect, RetryConnectMysql
proPath = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__))))  # noqa
sys.path.append(proPath)
from .app import app



class MyTask(Task):

    def on_success(self, retval, task_id, args, kwargs):
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logging.debug('task fail, reason: {0}, task_id - {1}, '
                      'args - {2}, kwargs - {3}, einfo - {4}'.format(
            exc, task_id, args, kwargs, einfo))
        return super(MyTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    @property
    def mongo(self):
        return MongodbConnect().client

    @property
    def redis(self):
        return RedisConnect().client

    @property
    def mysql(self):
        return RetryConnectMysql().connect_mysql()


@app.task(base=MyTask, bind=True, queue="schedule_task")
def monitor(self, parameter):
    return parameter

