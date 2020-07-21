#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : constant.py
# @Desc    : 项目常量文件

import os


def make_file_path(config_name: str) -> str:
    curr_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(curr_dir, config_name)


class Constant(object):
    # encrypt config
    BLOCK_SIZE = 16
    # base64.encodebytes(get_random_bytes(16)).strip().decode()
    ENCRYPT_KEY = 'luYg5DM8yTPXYWnijNAzpw=='
    # config path
    CONFIG_PATH = {
        'config': 'config.ini',
    }
    # config file path
    INI_PATH = make_file_path(CONFIG_PATH['config'])

    PROJECT_CHANNEL = "Hanley"

    DEVICE = {
        "ios",
        "android",
        "web",
        "mini"
    }

    APP_DEVICE = {
        "ios",
        "android"
    }

    WEB_DEVICE = {
        "web",
        "mini"
    }


class ReturnCode(object):
    CN_CODE = {
        0: "错误返回",
        1: "成功返回"
    }
