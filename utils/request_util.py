#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:26
# @Author  : Hanley
# @File    : request_util.py
# @Desc    : 请求基础文件

import time
import traceback
from copy import deepcopy

import ujson
import xmltodict
from tornado.httpclient import AsyncHTTPClient
from tornado.web import RequestHandler

from commons.common import Constant, Common, GenerateRandom
from commons.constant import ReturnCode
from commons.initlog import logging
from commons.status_code import *
from models.base import ChannelConfig
from utils.database_util import MongodbConnect, RedisConnect


def cost_time(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        return_data = await func(*args, **kwargs)
        end = time.time()
        used = end - start
        url = args[0].url
        logging.debug(f"===url: {url} cost time: {used}===")
        return return_data

    return wrapper


@cost_time
async def fetch_response(req):
    rpc_data = {"code": CODE_0, "msg": "外部接口调用异常", "time": time.time()}
    try:
        response = await AsyncHTTPClient().fetch(req)
        rpc_data = ujson.loads(response.body)
    except BaseException:
        if req.method == "GET":
            logging.error("route: {} return error".format(req.url))
        else:
            param = ujson.loads(req.body)
            logging.error("route: {}, param: {} return error".format(req.url, param))
        logging.error(traceback.format_exc())
    finally:
        return rpc_data


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
        super().prepare()
        self.simple_param()
        self.make_params()

    def make_params(self):
        self.get_domain()
        self.get_channel()
        self.init_web_param()

    def init_web_param(self):
        domain = self.parameter["domain"]
        preFix = domain.split(".")[0]
        channelCookieKey = Constant.COOKIE_CHANNEL.format(preFix)
        deviceCookieKey = Constant.COOKIE_DEVICE.format(preFix)
        uidCookieKey = Constant.COOKIE_UID.format(preFix)
        uid = self.inner_check("uid", uidCookieKey)
        device = self.inner_check("device", deviceCookieKey)
        channel = self.inner_check("channel", channelCookieKey)
        self.parameter["uid"] = uid
        self.parameter["device"] = device
        self.parameter["channel"] = channel

    def get_domain(self):
        hostDomain = self.parameter.get("domain") if self.parameter.get("domain") \
            else self.request.headers._dict.get("Host")
        real_ip = self.request.headers.get("X-Real-IP")
        real_ip = real_ip if real_ip else self.request.remote_ip
        self.parameter["real_ip"] = real_ip
        self.parameter["domain"] = hostDomain
        self.parameter["request_id"] = GenerateRandom.generate_uuid()

    def inner_check(self, key, cookieKey):
        if self.parameter.get(key):
            value = self.parameter.get(key)
        else:
            if self.get_secure_cookie(cookieKey):
                value = self.get_secure_cookie(cookieKey).decode()
            else:
                value = ""
        return value

    def xml2dict(self, xml_data):
        """
        xml转dict
        xml_data: xml字符串
        return: dict字符串
        """
        data = xmltodict.parse(xml_data, process_namespaces=True)
        return dict(list(data.values())[0])

    def simple_param(self):
        headers_log = self.request.headers._dict
        headers_log["path"] = self.request.path
        logging.debug("request headers: {}".format(headers_log))
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
                result = ReturnData(CODE_0)
                self.write(result.value)
                self.finish()
            else:
                self.parameter.update(self.json_args)
        elif self.request.body and "text/xml" in self.request.headers.get(
                "Content-Type", ""):
            self.parameter = self.xml2dict(self.request.body.decode())

    def get_channel(self):
        domain = self.parameter["domain"]
        _config = ChannelConfig.get_or_none(domain=domain)
        if not _config:
            create_dict = {
                "domain": domain,
                "channel": "external",
                "description": "外部渠道"
            }
            ChannelConfig.get_or_create(**create_dict)
            self.parameter["channel"] = "external"
        else:
            self.parameter["channel"] = _config.channel


class ReturnData(object):

    def __init__(self, code=1, data=None, flag=True, msg=None, decimal=False, **kwargs):
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
