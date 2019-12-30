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
    PROJECT_NAME = "这毒M药"
    SMS_MESSAGE = "【{}】短信验证码：{}，验证码一分钟内有效"


class ReturnCode(object):
    CN_CODE = {
        0: "错误返回",
        200: "成功返回",
        201: "",
        202: "该手机号已注册",
        203: "账户不存在，请先注册",
        204: "登陆密码错误，请输入正确密码",
        205: "请先登录",
        206: "请输入账号密码",
        401: "验证码已失效",
        402: "验证码不正确",
        500: "程序错误，请联系开发人员",
        600: "传入参数错误",
    }


class Scheme(object):
    # mysql schemes
    PEEWEE_SCHEMES = {
        'apsw',
        'mysql',
        'mysql+pool',
        'postgres',
        'postgres+pool',
        'postgresext',
        'postgresql+pool',
        'sqlite',
        'sqliteext'
        'sqlite+pool',
        'sqliteext+pool',
    }

    # mongodb uri schemes
    MONGODB_SCHEMES = {
        'mongodb'
    }

    HELLO = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string", "examples": ["YQ"]
            }
        },
        "required": [
            "name"
        ]
    }

    TEST_SCHEMES = {
        "type": "array",
        "title": "create order Scheme",
        "items": {
            "type": "object",
            "required": [
                "commodity_list"
            ],
            "properties": {
                "commodity_amount": {
                    "type": "number", "examples": [199.393]
                },
                "commodity_list": {
                    "type": "array",
                    "title": "commodity info list",
                    "items": {
                        "type": "object",
                        "required": [
                            "id",
                            "number"
                        ],
                        "properties": {
                            "id": {
                                "type": "string",
                                "examples": ["943f9326ijs311ea99"]
                            },
                            "name": {
                                "type": "string",
                                "examples": ["华夫饼"]
                            },
                            "price": {
                                "type": "number",
                                "examples": [199.393]
                            },
                            "number": {
                                "type": "integer",
                                "examples": [3]
                            }
                        }
                    }
                }
            }
        }
    }
