#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : common.py
# @Desc    : 公共方法文件

import base64
import configparser
import datetime
import hashlib
import json
import os
import random
import re
import time
import traceback
import uuid
from collections.abc import Iterable
from functools import wraps
from random import choice
from string import ascii_letters

import ujson
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from tornado.httpclient import AsyncHTTPClient, HTTPClient

from commons.constant import Constant
from commons.initlog import logging
from commons.status_code import *


def Singleton(cls):
    _instance = {}

    @wraps(cls)
    def _singleton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singleton



class Common(object):

    @staticmethod
    def get_config_value(section=None, file_path=Constant.INI_PATH) -> dict:
        config = configparser.ConfigParser()
        config.read(file_path)
        if isinstance(section, str):
            section = section.lower()
        options = config.options(section)
        dict_result = {}
        for option in options:
            temp = config.get(section, option)
            dict_result.update({option: temp})
        return dict_result

    @staticmethod
    def format_datetime(data):
        if isinstance(data, datetime.datetime):
            return data.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(data, datetime.date):
            return data.strftime("%Y-%m-%d")
        else:
            return data

    @staticmethod
    def validate_phone(phone_number: str) -> bool:
        _pattern = r"13\d{9}|14\d{9}|15\d{9}|16\d{9}|17\d{9}|18\d{9}|19\d{9}"
        pattern = re.compile(_pattern)
        if len(phone_number) != 11:
            return False
        else:
            if pattern.findall(phone_number):
                return True
            else:
                return False

    @staticmethod
    def sync_fetch(req):
        try:
            response = HTTPClient().fetch(req)
            try:
                data = ujson.loads(response.body)
            except BaseException:
                data = response.body
        except BaseException:
            logging.error("route: {} return error".format(req.url))
            logging.error(traceback.format_exc())
            if req.method == "GET":
                param = req.url
            else:
                param = ujson.loads(req.body)
            data = {"code": CODE_0, "data": param, "msg": "外部接口调用异常"}
            return data
        return data

    @staticmethod
    async def async_fetch(req):
        try:
            response = await AsyncHTTPClient().fetch(req)
            logging.error("res: {}".format(response))
            try:
                rpc_data = ujson.loads(response.body)
            except BaseException:
                rpc_data = response.body
        except BaseException:
            error_data = {"code": CODE_0, "msg": "", "data": None}
            logging.error(traceback.format_exc())
            return error_data
        return rpc_data

    @classmethod
    def decimal_dict(cls, _dict: dict):
        for k in _dict:
            if isinstance(_dict[k], dict):
                cls.format_decimal(_dict[k])
            else:
                if isinstance(_dict[k], float):
                    _dict[k] = "{:.2f}".format(_dict[k])
                elif isinstance(_dict[k], str):
                    try:
                        _dict[k] = "{:.2f}".format(float(_dict[k]))
                    except BaseException:
                        continue
                elif isinstance(_dict[k], Iterable):
                    _dict[k] = type(_dict[k])([cls.format_decimal(k) for k in _dict[k]])
                else:
                    return _dict
        return _dict

    @classmethod
    def format_decimal(cls, data):
        if isinstance(data, dict):
            return cls.decimal_dict(data)
        if isinstance(data, float):
            return "{:.2f}".format(data)
        if isinstance(data, str):
            try:
                data = "{:.2f}".format(float(data))
            except BaseException:
                pass
            return data
        if isinstance(data, Iterable):
            return type(data)([cls.format_decimal(k) for k in data])
        return data

    @staticmethod
    def format_time_ampm(time_or_datetime):
        if isinstance(time_or_datetime, datetime.datetime):
            h = int(time_or_datetime.strftime('%I'))
            ampm = time_or_datetime.strftime('%p').lower()
            if time_or_datetime.minute:
                m = time_or_datetime.strftime('%M')
                return "%s:%s%s" % (h, m, ampm)
            else:
                return "%s%s" % (h, ampm)
        elif isinstance(time_or_datetime, (tuple, list)) and len(time_or_datetime) >= 2:
            h = time_or_datetime[0]
            m = time_or_datetime[1]
            assert isinstance(h, int), type(h)
            assert isinstance(m, int), type(m)
            ampm = 'am'
            if h > 12:
                ampm = 'pm'
                h -= 12
            if m:
                return "%s:%s%s" % (h, m, ampm)
            else:
                return "%s%s" % (h, ampm)
        else:
            raise ValueError("Wrong parameter to this function")


