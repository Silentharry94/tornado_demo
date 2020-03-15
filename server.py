#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:34
# @Author  : Hanley
# @File    : server.py
# @Desc    : 项目启动文件

import time

import tornado.web
from tornado import httpserver, ioloop
from tornado.options import define, options

from commons.initlog import logging
from urls.url import handlers_loads
from utils.database_util import (
    RedisConnect
)

define("port", default=1212, type=int)

_settings = {
    "cookie_secret": "p4Qy1mcwQJiSOAytobquL3YDYuXDkkcYobmUWsaBuoo",
    'xsrf_cookies': False,
    'debug': True,
    "gzip": True
}


class Application(tornado.web.Application):

    def __init__(self):
        _settings["log_function"] = log_request
        self.init_database()
        super().__init__(handlers_loads(), **_settings)

    def init_database(self):
        _redis = RedisConnect().client
        _redis.set("start_tornado_demo_time", time.strftime("%Y-%m-%d %X"))
        # _mongo = MongodbConnect().client
        # _mysql = RetryConnectMysql.connect_mysql()
        # _mysql.connect()
        # logging.debug("success connect mysql: {}:{}".format(
        #     _mysql.connect_params["host"],
        #     _mysql.connect_params["port"]))


def log_request(handler):
    template = ' {code} {method} {time:0.2f}ms '
    request_time = 1000.0 * handler.request.request_time()
    data = {
        "code": handler.get_status(),
        "method": handler._request_summary(),
        "time": request_time,
    }
    logging.info(template.format(**data))


def main():
    app = Application()
    server = httpserver.HTTPServer(app)
    options.parse_command_line()
    server.listen(options.port, address="0.0.0.0")
    logging.debug("start tornado demo success, at port [{}]".format(options.port))
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
