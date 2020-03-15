#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : initlog.py
# @Desc    : 日志模块

import os
import sys

from loguru import logger

current_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

infolog_path = os.path.join(current_path, "logs")
warning_path = os.path.join(infolog_path, "warning")
errorlog_path = os.path.join(infolog_path, "errors")
debuylog_path = os.path.join(infolog_path, "debugs")

_format_str = "{time:YYYY-MM-DD at HH:mm:ss, SSS} " \
              "| {level} | {name} | {function} | {line} | {message}"

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
            "sink": "%s/warning_{time:YYYYMMDD}.log" % warning_path,
            "level": "WARNING",
            "enqueue": True,
            "backtrace": True,
            "rotation": "00:00",
            "retention": "30 days",
            "format": _format_str
        },
        {
            "sink": "%s/info_{time:YYYYMMDD}.log" % infolog_path,
            "level": "INFO",
            "enqueue": True,
            "backtrace": True,
            "rotation": "00:00",
            "retention": "30 days",
            "format": _format_str
        },
        {
            "sink": "%s/error_{time:YYYYMMDD}.log" % errorlog_path,
            "level": "ERROR",
            "enqueue": True,
            "backtrace": True,
            "rotation": "00:00",
            "retention": "30 days",
            "format": _format_str
        },
        {
            "sink": "%s/debug_{time:YYYYMMDD}.log" % debuylog_path,
            "level": "DEBUG",
            "enqueue": True,
            "backtrace": True,
            "rotation": "00:00",
            "retention": "30 days",
            "format": _format_str
        }
    ]
}


class MyLog(object):
    mylog = None

    def __new__(cls, *args, **kwargs):
        if cls.mylog is None:
            logger.configure(**config)
            cls.mylog = logger
        return cls.mylog


logging = MyLog()
