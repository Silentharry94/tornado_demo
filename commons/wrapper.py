#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : wrapper.py
# @Desc    : 装饰器文件

import traceback

from jsonschema import Draft4Validator, ValidationError
from playhouse.test_utils import count_queries

from commons.constant import Constant
from commons.initlog import logging
from commons.status_code import *
from utils.request_util import ReturnData


def parameter_check(schema, loginCheck=True):
    def validate(func):
        async def wrapper(self, *args, **kwargs):
            logging.debug("====================================")
            logging.debug("parameter: {}".format(self.parameter))
            return_data = ReturnData(CODE_1)
            flag = True
            if loginCheck:
                flag = login_check(self)
            if not flag:
                return_data = ReturnData(CODE_0)
                self.write(return_data.value)
                self.finish()
                return
            try:
                Draft4Validator(schema=schema).validate(self.parameter)
            except ValidationError as e:
                logging.warning("{}: {}".format(CODE_0, e.message))
                return_data = ReturnData(CODE_0, msg=e.message)
            else:
                try:
                    return_data = await func(self, *args, **kwargs)
                except BaseException:
                    logging.error(traceback.format_exc())
                    return_data = ReturnData(CODE_0)
            finally:
                if isinstance(return_data, ReturnData):
                    logging.info(
                        "Success handlers request: {}, code: {}".format(
                            self.request.path, return_data.code))
                    self.write(return_data.value)
                else:
                    logging.info(
                        "Success handlers request: {}".format(
                            self.request.path))
                    self.write(return_data)
                self.finish()
            return

        return wrapper

    return validate


def no_parameter_check(loginCheck=True):
    def validate(func):
        async def wrapper(self, *args, **kwargs):
            logging.debug(f"====================================")
            logging.debug("parameter: {}".format(self.parameter))

            flag = True
            if loginCheck:
                flag = login_check(self)
            if not flag:
                return_data = ReturnData(CODE_0)
                self.write(return_data.value)
                self.finish()
                return

            try:
                return_data = await func(self, *args, **kwargs)
            except BaseException:
                logging.error(traceback.format_exc())
                return_data = ReturnData(CODE_0)
            if isinstance(return_data, ReturnData):
                logging.info(
                    "Success handlers request: {}, code: {}".format(
                        self.request.path, return_data.code))
                self.write(return_data.value)
            else:
                logging.info(
                    "Success handlers request: {}".format(
                        self.request.path))
                self.write(return_data)
            self.finish()
            return

        return wrapper

    return validate


def count_sql(func):
    async def wrapper(self, *args, **kwargs):
        with count_queries() as counter:
            return_data = await func(self, *args, **kwargs)
        logging.debug(f"sql count: {counter.count}")
        return return_data

    return wrapper


def login_check(self):
    """
    redis_key: domain+channel+uid
    :param self:
    :return:
    """
    flag = False
    if "device" not in self.parameter:
        return flag
    if "channel" not in self.parameter:
        return flag
    if "uid" not in self.parameter:
        return flag
    if "token" not in self.parameter:
        return flag
    if "domain" not in self.parameter:
        return flag
    device = self.parameter.get("device")
    channel = self.parameter["channel"]
    uid = self.parameter["uid"]
    login_token = self.parameter["token"]
    domain = self.parameter["domain"]
    key = "".join([domain, channel, uid])
    token = self._redis.get(key)
    if not login_token:
        logging.debug("please confirm post token")
        return flag
    if not token or login_token != token:
        logging.debug("token invalid or token does not exist")
        return flag
    if device not in Constant.DEVICE:
        logging.debug("Unrecognized device")
        return flag
    flag = True
    return flag
