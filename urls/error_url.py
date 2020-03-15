#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/3/15 下午11:31
# @Author  : Hanley
# @File    : error_url.py
# @Desc    : 

from tornado.web import url

from handlers import errorService as error

router = [
    url(r'(.*)', error.ErrorService, name="error"),
]
