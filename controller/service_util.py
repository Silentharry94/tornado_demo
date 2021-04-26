#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/23 下午6:03
# @Author  : Hanley
# @File    : service_util.py
# @Desc    :

import bcrypt

from commons.common import singleton, Common
from utils.sync_db import RedisConnect, MongodbConnect


@singleton
class Service(object):
    _init = False

    def __init__(self):
        self.init()

    def init(self):
        if self._init:
            return
        mongo_config = Common.yaml_config("mongo")
        redis_config = Common.yaml_config("redis")
        self.mongo = MongodbConnect(mongo_config).client
        self.redis = RedisConnect(redis_config).client
        self._init = True

    @staticmethod
    def generate_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(8)).decode()

    @staticmethod
    def check_password(new_password: str, old_password: str) -> bool:
        return bcrypt.checkpw(new_password.encode("utf-8"), old_password.encode("utf-8"))
