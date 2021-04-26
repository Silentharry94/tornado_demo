#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/23 下午6:03
# @Author  : Hanley
# @File    : helloService.py
# @Desc    :

from commons.common import str_now
from commons.initlog import logging
from commons.status_code import *
from middelware.core import BaseHandler, ReturnData
from middelware.wrapper import uri_check


class HelloService(BaseHandler):

    @uri_check()
    async def get(self):
        data = "Hello World, It's tornado demo"
        logging.info(data)
        redis_data = self.redis.getset(self._inner["request_id"], str_now())
        logging.debug(f"redis_data: {redis_data}")
        self.mongo["tornado"]["test"].insert_one(self.parameter)
        await self.async_client.fetch_json(
            "GET",
            "https://007vin.com/v2/inventory/part/inventory/merchants_zhb?pid=J9C2713&brandCode=jaguar&lng=120.21&lat=30.25")
        mongo_query = self.mongo["tornado"]["test"].find({}, {"_id": 0})
        mongo_data = list(mongo_query)

        return ReturnData(CODE_1, mongo_data)
