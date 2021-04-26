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
from tornado.httpclient import AsyncHTTPClient
from tornado.options import define, options

from utils.sync_db import RedisConnect, MysqlConnect, MongodbConnect

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=1000)
define("port", default=9376, type=int)
define("env", default="local", type=str)
options.parse_command_line()
from commons.common import Common

Common.init_config_file(options.env)

from commons.common import AsyncClientSession
from commons.constant import Constant
from commons.initlog import logging
from scripts.init_tables import sync_uri
from urls.url import handlers_loads
from middelware.core import log_request, BaseApp


def app(options):
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    loop = asyncio.get_event_loop()
    async_client = AsyncClientSession()
    loop.run_until_complete(async_client.init_session())
    settings = {
        "cookie_secret": "p4Qy1mcwQJiSOAytobquL3YDYuXDkkcYobmUWsaBuoo",
        'xsrf_cookies': False,
        'debug': False,
        "gzip": True,
        "env": options.env,
        "log_function": log_request,
        "async_client": async_client,
        "redis": RedisConnect(Common.yaml_config("redis")).client,
        "mysql": MysqlConnect.init_db(Common.yaml_config("mysql")),
        "mongo": MongodbConnect(Common.yaml_config("mongo")).client
    }
    app = BaseApp(handlers_loads(), settings)
    sync_uri(handlers_loads())
    server = httpserver.HTTPServer(app)
    server.listen(options.port, address="0.0.0.0")
    try:
        logging.debug(f"start {Constant.PROJECT} {options.env} success,"
                      f" at port [%s]" % options.port)
        ioloop.IOLoop.instance().start()
    except BaseException as e:
        logging.warning(e)
        loop.run_until_complete(async_client.close())
        ioloop.IOLoop.instance().stop()
        logging.debug(f"{Constant.PROJECT} loop safe stop")


if __name__ == '__main__':
    app(options)
