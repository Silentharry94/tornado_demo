#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : initlog.py
# @Desc    : 日志模块
import os
import sys

from loguru import logger

BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DEFAULT_LOG_PATH = os.path.join(BASE_PATH, "log")
DEFAULT_FORMAT = "{time:YYYY-MM-DD HH:mm:ss} | {level} | {process.id} | {name} | {function} | {line} | {message}"

API_LOG_PATH = os.path.join(BASE_PATH, "log", "api")
API_HANDLERS = [
    {
        "sink": "%s/{time:YYYYMMDD}.log" % API_LOG_PATH,
        "enqueue": True,
        "backtrace": True,
        "rotation": "00:00",
        "retention": "30 days",
        "format": DEFAULT_FORMAT,
        "filter": lambda x: x["extra"]["channel"] == "api"
    }
]

CELERY_LOG_PATH = os.path.join(BASE_PATH, "log", "celery")
CELERY_HANDLERS = [
    {
        "sink": sys.stdout,
        "enqueue": True,
        "backtrace": True,
        "format": DEFAULT_FORMAT,
        "filter": lambda x: x["extra"]["channel"] == "celery"
    },
    {
        "sink": "%s/{time:YYYYMMDD}.log" % CELERY_LOG_PATH,
        "enqueue": True,
        "backtrace": True,
        "rotation": "00:00",
        "retention": "30 days",
        "format": DEFAULT_FORMAT,
        "filter": lambda x: x["extra"]["channel"] == "celery"
    }
]


class ServerLog:

    def __init__(self, channel: str, handlers: list):
        self.channel = channel
        _ = [logger.add(**h) for h in handlers]
        self.client = logger.bind(channel=channel)


logging = ServerLog("api", API_HANDLERS).client
celery_log = ServerLog("celery", CELERY_HANDLERS).client
