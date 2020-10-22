#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/23 下午6:03
# @Author  : Hanley
# @File    : service_util.py
# @Desc    :

import bcrypt
from peewee import fn
from playhouse.shortcuts import dict_to_model, model_to_dict

from utils.database_util import RedisConnect, MongodbConnect


class ServiceUtil(object):

    def __init__(self):
        self.mongo = MongodbConnect().client
        self.redis = RedisConnect().client

    @staticmethod
    def generate_password(password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(8)).decode()

    @staticmethod
    def check_password(new_password: str, old_password: str) -> bool:
        return bcrypt.checkpw(new_password.encode("utf-8"), old_password.encode("utf-8"))

    def get_params(self, model_class, dicts, exclude=()):
        _class = dict_to_model(model_class, dicts, ignore_unknown=True)
        _parameter = model_to_dict(_class, exclude=exclude)
        param = dict()
        for _k, _v in _parameter.items():
            if _v is not None and _k in dicts:
                param[_k] = _v
        return param

    def generate_max_id(self, model, modelKey, length="big", start=None) -> str:
        maxId = model.select(fn.Max(modelKey)).scalar()
        if start is None:
            if length == "big":
                start = 100 << 10
            elif length == "small":
                start = 10 << 10
            else:
                start = 1
        if not maxId:
            maxId = start
        else:
            maxId = str(int(maxId) + 1)
        return str(maxId)
