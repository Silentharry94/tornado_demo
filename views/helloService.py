#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/23 下午6:03
# @Author  : Hanley
# @File    : helloService.py
# @Desc    :
import os

from commons.common import str_now, SyncClientSession
from commons.status_code import *
from commons.initlog import logging
from middelware.core import BaseHandler, ReturnData
from middelware.wrapper import uri_check
from models.test import AsyncDB


class HelloService(BaseHandler):
    SUPPORTED_METHODS = ("GET", "POST", "DELETE")

    @uri_check()
    async def get(self):
        page = int(self.parameter.get("page", 1))
        page_size = int(self.parameter.get("page_size", 10))
        msg = "Hello World, It's tornado demo"
        # data = [{"num": i / 100 + (i + 1) / 10} for i in range(100)]
        redis_data = await self.redis.hgetall("STR_NOW")
        skip_num = (page - 1) * page_size
        mongo_query = self.mongo["web_service"]["test"].find(
            {}, {"_id": 0}).skip(skip_num).limit(page_size)
        mongo_data = [item async for item in mongo_query]
        display = (AsyncDB.request_id, AsyncDB.type, AsyncDB.type_id, AsyncDB.pid)
        mysql_query = AsyncDB.select(*display).paginate(page, page_size).dicts()
        mysql_query = await self.mysql.execute(mysql_query)
        mysql_data = [item for item in mysql_query]
        data = {
            "redis_data": redis_data,
            "mongo_data": mongo_data,
            "mysql_data": mysql_data
        }
        return ReturnData(
            CODE_1, data=data, msg=msg, decimal=True,
            **{"page": page, "page_size": page_size})

    @uri_check()
    async def post(self):
        async_fetch_res = await self.async_client.async_json(
            "GET", "https://api.bilibili.com/x/web-frontend/data/collector")
        sync_fetch_res = SyncClientSession().sync_json(
            "GET", "https://api.bilibili.com/x/web-frontend/data/collector")
        logging.debug(f"sync_fetch_res: {sync_fetch_res}")
        logging.debug(f"async_fetch_res: {async_fetch_res}")
        self.redis.hset("STR_NOW", self.parameter["request_id"], str_now())
        await self.mongo["web_service"]["test"].insert_one(
            {"parameter": self.parameter})
        mysql_sql = AsyncDB.insert(
            pid=os.getpid(),
            type="MYSQL",
            type_id=id(self.mysql),
            request_id=self.parameter['request_id']
        )
        mongo_sql = AsyncDB.insert(
            pid=os.getpid(),
            type="MONGODB",
            type_id=id(self.mongo),
            request_id=self.parameter['request_id']
        )
        redis_sql = AsyncDB.insert(
            pid=os.getpid(),
            type="REDIS",
            type_id=id(self.redis),
            request_id=self.parameter['request_id']
        )
        client_sql = AsyncDB.insert(
            pid=os.getpid(),
            type="CLIENT",
            type_id=id(self.async_client),
            request_id=self.parameter['request_id']
        )
        await self.mysql.execute(mysql_sql)
        await self.mysql.execute(mongo_sql)
        await self.mysql.execute(redis_sql)
        await self.mysql.execute(client_sql)
        return ReturnData()

    @uri_check()
    async def delete(self):
        await self.redis.delete("STR_NOW")
        self.mongo.drop_database("web_service")
        AsyncDB.truncate_table()
        return ReturnData()
