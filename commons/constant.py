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

    # config file path
    INI_PATH = make_file_path('config.ini')

    PROJECT_CHANNEL = "Hanley"

    # device
    APP_DEVICE = {"ios", "android"}
    WEB_DEVICE = {"web"}
    DEVICE = set()
    DEVICE.update(APP_DEVICE)
    DEVICE.update(WEB_DEVICE)

    # cookie
    COOKIE_CHANNEL = "{}_demo_channel"
    COOKIE_DEVICE = "{}_demo_device"
    COOKIE_UID = "{}_demo_uid"
    COOKIE_TOKEN = "{}_demo_token"

    # external request
    TIME_OUT = 3
    MID_TIME_OUT = 10
    LONG_TIME_OUT = 30
    JSON_HEADERS = {"Content-Type": "application/json"}

    # apply status
    APPLY_STATUS = {
        0: "错误返回",
        21000: "Store无法读取你提供的JSON数据",
        21002: "收据数据不符合格式",
        21003: "收据无法被验证",
        21004: "你提供的共享密钥和账户的共享密钥不一致",
        21005: "收据服务器当前不可用",
        21006: "收据是有效的，但订阅服务已经过期。当收到这个信息时，解码后的收据信息也包含在返回内容中",
        21007: "收据信息是测试用（sandbox），但却被发送到产品环境中验证",
        21008: "收据信息是产品环境中使用，但却被发送到测试环境中验证"
    }


class ReturnCode(object):
    CN_CODE = {
        0: "错误返回",
        1: "成功返回"
    }
