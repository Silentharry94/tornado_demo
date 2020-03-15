#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/23 下午6:39
# @Author  : Hanley
# @File    : hello_url.py
# @Desc    : 

from tornado.web import url

from handlers import helloService as hello

router = [
    url(r'/hello/world', hello.HelloService, name="test"),
]
