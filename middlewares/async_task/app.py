#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/5 下午5:34
# @Author  : Hanley
# @File    : app.py.py
# @Desc    :


from __future__ import absolute_import, unicode_literals

from celery import Celery

app = Celery('async_task')

app.config_from_object('async_task.config')

if __name__ == '__main__':
    app.start()
