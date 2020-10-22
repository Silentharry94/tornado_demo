#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:28
# @Author  : Hanley
# @File    : base.py
# @Desc    : 数据模型


import time

from peewee import (
    CharField,
    IntegerField,
    Model,
    SmallIntegerField
)

from utils.database_util import RetryConnectMysql

_mysql = RetryConnectMysql.connect_mysql()


class BaseModel(Model):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        database = _mysql


class CommonBase(BaseModel):
    status = SmallIntegerField(null=False, default=1, index=True, verbose_name="用户状态")
    create_time = CharField(max_length=64, default=time.strftime("%Y-%m-%d %X"),
                            verbose_name="创建时间")
    update_time = CharField(max_length=64, default="",
                            verbose_name="更新时间")


class UserBase(BaseModel):
    uid = CharField(max_length=64, null=False, unique=True, verbose_name="用户唯一id")
    mobile = CharField(max_length=32, null=False, unique=True, verbose_name="登陆账号")
    status = SmallIntegerField(null=False, default=1, index=True, verbose_name="用户状态")
    role_id = IntegerField(null=False, default=10, index=True, verbose_name="用户角色")
    device = CharField(max_length=16, null=False, default="android",
                       index=True, verbose_name="设备名称")

    username = CharField(max_length=32, null=False, default="", verbose_name="用户姓名")
    password = CharField(max_length=64, null=False, default="", verbose_name="用户密码")
    last_login_ip = CharField(max_length=32, null=True, default="", verbose_name="登陆ip")
    gender = SmallIntegerField(null=False, default=1, verbose_name="性别")
    company = CharField(max_length=64, null=False, default="", verbose_name="公司名称")
    registration_time = CharField(max_length=64, default=time.strftime("%Y-%m-%d %X"),
                                  verbose_name="注册时间")
    last_login_time = CharField(max_length=64, default=time.strftime("%Y-%m-%d %X"),
                                verbose_name="登陆时间")
    province = CharField(max_length=16, default="", verbose_name="省")
    city = CharField(max_length=16, default="", verbose_name="市")
    area = CharField(max_length=16, default="", verbose_name="区")
    address = CharField(max_length=128, default="", verbose_name="详细地址")
    level = CharField(max_length=16, default="", verbose_name="公司等级")
    licence = CharField(max_length=256, default="", verbose_name="公司营业执照")
    avatar = CharField(max_length=256, default="", verbose_name="用户头像")


class BindingBase(CommonBase):
    master_id = CharField(null=False, max_length=128, index=True, verbose_name="级联id")
    slave_id = CharField(null=False, max_length=128, index=True, verbose_name="被级联id")

    class Meta:
        indexes = (
            (("master_id", "slave_id"), False),
            (("master_id", "slave_id", "status"), False)
        )


class ChannelConfig(BaseModel):
    domain = CharField(max_length=512, default="", unique=True, verbose_name="域名")
    channel = CharField(max_length=64, default="", verbose_name="渠道名")
    description = CharField(max_length=64, default="", verbose_name="渠道描述")

    class Meta:
        table_name = "channel_config"
