#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : wrapper.py
# @Desc    : 装饰器文件

import traceback

from jsonschema import Draft4Validator, ValidationError

from commons.constant import Constant
from commons.initlog import logging
from commons.status_code import *  # noqa
from utils.request_util import ReturnData


def parameter_check(schema, valid_check=False):
    def validate(func):
        async def wrapper(self, *args, **kwargs):
            logging.debug("====================================")
            logging.debug("parameter: {}".format(self.parameter))
            return_data = ReturnData(CODE_1)
            try:
                Draft4Validator(schema=schema).validate(self.parameter)
            except ValidationError as e:
                logging.warning("{}: {}".format(CODE_0, e.message))
                return_data = ReturnData(CODE_0, msg=e.message)
            else:
                flag = True
                if valid_check:
                    flag = valid_login(self)
                if flag:
                    try:
                        return_data = await func(self, *args, **kwargs)
                    except BaseException:
                        logging.error(traceback.format_exc())
                        return_data = ReturnData(CODE_0)
                else:
                    return_data = ReturnData(CODE_0)
            finally:
                if isinstance(return_data, ReturnData):
                    logging.info(
                        "Success handlers request: {}, code: {}".format(
                            self.request.path, return_data.code))
                    self.write(return_data.value)
                elif isinstance(return_data, bytes):
                    logging.info(
                        "Success handlers request: {}".format(self.request.path))
                    self.write(return_data)
                else:
                    logging.info(
                        "Success handlers request: {}".format(self.request.path))
                    self.write(return_data)
                self.finish()
            return
        return wrapper
    return validate


def no_parameter_check():
    def validate(func):
        async def wrapper(self, *args, **kwargs):
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


def valid_login(self):
    """
    redis_key: channel+uid
    :param self:
    :return:
    """
    check_params = ("device", "channel", "uid", "token")
    flag = False

    device = self.parameter["device"]
    channel = self.parameter["channel"]
    uid = self.parameter["uid"]
    login_token = self.parameter["token"]
    redis_key = "".join([channel, uid])
    redis_token = self._redis.get(redis_key)
    if not login_token:
        logging.debug("please confirm post token")
        return flag
    if not redis_token or login_token != redis_token:
        logging.debug("token invalid or token does not exist")
        return flag
    if device not in Constant.DEVICE:
        logging.debug("Unrecognized device")
        return flag
    flag = True
    return flag
