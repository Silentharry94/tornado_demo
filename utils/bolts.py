#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/5/25 7:56 下午
# @Author  : Hanley
# @File    : bolts.py
# @Desc    :


def is_contain_zh(string):
    """包含汉字的返回TRUE"""
    if not string:
        return False
    for c in string:
        if '\u4e00' <= c <= '\u9fa5':
            return True
    return False
