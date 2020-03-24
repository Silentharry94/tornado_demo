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
    Model,
    BigIntegerField,
    TextField,
    SmallIntegerField
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
    channel = CharField(max_length=16, verbose_name="渠道")
    uid = CharField(max_length=64, verbose_name="用户id")
    accid = CharField(max_length=64, verbose_name="聊天id")
    push_id = CharField(max_length=64, verbose_name="推送id")
    role_id = CharField(max_length=8, verbose_name="角色id")
    account_code = CharField(max_length=64, verbose_name="账号编码")
    mobile = CharField(max_length=16, verbose_name="登陆帐号")
    username = CharField(max_length=16, verbose_name="用户名")
    password = CharField(max_length=64, verbose_name="用户密码")
    status = SmallIntegerField(null=False, default=1, verbose_name="帐号状态")

    registration_time = DateTimeField(default=datetime.datetime.now, verbose_name="注册时间")
    login_time = DateTimeField(default=datetime.datetime.now, verbose_name="登陆时间")
    login_ip = CharField(max_length=16, verbose_name="登陆ip")
    device = CharField(max_length=16, null=False, default="android", verbose_name="设备名称")

    company = CharField(max_length=64, verbose_name="公司名称")
    avatar = CharField(max_length=256, verbose_name="用户头像")
    score = BigIntegerField(verbose_name="积分")
    phone = CharField(max_length=16, verbose_name="手机号")
    identity = CharField(max_length=64, verbose_name="身份证号")
    gender = SmallIntegerField(null=False, default=1, choices=(0, 1), verbose_name="性别")
    qq_no = CharField(max_length=16, verbose_name="qq号")
    we_chat = CharField(max_length=32, verbose_name="微信号")
    email = CharField(max_length=64, verbose_name="电子邮箱")
    born = CharField(max_length=16, verbose_name="出生日期")
    shop_tag = CharField(max_length=32, verbose_name="店铺标签")
    kind_tag = CharField(max_length=32, verbose_name="工种标签")

    class Meta:
        table_name = "user_base"


class Permission(BaseModel):
    channel = CharField(max_length=16, verbose_name="渠道")
    permission_id = CharField(max_length=8, verbose_name="权限id")
    title = CharField(max_length=16, verbose_name="标题")
    description = CharField(max_length=64, verbose_name="权限描述")
    status = SmallIntegerField(null=False, default=0, verbose_name="状态标记")
    create_time = DateTimeField(default=datetime.datetime.now, verbose_name="创建时间")
    update_time = DateTimeField(default=datetime.datetime.now, verbose_name="更新时间")

    class Meta:
        table_name = "permission_base"


class Role(BaseModel):
    channel = CharField(max_length=16, verbose_name="渠道")
    role_id = CharField(max_length=8, verbose_name="角色id")
    title = CharField(max_length=16, verbose_name="标题")
    description = CharField(max_length=64, verbose_name="角色描述")
    status = SmallIntegerField(null=False, default=0, verbose_name="状态标记")
    create_time = DateTimeField(default=datetime.datetime.now, verbose_name="创建时间")
    update_time = DateTimeField(default=datetime.datetime.now, verbose_name="更新时间")

    class Meta:
        table_name = "role_base"


class AuthBinding(BaseModel):
    channel = CharField(max_length=16, verbose_name="渠道")
    master_uid = CharField(max_length=128, verbose_name="用户唯一id")
    role_id = CharField(max_length=8, verbose_name="角色id")
    permission_group = TextField(verbose_name="角色权限")
    binding_time = DateTimeField(default=datetime.datetime.now, verbose_name="绑定时间")
    status = SmallIntegerField(null=False, default=0, verbose_name="状态标记")

    class Meta:
        table_name = "auth_binding_base"


if __name__ == "__main__":
    _mysql.create_tables([
        UserBase,
        Permission,
        Role,
        AuthBinding
    ])
