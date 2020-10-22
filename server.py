#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:34
# @Author  : Hanley
# @File    : server.py
# @Desc    : 项目启动文件


import os
import time

import tornado.web
from tornado import httpserver, ioloop
from tornado.httpclient import AsyncHTTPClient
from tornado.options import define, options

AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient", max_clients=1000)
define("port", default=14370, type=int)
define("env", default='dev', type=str)
options.parse_command_line()

# 生成配置文件
from commons.common import Common

FILE_MAP = {
    'dev': 'config_dev.ini',
    'prod': 'config_prod.ini',
    'local': 'config_local.ini'
}
source_file = os.path.join(os.getcwd(), FILE_MAP.get(options.env))
target_file = os.path.join(os.getcwd(), 'config.ini')
Common.cp_file(source_file, target_file)

from commons.initlog import logging
from urls.url import handlers_loads
from utils.database_util import (
    RedisConnect,
    RetryConnectMysql,
)

_settings = {
    "cookie_secret": "eDXDWxzSeKVbhpGNUhMoVtWIDlAZJyXHrAOulHfOsLEkWIeq",
    'xsrf_cookies': False,
    'debug': False,
    "gzip": True
}


class Application(tornado.web.Application):

    def __init__(self):
        _settings["log_function"] = log_request
        self.init_database()
        super().__init__(handlers_loads(), **_settings)

    def init_database(self):
        _redis = RedisConnect().client
        _mysql = RetryConnectMysql.connect_mysql()
        _mysql.connect()
        _redis.set("start_demo_time", time.strftime("%Y-%m-%d %X"), ex=60 * 60 * 8)
        logging.debug("success connect mysql: {}:{}".format(
            _mysql.connect_params["host"],
            _mysql.connect_params["port"]))


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
    server.listen(options.port, address="0.0.0.0")
    logging.debug(f"start demo {options.env} success, at port {options.port}")
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
