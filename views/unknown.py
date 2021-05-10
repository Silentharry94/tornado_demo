#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/5/6 6:19 下午
# @Author  : Hanley
# @File    : unknown.py
# @Desc    :

from commons.status_code import *
from middelware.core import BaseHandler, ReturnData
from middelware.wrapper import uri_check


class UnknownService(BaseHandler):
    SUPPORTED_METHODS = ("GET", "HEAD", "POST", "DELETE", "PATCH", "PUT", "OPTIONS")

    @uri_check()
    async def get(self):
        return ReturnData(CODE_404)

    async def post(self):
        await self.get()

    async def put(self):
        await self.get()

    async def delete(self):
        await self.get()

    async def options(self):
        await self.get()

    async def head(self):
        await self.get()

    async def patch(self):
        await self.get()
