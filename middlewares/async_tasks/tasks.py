#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/5 下午5:34
# @Author  : Hanley
# @File    : tasks.py.py
# @Desc    :


from __future__ import absolute_import, unicode_literals

import os
import sys

proPath = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__))))  # noqa
sys.path.append(proPath)
from .celeryapp import app


@app.task
def async_method(parameter):
    return parameter


@app.task
def crontab_method(parameter):
    return parameter
