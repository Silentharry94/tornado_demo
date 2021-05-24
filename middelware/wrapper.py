#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : wrapper.py
# @Desc    : 装饰器文件
import traceback

from jsonschema import Draft4Validator, ValidationError

from commons.common import datetime_now
from commons.initlog import logging
from commons.status_code import *
from middelware.core import ReturnData


async def group_check(self, schema):
    _code = CODE_0
    # 参数校验
    if schema:
        try:
            Draft4Validator(schema=schema).validate(self.parameter)
        except ValidationError as e:
            logging.warning("{}: {}".format(CODE_101, e.message))
            _code = CODE_101
    return _code


def uri_check(schema=None):
    def validate(func):
        async def wrapper(self, *args, **kwargs):
            request_id = self.parameter["request_id"]
            request_time = self.parameter["request_time"]
            logging.debug(f"headers: {self.request.headers._dict}")
            logging.debug(">>>parameter: {}".format(self.parameter))
            _return_data = ReturnData(CODE_0)
            try:
                check_code = await group_check(self, schema)
                # 通过校验
                if check_code == CODE_0:
                    _return_data = await func(self, *args, **kwargs)
                else:
                    _return_data = ReturnData(check_code)
            except Exception as e:
                logging.error(traceback.format_exc())
                _return_data = ReturnData(CODE_500, trace=str(e))
            if isinstance(_return_data, ReturnData):
                _return_data.request_id = request_id
                return_data = _return_data.value
            else:
                return_data = _return_data
            end_time = datetime_now()
            await self.finish(return_data)
            duration = round(
                (end_time - request_time).total_seconds() * 1000, 3)
            self.parameter["duration"] = duration
            logging.debug(f"path: {self.request.path}, "
                          f"request_id: {request_id}, "
                          f"code: {return_data.get('code')}, "
                          f"duration: {duration}ms")
            return return_data

        return wrapper

    return validate
