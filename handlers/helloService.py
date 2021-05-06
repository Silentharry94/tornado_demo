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
        data = [i / 100 + (i + 1) / 10 for i in range(100)]
        data.append(0.125344)
        return ReturnData(CODE_1, data=data, msg=msg, decimal=True)

    async def post(self):
        await self.get()
