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


class RedisKey:
    second = 1
    minute = 60
    hour = minute * 60
    day = hour * 24
    month = day * 30

    WEBSERVICE_USER_LOGIN = "webservice_user_login_{}"
    DOMAIN_CONFIG = "domain_config_{}"
    USER_INFO_BY_UID = "user_info_by_uid_{}"
    USER_ACCESS_API_LIMIT = "user_access_api_limit_{}"
    USER_RESET_PWD_VERIFY_CODE = "user_reset_pwd_verify_code_{}"
    USER_REGISTER_VERIFY_CODE = "user_register_verify_code_{}"


class Constant:
    PROJECT = "demo"
    # encrypt config
    BLOCK_SIZE = 16

    # base64.encodebytes(get_random_bytes(16)).strip().decode()
    ENCRYPT_KEY = 'luYg5DM8yTPXYWnijNAzpw=='

    # config file path
    YAML_CONFIG = make_file_path('config.yaml')
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

    # request
    COMMON_REQUEST_PARAM = [
        "client_id", "request_id", "start_time",
    ]
    NO_RECORD_URI = ()

    # external request
    TIME_OUT = 3
    MID_TIME_OUT = 10
    LONG_TIME_OUT = 30
    JSON_HEADERS = {"Content-Type": "application/json"}
