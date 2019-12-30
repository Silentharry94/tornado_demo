#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : wrapper.py
# @Desc    : 装饰器文件

import traceback

from jsonschema import Draft4Validator, ValidationError

from commons.initlog import logging
from utils.request_util import ReturnData


def parameter_check(schema, check=True):
    def validate(func):
        async def wrapper(self, *args, **kwargs):
            logging.debug("try to validate parameter, "
                          "parameter: {}".format(self.parameter))
            return_data = ReturnData(200)
            try:
                Draft4Validator(schema=schema).validate(self.parameter)
            except ValidationError as e:
                logging.warning("{}: {}".format(600, e.message))
                return_data = ReturnData(600, e.message)
            else:
                logging.debug("validate parameter passed")
                login_flag = True
                if check:
                    login_flag = user_check(self)
                if login_flag:
                    try:
                        return_data = await func(self, *args, **kwargs)
                    except BaseException:
                        logging.error(traceback.format_exc())
                        return_data = ReturnData(500)
                else:
                    return_data = ReturnData(205)
            finally:
                logging.info(
                    "Success handlers request: {}, code: {}".format(
                        self.request.path, return_data.code))
                self.write(return_data.value)
                self.finish()
            return

        return wrapper

    return validate


def no_parameter_check(check=True):
    def validate(func):
        async def wrapper(self, *args, **kwargs):
            login_flag = True
            if check:
                login_flag = user_check(self)
            if login_flag:
                try:
                    return_data = await func(self, *args, **kwargs)
                except BaseException:
                    logging.error(traceback.format_exc())
                    return_data = ReturnData(500)
            else:
                return_data = ReturnData(205)
            logging.info(
                "Success handlers request: {}, code: {}".format(
                    self.request.path, return_data.code))
            self.write(return_data.value)
            self.finish()
            return

        return wrapper

    return validate


def user_check(self):
    user_id = self.parameter.get("user_id", None)
    login_token = self.parameter.get("token", None)
    if not user_id or not login_token:
        logging.debug("请确保传入user_id和token")
        return False
    key = "".join([self.channel, user_id])
    token = self._redis.get(key)
    if not token or login_token != token:
        logging.debug("token失效，请重新登录")
        return False
    else:
        return True
