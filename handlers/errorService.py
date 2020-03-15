#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/3/15 下午11:32
# @Author  : Hanley
# @File    : errorService.py
# @Desc    : 

from abc import ABC

from commons.initlog import logging
from commons.status_code import *
from commons.wrapper import no_parameter_check
from utils.request_util import BaseHandler, ReturnData


class ErrorService(BaseHandler, ABC):

    @no_parameter_check()
    async def get(self):
        data = "Hello World, It's tornado demo error url"
        logging.info(data)
        return ReturnData(CODE_1, data, decimal=True)
