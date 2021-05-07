#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/19 下午4:34
# @Author  : Hanley
# @File    : server.py
# @Desc    : 项目启动文件
import asyncio
import logging

import uvloop
from tornado import httpserver, ioloop
from tornado.options import define, options

define("port", default=9376, type=int)
define("env", default="local", type=str)
options.logging = None
options.parse_command_line()
from commons.common import Common

Common.init_config_file(options.env)

from commons.common import AsyncClientSession
from commons.constant import Constant
from commons.initlog import logging
from scripts.init_tables import sync_uri
from urls.url import handlers_loads
from utils.async_db import AsyncRedis, AsyncMySQLConnect, AsyncMongodbConnect, AsyncManager
from middelware.core import BaseApp


def make_settings(loop) -> dict:
    config = Common.yaml_config()
    redis_config = config["redis"]
    mongo_config = config["mongo"]
    mysql_config = config["mysql"]
    async_client = AsyncClientSession()
    mysql_client = AsyncMySQLConnect.init_db(mysql_config)
    mysql_manager = AsyncManager(database=mysql_client)
    mongo_client = AsyncMongodbConnect(mongo_config).client
    redis_client = AsyncRedis(redis_config)
    loop.run_until_complete(redis_client.init_db())
    loop.run_until_complete(async_client.init_session())

    return {
        "cookie_secret": "p4Qy1mcwQJiSOAytobquL3YDYuXDkkcYobmUWsaBuoo",
        'xsrf_cookies': False,
        'debug': False,
        "gzip": True,
        "env": options.env,
        "async_client": async_client,
        "redis": redis_client.client,
        "mysql": mysql_manager,
        "mongo": mongo_client
    }


def app(options):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    settings = make_settings(loop)
    app = BaseApp(handlers_loads(), settings)
    sync_uri(handlers_loads())
    server = httpserver.HTTPServer(app)
    server.listen(options.port, address="0.0.0.0")
    try:
        logging.debug(f"start {Constant.PROJECT} {options.env} success,"
                      f" at port [%s]" % options.port)
        ioloop.IOLoop.instance().start()
    except BaseException:
        settings["redis"].close()
        loop.run_until_complete(settings["async_client"].close())
        loop.run_until_complete(settings["redis"].wait_closed())
        loop.run_until_complete(settings["mysql"].close())
        ioloop.IOLoop.instance().stop()
        logging.debug(f"{Constant.PROJECT} loop safe stop")


if __name__ == '__main__':
    app(options)