class GenerateRandom(object):

    @staticmethod
    def generate_random_id() -> str:
        now = datetime.datetime.now().strftime("%Y%m%d")
        unix = str(time.time()).replace('.', "")[-10:]
        rand_ind = random.randint(1000, 9999)
        return ''.join([now[-6:], unix, str(rand_ind)])

    @staticmethod
    def generate_uuid() -> str:
        _uuid1 = str(uuid.uuid1())
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, _uuid1)).replace('-', '')

    @staticmethod
    def random_session_id():
        create_session_id = lambda: hashlib.sha1(
            bytes("{}{}".format(os.urandom(16), time.time()), encoding="utf-8")).hexdigest()
        return create_session_id()

    @staticmethod
    def random_string(length=10):
        return ''.join(choice(ascii_letters) for _ in range(length))

    @staticmethod
    def generate_random_color():
        def dec2hex(d):
            return "%02X" % d

        return '#%s%s%s' % (
            dec2hex(random.randint(0, 255)),
            dec2hex(random.randint(0, 255)),
            dec2hex(random.randint(0, 255)),
        )


class DealEncrypt(object):

    # base64加密
    @staticmethod
    def b64_encrypt(data: (str, bytes)) -> str:
        if isinstance(data, str):
            data = data.encode('utf-8')
        enb64_str = base64.b64encode(data)
        return enb64_str.decode('utf-8')

    # base64解密
    @staticmethod
    def b64_decrypt(data: str) -> str:
        deb64_str = base64.b64decode(data)
        return deb64_str.decode('utf-8')

    # base64对url加密
    @staticmethod
    def url_b64_encrypt(data: str) -> str:
        enb64_str = base64.urlsafe_b64encode(data.encode('utf-8'))
        return enb64_str.decode("utf-8")

    # base64对url解密
    @staticmethod
    def url_b64_decrypt(data: str) -> str:
        deb64_str = base64.urlsafe_b64decode(data)
        return deb64_str.decode("utf-8")

    # hashlib md5加密
    @staticmethod
    def hash_md5_encrypt(data: (str, bytes)) -> str:
        if isinstance(data, str):
            data = data.encode('utf-8')
        md5 = hashlib.md5()
        md5.update(Constant.ENCRYPT_KEY.encode('utf-8'))
        md5.update(data)
        return md5.hexdigest()

    # hashlib sha1加密
    @staticmethod
    def hash_sha1_encrypt(data: (str, bytes)) -> str:
        if isinstance(data, str):
            data = data.encode('utf-8')
        md5 = hashlib.sha1()
        md5.update(Constant.ENCRYPT_KEY.encode('utf-8'))
        md5.update(data)
        return md5.hexdigest()

    # hashlib sha256加密
    @staticmethod
    def hash_sha256_encrypt(data: (str, bytes)) -> str:
        if isinstance(data, str):
            data = data.encode('utf-8')
        md5 = hashlib.sha256()
        md5.update(Constant.ENCRYPT_KEY.encode('utf-8'))
        md5.update(data)
        return md5.hexdigest()

    # Crypto AES加密
    @staticmethod
    def crypto_encrypt(data: (str, bytes)) -> str:
        """
        data大于16位，返回64位字符；小于16位，返回32位字符
        :param data:
        :return:
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        cipher = AES.new(Constant.ENCRYPT_KEY.encode('utf8'), AES.MODE_ECB)
        msg = cipher.encrypt(pad(data, Constant.BLOCK_SIZE))
        return msg.hex()

    # Crypto AES解密
    @staticmethod
    def crypto_decrypt(data: str) -> str:
        decipher = AES.new(Constant.ENCRYPT_KEY.encode('utf8'), AES.MODE_ECB)
        msg_dec = decipher.decrypt(bytes.fromhex(data))
        return unpad(msg_dec, Constant.BLOCK_SIZE).decode()


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


from pprint import pprint

pprint(GenerateRandom.generate_random_color())
