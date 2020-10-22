#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : initlog.py
# @Desc    :

import os
import sys

from loguru import logger

from commons.common import singleton

current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
applog_path = os.path.join(current_path, "log")
_format_str = "{time:YYYY-MM-DD HH:mm:ss} " \
              "| {level} | {name} | {function} | {line} | {message} "

config = {
    "handlers": [
        # sink: 输出位置,
        # level: 输出等级,
        # enqueue: 异步写入,
        # rotation: 拆分文件方式,
        # retention: 清理文件方式,
        # format: 文件格式化方式
        {
            "sink": sys.stdout,
            "level": "DEBUG",
            "enqueue": True,
            "backtrace": True,
            "format": _format_str
        },
        {
            "sink": "%s/{time:YYYYMMDD}.log" % applog_path,
            "level": "INFO",
            "enqueue": True,
            "backtrace": True,
            "rotation": "00:00",
            "retention": "30 days",
            "format": _format_str
        },
        {
            "sink": "%s/{time:YYYYMMDD}.log" % applog_path,
            "level": "WARNING",
            "enqueue": True,
            "backtrace": True,
            "rotation": "00:00",
            "retention": "30 days",
            "format": _format_str
        },
        {
            "sink": "%s/{time:YYYYMMDD}.log" % applog_path,
            "level": "ERROR",
            "enqueue": True,
            "backtrace": True,
            "rotation": "00:00",
            "retention": "30 days",
            "format": _format_str
        },
        {
            "sink": "%s/{time:YYYYMMDD}.log" % applog_path,
            "level": "DEBUG",
            "enqueue": True,
            "backtrace": True,
            "rotation": "00:00",
            "retention": "30 days",
            "format": _format_str
        }
    ]
}


@singleton
class MyLog(object):

    def __init__(self):
        logger.configure(**config)
        self.client = logger


logging = MyLog().client
