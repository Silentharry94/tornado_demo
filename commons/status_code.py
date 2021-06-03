#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/1/7 下午3:02
# @Author  : Hanley
# @File    : status_code.py
# @Desc    :

CODE_0 = 0
CODE_1 = 1
CODE_101 = 101
CODE_201 = 201
CODE_202 = 202
CODE_203 = 203
CODE_204 = 204
CODE_205 = 205
CODE_206 = 206
CODE_207 = 207
CODE_208 = 208
CODE_209 = 209
CODE_210 = 210
CODE_211 = 211
CODE_300 = 300
CODE_301 = 301
CODE_302 = 302
CODE_400 = 400
CODE_404 = 404
CODE_500 = 500

EN_CODE = {
    CODE_1: "Successfully return",
    CODE_0: "Error return",
    CODE_101: "Parameter error",
    CODE_201: "The account does not exist or the password is incorrect",
    CODE_202: "The account status is abnormal",
    CODE_203: "The account has been registered",
    CODE_204: "Register error, please try again later",
    CODE_205: "Please login",
    CODE_206: "Please open member first",
    CODE_207: "The user has not set up a mailbox",
    CODE_208: "The verification code is incorrect or invalid",
    CODE_209: "Please enter your login password or verification code",
    CODE_210: "Failed to send mail, please try again later",
    CODE_211: "Unable to recognize the email, please retry enter",
    CODE_300: "Unknown domain",
    CODE_301: "Access restricted, please try again later",
    CODE_302: "The service is busy, please try again later",
    CODE_400: "Bad request",
    CODE_404: "Url not found",
    CODE_500: "Server error",
}
