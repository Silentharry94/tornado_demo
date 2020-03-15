#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/5 下午5:34
# @Author  : Hanley
# @File    : tasks.py.py
# @Desc    :


from __future__ import absolute_import, unicode_literals

from celery_once import QueueOnce

from commons.initlog import logging
from .celeryapp import app


class MyTask(QueueOnce):
    def on_success(self, retval, task_id, args, kwargs):
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logging.debug('task fail, reason: {0}, task_id - {1}, '
                      'args - {2}, kwargs - {3}, einfo - {4}'.format(
            exc, task_id, args, kwargs, einfo))
        return super(MyTask, self).on_failure(exc, task_id, args, kwargs, einfo)


@app.task(base=MyTask, once={'graceful': True})
def async_method(parameter):
    return parameter
