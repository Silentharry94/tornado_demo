#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:26
# @Author  : Hanley
# @File    : request_util.py
# @Desc    : 请求基础文件

import time
from copy import deepcopy

import ujson
from tornado.web import RequestHandler

from commons.common import Common
from commons.constant import ReturnCode
from commons.initlog import logging
from commons.status_code import *
from utils.database_util import MongodbConnect, RedisConnect


class BaseHandler(RequestHandler):

    def __init__(self, application, request, **kwargs):
        super(BaseHandler, self).__init__(application, request, **kwargs)

    @property
    def _redis(self):
        return RedisConnect().client

    @property
    def _mongo(self):
        return MongodbConnect().client

    def prepare(self):
        headers_log = self.request.headers._dict
        headers_log["path"] = self.request.path
        logging.debug("request headers: {}".format(headers_log))
        self.make_params()
        super().prepare()

    def make_params(self):
        self.parameter = {}
        query = deepcopy(self.request.arguments)
        for key in query:
            if isinstance(query[key], list):
                query[key] = query[key][0]
            if isinstance(query[key], bytes):
                query[key] = query[key].decode()
            self.parameter[key] = query[key]

        if self.request.body:
            if "application/json" in self.request.headers.get("Content-Type", ""):
                try:
                    self.json_args = ujson.loads(self.request.body)
                except BaseException:
                    logging.error("can't loads param: {}".format(
                        self.request.body))
                    result = ReturnData(CODE_0)
                    self.write(result.value)
                    self.finish()
                else:
                    self.parameter.update(self.json_args)


class ReturnData(object):

    def __init__(self, code=200, data=None, flag=True, msg=None, decimal=False, **kwargs):
        self.code = code
        self.message = msg if msg else ReturnCode.CN_CODE[code]
        self.data = Common.format_decimal(data) if decimal else data
        self.flag = flag
        self.kwargs = kwargs

    @property
    def value(self):
        returnMap = {
            "code": self.code,
            "msg": self.message,
            "time": time.time(),
        }
        if self.flag:
            returnMap.update({"data": self.data})
        if self.kwargs:
            returnMap.update(self.kwargs)
        return returnMap
