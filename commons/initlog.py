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
    __conn = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(ServerLog, cls).__new__(cls)
        return cls._instance

    def __init__(self, channel: str, handlers: list):
        if not self.__conn.get(channel):
            self.channel = channel
            _ = [logger.add(**h) for h in handlers]
            client = logger.bind(channel=channel)
            self.__conn.setdefault(channel, client)
        self.client = self.__conn[channel]


logging = ServerLog("api", API_HANDLERS).client
celery_log = ServerLog("celery", CELERY_HANDLERS).client
