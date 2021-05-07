#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:28
# @Author  : Hanley
# @File    : base.py
# @Desc    : 数据模型
import datetime

from peewee import *

from commons.common import Common
from utils.async_db import AsyncMySQLConnect

mysql_config = Common.yaml_config("mysql")
mysql_client = AsyncMySQLConnect.init_db(mysql_config)


class BaseModel(Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        database = mysql_client


class UriConfig(BaseModel):
    code = IntegerField(unique=True, verbose_name="接口编码")
    path = CharField(max_length=128, default="", unique=True, verbose_name="接口地址")
    name = CharField(max_length=63, default="", verbose_name="接口名称")
    regex = SmallIntegerField(default=0, verbose_name="是否使用正则")
    pattern = CharField(max_length=256, default="", verbose_name="正则表达式")
    description = CharField(max_length=256, default="", verbose_name="接口描述")
    method = CharField(default="GET", max_length=64, verbose_name="请求方式")
    login_check = SmallIntegerField(default=1, verbose_name="登录权限")
    access_check = SmallIntegerField(default=1, verbose_name="访问权限")
    schema = TextField(default="", verbose_name="参数校验")
    status = SmallIntegerField(index=True, default=1, verbose_name="启用标记")
    create_time = DateTimeField(default=datetime.datetime.now, verbose_name="创建时间")
    update_time = DateTimeField(default=datetime.datetime.now, verbose_name="更新时间")

    class Meta:
        table_name = "uri_config"
