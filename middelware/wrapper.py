#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : wrapper.py
# @Desc    : 装饰器文件
import functools
import traceback

from commons.common import perf_time
from commons.initlog import logging
from commons.status_code import *
from middelware.core import ReturnData


async def group_check(self, schema):
    return CODE_0


def uri_check(schema=None):
    def validate(func):
        @functools.wraps(func)
        async def async_wrapper(self, *args, **kwargs):
            logging.debug(f"parameter: {self.parameter}")
            return_data = ReturnData(CODE_0)
            try:
                return_data.code = await group_check(self, schema)
                if return_data.code == CODE_0:
                    return_data = await func(self, *args, **kwargs)
            except BaseException as e:
                logging.error(e)
                logging.error(traceback.format_exc())
                return_data.trace = str(e)
                return_data.code = CODE_500
            start_time = self._inner.get("start_time")
            duration = (perf_time() - start_time) * 1000
            return_data.request_id = self._inner.get("request_id", "")
            logging.debug(f"path: {self.request.path} "
                          f"code: {return_data.code} duration: {duration}ms")
            await self.finish(return_data.value)
            return

        return async_wrapper

    return validate
