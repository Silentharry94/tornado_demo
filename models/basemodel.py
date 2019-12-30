#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:28
# @Author  : Hanley
# @File    : basemodel.py
# @Desc    : 数据模型

import datetime

from peewee import (
    CharField,
    DateTimeField,
    IntegerField,
    Model,
)

from utils.database_util import RetryConnectMysql

_mysql = RetryConnectMysql.connect_mysql()


class BaseModel(Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 事务属性
        self.transaction = _mysql.atomic

    class Meta:
        database = _mysql


class UserBase(BaseModel):
    uid = CharField(max_length=128, verbose_name="用户唯一id")
    username = CharField(max_length=64, verbose_name="用户账户")
    password = CharField(max_length=128, verbose_name="用户密码")
    registration_time = DateTimeField(default=datetime.datetime.now,
                                      verbose_name="注册时间")
    status = IntegerField(default=1, verbose_name="用户状态")
    role_id = IntegerField(verbose_name="角色id")
    push_id = CharField(max_length=64, verbose_name="推送id")

    class Meta:
        table_name = "user_base"


if __name__ == "__main__":
    _mysql.create_tables([UserBase])
