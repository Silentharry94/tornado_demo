#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/5/6 4:58 下午
# @Author  : Hanley
# @File    : unknown.py
# @Desc    :

from tornado.web import url

from views import unknown

router = [
    url(r'.*', unknown.UnknownService, name="unknown"),
]
