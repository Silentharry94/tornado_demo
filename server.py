#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:34
# @Author  : Hanley
# @File    : server.py
# @Desc    : 项目启动文件

import tornado.web
from tornado import httpserver, ioloop
from tornado.options import define, options

from commons.initlog import logging
from urls.url import handlers_loads

define("port", default=1224, type=int)

_settings = {
    "cookie_secret": "p4Qy1mcwQJiSOAytobquL3YDYuXDkkcYobmUWsaBuoo",
    'xsrf_cookies': False,
    'debug': True,
    "gzip": True
}


class Application(tornado.web.Application):

    def __init__(self):
        _settings["log_function"] = log_request
        super().__init__(handlers_loads(), **_settings)


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
    logging.debug("start kuaizhun success, at port [%s]" % options.port)
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
