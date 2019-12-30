#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/23 下午6:39
# @Author  : Hanley
# @File    : user_url.py
# @Desc    : 

from tornado.web import url

from handlers import user_service as user

router = [
    url(r'/v1/user/register', user.UserRegister, name="用户注册"),
    url(r'/v1/user/send_sms', user.SendSmsCode, name="发送短信验证码"),
    url(r'/v1/user/check_sms', user.CheckSmsCode, name="校验验证码"),
    url(r'/v1/user/user_login', user.UserLogin, name="用户登陆"),
    url(r'/v1/user/reset_password', user.ResetPassword, name="更新用户密码"),
    url(r'/v1/user/test/(?P<role>\w+)', user.AdminHandler, name="测试接口"),
]
