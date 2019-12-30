#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/23 下午6:03
# @Author  : Hanley
# @File    : user_service.py
# @Desc    :

import math
import random
import time
from abc import ABC
from urllib.parse import urlencode

from tornado.httpclient import HTTPRequest

from commons.common import Common, DealEncrypt
from commons.constant import Constant
from commons.initlog import logging
from commons.wrapper import no_parameter_check
from models.basemodel import UserBase
from utils.request_util import BaseHandler, ReturnData


class AdminHandler(BaseHandler, ABC):

    @no_parameter_check(check=False)
    async def post(self, role, level=None):
        data = None
        if role == "manager":
            code = self.store_manager()
        elif role == "customer":
            code = self.customer_service()
        else:
            code = 200
        return ReturnData(code, data)

    def store_manager(self):
        logging.debug("i am manager")
        return 200

    def customer_service(self):
        logging.debug("i am customer")
        return 200

    def common_func(self):
        return 200


class SendSmsCode(BaseHandler, ABC):
    """
    发送短信验证码
    redis_key:channel+phone
    redis_expires: 60s
    """

    @no_parameter_check(check=False)
    async def post(self):
        phone_number = self.parameter["phone"]
        sms_code = str(random.randint(1110, 8898))

        setMsg = Constant.SMS_MESSAGE.format(
            Constant.PROJECT_NAME, sms_code)

        msg_params = {
            "channel": self.channel,
            "mobile": phone_number,
            "text": setMsg
        }
        request_obj = HTTPRequest(
            url=Common.get_config_value("external-service")["sms_url"],
            method="POST",
            body=urlencode(msg_params),
            request_timeout=10
        )

        await self.fetch_response(request_obj)
        key = "".join([self.channel, phone_number])
        self._redis.set(key, sms_code, ex=60)
        return ReturnData(200)

    async def get(self):
        await self.post()


class UserRegister(BaseHandler, ABC):
    """
    用户注册
    一个手机号只能注册一次
    """

    @no_parameter_check(check=False)
    async def post(self):
        code = 200
        username = self.parameter["username"]
        password = self.parameter.get("password", username[-6:])
        user_info = UserBase.get_or_none(UserBase.username == username)
        if user_info:
            code = 202
        else:
            insert_dict = {
                "uid": DealEncrypt.hash_md5_encrypt(username),
                "username": username,
                "password": DealEncrypt.crypto_encrypt(password),
                "registration_time": time.strftime("%Y-%m-%d %X")
            }
            UserBase.insert(insert_dict).execute()
        return ReturnData(code)

    async def get(self):
        await self.post()


class UserLogin(BaseHandler, ABC):
    """
    用户登录
    redis_key:channel+uid
    """

    @no_parameter_check(check=False)
    async def post(self):
        code = 200
        data = None
        username = self.parameter.get("username", None)
        password = self.parameter.get("password", None)

        # 未输入账号密码
        if not username or not password:
            code = 206
        else:
            user_account = UserBase.get_or_none(UserBase.username == username)
            # 账号不存在
            if user_account is None:
                code = 203
            # 密码不正确
            elif password != DealEncrypt.crypto_decrypt(user_account.password):
                code = 204
            # 正确返回
            else:
                time_stamp = str(math.ceil(time.time()))
                salt = "".join([username, time_stamp])
                token = DealEncrypt.hash_sha256_encrypt(salt)
                key = "".join([self.channel, user_account.uid])
                self._redis.set(key, token)
                data = {"token": token}
        return ReturnData(code, data)

    async def get(self):
        await self.post()


class CheckSmsCode(BaseHandler, ABC):
    """
    校验短信验证码
    """

    @no_parameter_check(check=False)
    async def post(self):
        code = 200
        sms_code = self.parameter["sms_code"]
        phone_number = self.parameter["phone"]
        key = "".join([self.channel, phone_number])
        value = self._redis.get(key)
        # 验证码已失效
        if not value:
            code = 401
        # 验证码不正确
        elif sms_code != value:
            code = 402
        return ReturnData(code)

    async def get(self):
        await self.post()


class ResetPassword(BaseHandler, ABC):
    """
    修改密码
    """

    @no_parameter_check(check=False)
    async def post(self):
        code = 200
        username = self.parameter["username"]
        password = self.parameter["password"]
        dict_update = {
            "password": DealEncrypt.crypto_encrypt(password)
        }
        UserBase.update(dict_update).where(
            UserBase.username == username).execute()
        return ReturnData(code)

    async def get(self):
        await self.post()
