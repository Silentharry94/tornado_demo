#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/5 下午5:34
# @Author  : Hanley
# @File    : celeryapp.py.py
# @Desc    :


from __future__ import absolute_import, unicode_literals

from celery import Celery

app = Celery('async_tasks')
app.config_from_object('async_tasks.celeryconfig')
app.conf.ONCE = {
  'backend': 'celery_once.backends.Redis',
  'settings': {
    'url': "redis://127.0.0.1:6379/8",
    'default_timeout': 60 * 60 * 24
  }
}

if __name__ == '__main__':
  app.start()
