#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/26 11:23 上午
# @Author  : Hanley
# @File    : core.py
# @Desc    :

from copy import deepcopy

import tornado.web
import ujson
from playhouse.pool import PooledMySQLDatabase
from pymongo import MongoClient
from redis.client import Redis
from tornado.web import RequestHandler

from commons.common import AsyncClientSession, perf_time
from commons.common import Common, GenerateRandom
from commons.constant import Constant
from commons.initlog import logging
from commons.status_code import *
from scripts.init_tables import complete_table


def log_request(handler):
    template = ' {code} {summary} '
    data = {
        "code": handler.get_status(),
        "summary": handler._request_summary(),
    }
    logging.info(template.format(**data))


class BaseApp(tornado.web.Application):

    def __init__(self, handlers, settings):
        self.init_database()
        super().__init__(handlers, **settings)

    def init_database(self):
        complete_table()


class BaseHandler(RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)
        self.parameter = {}
        self._inner = {}

    @property
    def redis(self) -> Redis:
        return self.settings["redis"]

    @property
    def mongo(self) -> MongoClient:
        return self.settings["mongo"]

    @property
    def mysql(self) -> PooledMySQLDatabase:
        return self.settings["mysql"]

    @property
    def async_client(self) -> AsyncClientSession:
        return self.settings["async_client"]

    def common_param(self):
        self._inner = dict.fromkeys(Constant.COMMON_REQUEST_PARAM, "")
        headers_log = self.request.headers._dict
        _host = headers_log.get("Host")
        real_ip = headers_log.get("X-Real-IP") if headers_log.get("X-Real-IP") else self.request.remote_ip
        self._inner["start_time"] = perf_time()
        self._inner["client_id"] = real_ip
        self._inner["request_id"] = GenerateRandom.generate_uuid()

    def request_param(self):
        query = deepcopy(self.request.arguments)
        for key in query:
            if isinstance(query[key], list):
                query[key] = query[key][0]
            if isinstance(query[key], bytes):
                query[key] = query[key].decode()
            self.parameter[key] = query[key]
        if self.request.body and self.request.headers.get(
                "Content-Type", "").startswith("application/json"):
            try:
                self.json_args = ujson.loads(self.request.body)
            except BaseException:
                logging.error("can't loads param: {}".format(
                    self.request.body))
                result = ReturnData(CODE_600, request_id=self._inner["request_id"])
                self.write(result.value)
                self.finish()
            else:
                self.parameter.update(self.json_args)

    def prepare(self):
        self.common_param()
        self.request_param()


class ReturnData:
    __slots__ = (
        "code",
        "message",
        "data",
        "kwargs",
        "trace",
        "request_id"
    )

    def __init__(self, code=1, data=None, msg=None,
                 decimal=False, trace="", request_id="", **kwargs):
        self.code = code
        self.message = msg if msg else CN_CODE[code]
        self.data = Common.format_decimal(data) if decimal else data
        self.kwargs = kwargs
        self.trace = trace
        self.request_id = request_id

    @property
    def value(self):
        returnMap = {
            "code": self.code,
            "msg": self.message,
            "data": self.data,
            "trace": self.trace,
            "request_id": self.request_id
        }
        if self.kwargs:
            returnMap.update(self.kwargs)
        return returnMap
