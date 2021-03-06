#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:40
# @Author  : Hanley
# @File    : url.py
# @Desc    : 路由文件

from urls import error_url
from urls import hello_url


def handlers_loads():
    handlers = []

    handlers.extend(hello_url.router)

    handlers.extend(error_url.router)

    print(handlers)
    return handlers
