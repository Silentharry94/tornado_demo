#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:26
# @Author  : Hanley
# @File    : request_util.py
# @Desc    : 请求基础文件

import collections
import time
import traceback
from copy import deepcopy

import ujson
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler

from commons.constant import ReturnCode, Constant
from commons.initlog import logging
from utils.database_util import MongodbConnect, RedisConnect


class BaseHandler(RequestHandler):

    def __init__(self, application, request, **kwargs):
        """"""
        self.channel = Constant.PROJECT_CHANNEL
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

        if self.request.body and self.request.headers.get(
                "Content-Type", "").startswith("application/json"):
            try:
                self.json_args = ujson.loads(self.request.body)
            except BaseException:
                logging.error("can't loads param: {}".format(
                    self.request.body))
                result = ReturnData(602)
                self.write(result.value)
                self.finish()
            else:
                self.parameter = self.json_args

    def byte_to_str(self, data):
        """
        转换输入对象为utf8格式
        :param data:
        :return:
        """
        if isinstance(data, bytes):
            return data.decode('utf8')
        if isinstance(data, str):
            return data
        elif isinstance(data, collections.Mapping):
            return dict(map(self.byte_to_str, data.items()))
        elif isinstance(data, collections.Iterable):
            return type(data)(map(self.byte_to_str, data))
        else:
            return data

    def _xss(self, data):
        """
        防止xss注入
        """
        if data:
            getData = self.byte_to_str(data)
            return getData.replace(" ", "")
        else:
            return ""

    async def fetch_response(self, req):
        """
        远程rpc接口异步调用
        """
        rpc_data = ""
        try:
            response = await AsyncHTTPClient().fetch(req)
            rpc_data = ujson.loads(response.body)
        except BaseException:
            logging.error(traceback.format_exc())
        finally:
            return rpc_data


class ReturnData(object):

    def __init__(self, code=200, data=None, flag=True, **kwargs):
        self.code = code
        self.message = ReturnCode.CN_CODE[code]
        self.data = data
        self.flag = flag
        self.kwargs = kwargs

    @property
    def value(self):
        returnMap = {
            "code": self.code,
            "msg": self.message,
            "time": time.time(),
        }
        if self.data is None:
            self.data = ""
        if self.flag:
            returnMap.update({"data": self.data})
        if self.kwargs:
            returnMap.update(self.kwargs)
        return returnMap
