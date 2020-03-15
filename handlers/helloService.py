#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/23 下午6:03
# @Author  : Hanley
# @File    : helloService.py
# @Desc    :

from commons.initlog import logging
from commons.status_code import *
from commons.wrapper import no_parameter_check
from utils.request_util import BaseHandler, ReturnData


class HelloService(BaseHandler):

    @no_parameter_check()
    async def get(self):
        data = "Hello World, It's tornado demo"
        logging.info(data)
        return ReturnData(CODE_1, data, decimal=True)
