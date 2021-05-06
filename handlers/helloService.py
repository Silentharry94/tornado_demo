#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/23 下午6:03
# @Author  : Hanley
# @File    : helloService.py
# @Desc    :

from commons.status_code import *
from middelware.core import BaseHandler, ReturnData
from middelware.wrapper import uri_check


class HelloService(BaseHandler):
    SUPPORTED_METHODS = ("GET", "POST")

    @uri_check()
    async def get(self):
        msg = "Hello World, It's tornado demo"
        return ReturnData(CODE_1, msg=msg)

    async def post(self):
        await self.get()
