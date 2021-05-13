#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : wrapper.py
# @Desc    : 装饰器文件
import functools
import traceback

from jsonschema import Draft4Validator, ValidationError

from commons.common import perf_time
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
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            return_data = ReturnData(CODE_0)
            request_id = self._inner.get("request_id", "")
            logging.debug(f"parameter: {self.parameter} request_id: {request_id}")
            try:
                return_data.code = await group_check(self, schema)
                if return_data.code == CODE_0:
                    return_data = await func(self, *args, **kwargs)
            except BaseException as e:
                logging.error(e)
                logging.error(traceback.format_exc())
                return_data.trace = str(e)
                return_data.code = CODE_500
            return_data.request_id = request_id
            await self.finish(return_data.value)
            self._inner["end_time"] = perf_time()
            duration = (self._inner["end_time"] - self._inner["start_time"]) * 1000
            logging.debug(f"path: {self.request.path}, "
                          f"request_id: {request_id} ,"
                          f"duration: {duration}ms")
            return

        return async_wrapper

    return validate
