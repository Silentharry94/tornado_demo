#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : wrapper.py
# @Desc    : 装饰器文件

import traceback
from functools import wraps

from jsonschema import Draft4Validator, ValidationError

from commons.common import datetime_now, str_now, Common
from commons.constant import RedisKey, Constant
from commons.initlog import logging
from commons.status_code import *
from middelware.core import ReturnData


def parameter_valid(schema, parameter):
    try:
        Draft4Validator(schema=schema).validate(parameter)
        return True
    except ValidationError as e:
        logging.warning("{}: {}".format(CODE_101, e.message))
        return False


async def login_valid(self):
    access_token = self.parameter["access_token"]
    domain = self.parameter["domain"]
    uid = self.parameter["uid"]
    login_key = "-".join([domain, uid])
    cache_key = RedisKey.WEBSERVICE_USER_LOGIN.format(login_key)
    cache_data = await self.redis.get(cache_key)
    if not access_token or not cache_data or access_token != cache_data:
        return False
    return True


async def api_limit_valid(self, restrict):
    """
    restrict: (interval, frequency)
    interval: 时间间隔
    frequency: 限制频次
    """
    interval, frequency = restrict
    path = self.request.path
    client_ip = self.parameter["client_ip"]
    uid = self.parameter["uid"]
    salt = "-".join([client_ip, path, uid])
    limit_key = RedisKey.USER_ACCESS_API_LIMIT.format(salt)
    limit_data = await self.redis.get(limit_key)

    if not limit_data:
        await self.redis.incr(limit_key)
        await self.redis.expire(limit_key, interval)
    else:
        if int(limit_data) < frequency:
            await self.redis.incr(limit_key)
        else:
            logging.warning(f"api limit for {salt}")
            return False
    return True


async def group_check(self, schema, login_check, api_restrict):
    _code = CODE_0

    # 参数校验
    if schema:
        if not parameter_valid(schema, self.parameter):
            return CODE_101
    # 登录校验
    if login_check:
        if not await login_valid(self):
            return CODE_205
    # 接口访问限制
    if api_restrict:
        if not await api_limit_valid(self, api_restrict):
            return CODE_301
    return _code


def send_message(self, return_data):
    return_data.pop("data", "")
    env = self.settings.get("env")
    if env == "prod" and self.request.path not in Constant.NO_RECORD_URI:
        start_time = self.parameter["request_time"]
        return_time = datetime_now()
        cost_time = round((return_time - start_time).total_seconds() * 1000.0, 3)
        message_info, log_info = {}, {}
        collection = str_now("%Y%m")
        self.parameter["request_time"] = Common.format_datetime(self.parameter["request_time"])
        log_info["channel"] = self.settings.get("channel", "")
        log_info["headers"] = self.request.headers._dict
        log_info["routing"] = self.parameter.get("routing", "")
        log_info["path"] = self.request.path
        log_info["parameter"] = self.parameter
        log_info["return_data"] = return_data
        log_info["start_time"] = start_time.strftime("%Y-%m-%d %X.%f")
        log_info["return_time"] = return_time.strftime("%Y-%m-%d %X.%f")
        log_info["cost_time"] = cost_time
        log_info["trace"] = return_data["trace"]
        message_info["collection"] = collection
        message_info["log_info"] = log_info
        try:
            self.kafka_producer.log_send(value=message_info)
        except Exception as e:
            logging.warning(traceback.format_exc())
            logging.warning(f"send log to kafka error, {e}")


def uri_check(schema=None, login_check: bool = True, api_restrict: tuple = None):
    def validate(func):
        @wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            request_id = self.parameter.get("request_id", "")
            logging.debug(f"parameter: {self.parameter}")
            try:
                check_code = await group_check(self, schema, login_check, api_restrict)
                if check_code == CODE_0:
                    return_data = await func(self, *args, **kwargs)
                else:
                    return_data = ReturnData(check_code)
            except Exception as e:
                logging.error(e)
                logging.error(traceback.format_exc())
                return_data = ReturnData(CODE_500, trace=str(e))
            return_data.request_id = request_id
            return_time = datetime_now()
            duration = round(
                (return_time - self.parameter["request_time"]).total_seconds() * 1000, 3)
            logging.debug(f"{self.request.method} {self.request.path} "
                          f"{request_id} duration: {duration}ms")
            send_message(self, return_data.value)
            await self.finish(return_data.value)
            return

        return async_wrapper

    return validate
