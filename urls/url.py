#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:40
# @Author  : Hanley
# @File    : url.py
# @Desc    : 路由文件

from urls import user_url


def handlers_loads():
    handlers = []

    handlers.extend(user_url.router)

    return handlers
