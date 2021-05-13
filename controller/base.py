#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/23 下午6:03
# @Author  : Hanley
# @File    : base.py
# @Desc    :

import asyncio

from commons.common import Common, AsyncClientSession
from utils.async_db import AsyncMySQLConnect, AsyncManager, AsyncMongodbConnect, AsyncRedis


class ControllerBase(object):
    __slots__ = (
        "client",
        "redis",
        "mongo",
        "mysql",
        "loop",
    )
    _init = False

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(ControllerBase, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.init_base()

    def init_base(self, loop=None):
        if not loop:
            self.loop = asyncio.get_event_loop()
        if self._init:
            return
        config = Common.yaml_config()
        redis_config = config["redis"]
        mongo_config = config["mongo"]
        mysql_config = config["mysql"]
        async_client = AsyncClientSession()
        mysql_client = AsyncMySQLConnect.init_db(mysql_config)
        mysql_manager = AsyncManager(database=mysql_client)
        mongo_client = AsyncMongodbConnect(mongo_config).client
        redis_client = AsyncRedis(redis_config)
        self.loop.run_until_complete(redis_client.init_db())
        self.loop.run_until_complete(async_client.init_session())
        self.client = async_client
        self.redis = redis_client.client
        self.mongo = mongo_client
        self.mysql = mysql_manager
        ControllerBase._init = True

    def close(self):
        self.redis.close()
        self.loop.run_until_complete(self.client.close())
        self.loop.run_until_complete(self.redis.wait_closed())
        self.loop.run_until_complete(self.mysql.close())
