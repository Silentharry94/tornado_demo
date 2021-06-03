#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/12/19 下午4:34
# @Author  : Hanley
# @File    : server.py
# @Desc    : 项目启动文件

from tornado import httpserver, ioloop
from tornado.options import define, options

define("port", default=9376, type=int)
define("env", default="local", type=str)
define("channel", default="demo", type=str)
options.logging = None
options.parse_command_line()
from commons.common import Common

Common.init_config_file(options.env)
from commons.constant import Constant
from commons.initlog import logging
from controller.base import ControllerBase
from scripts.init_tables import sync_uri
from urls.url import handlers_loads
from middelware.core import BaseApp


def make_settings(options) -> dict:
    controller = ControllerBase()
    return {
        "cookie_secret": "p4Qy1mcwQJiSOAytobquL3YDYuXDkkcYobmUWsaBuoo",
        'xsrf_cookies': False,
        'debug': False,
        "gzip": True,
        "env": options.env,
        "channel": options.channel,
        "controller": controller,
    }


def app(options):
    settings = make_settings(options)
    app = BaseApp(handlers_loads(), settings)
    sync_uri(handlers_loads())
    server = httpserver.HTTPServer(app)
    server.listen(options.port, address="0.0.0.0")
    try:
        logging.debug(f"start {Constant.PROJECT} {options.env} success,"
                      f" at port [%s]" % options.port)
        ioloop.IOLoop.instance().start()
    except BaseException:
        settings["controller"].close()
        ioloop.IOLoop.instance().stop()
        logging.debug(f"{Constant.PROJECT} loop safe stop")


if __name__ == '__main__':
    app(options)
