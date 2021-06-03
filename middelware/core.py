#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/26 11:23 上午
# @Author  : Hanley
# @File    : core.py
# @Desc    :

from copy import deepcopy

import tornado.web
import ujson
from aioredis import Redis
from motor.core import AgnosticClient
from tornado.web import RequestHandler

from commons.common import AsyncClientSession, datetime_now
from commons.common import Common, GenerateRandom
from commons.constant import Constant
from commons.initlog import logging
from commons.status_code import *
from scripts.init_tables import complete_table
from utils.async_db import AsyncManager
from utils.kafka_producer import KafkaEntryPoint


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

    @property
    def redis(self) -> Redis:
        return self.settings["controller"].redis

    @property
    def mongo(self) -> AgnosticClient:
        return self.settings["controller"].mongo

    @property
    def ext_mongo(self) -> AgnosticClient:
        return self.settings["controller"].ext_mongo

    @property
    def mysql(self) -> AsyncManager:
        return self.settings["controller"].mysql

    @property
    def epc_mysql(self) -> AsyncManager:
        return self.settings["controller"].epc_mysql

    @property
    def async_client(self) -> AsyncClientSession:
        return self.settings["controller"].async_client

    @property
    def kafka_producer(self) -> KafkaEntryPoint:
        return self.settings["controller"].kafka_producer

    def common_param(self):
        self.parameter = dict.fromkeys(Constant.COMMON_REQUEST_PARAM, "")
        headers_log = self.request.headers._dict
        real_ip = headers_log["X-Real-IP"] if headers_log.get("X-Real-IP") \
            else self.request.remote_ip
        domain = headers_log.get("Host")
        pre_fix = domain.split(".")[0]
        token_key = Constant.COOKIE_TOKEN.format(pre_fix)
        uid_key = Constant.COOKIE_UID.format(pre_fix)
        self.parameter["request_time"] = datetime_now()
        self.parameter["client_ip"] = real_ip
        self.parameter["request_id"] = GenerateRandom.generate_uuid()
        self.parameter["domain"] = domain
        self.parameter["uid"] = self.get_cookie(uid_key, "")
        self.parameter["access_token"] = self.get_cookie(token_key, "")

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
            except Exception as e:
                logging.error(e)
                result = ReturnData(CODE_101, request_id=self.parameter["request_id"])
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
        self.message = msg if msg else EN_CODE[code]
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
