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
import math
import random
import time
import uuid
from functools import wraps

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from commons.constant import Constant


def Singleton(cls):
    _instance = {}

    @wraps(cls)
    def _singlenton(*args, **kargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kargs)
        return _instance[cls]

    return _singlenton


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
    def generate_random_id() -> str:
        now = datetime.datetime.now().strftime("%Y%m%d")
        unix = str(math.ceil(time.time()))
        rand_ind = random.randint(100000, 999999)
        return ''.join([str(rand_ind), unix[2:10], now[-6:]])

    @staticmethod
    def generate_uuid() -> str:
        _uuid1 = str(uuid.uuid1())
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, _uuid1)).replace('-', '')

    @staticmethod
    def format_datetime(data):
        if isinstance(data, datetime.datetime):
            return data.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(data, datetime.date):
            return data.strftime("%Y-%m-%d")
        else:
            return data


class DealEncrypt(object):

    # base64加密
    @staticmethod
    def b64_encrypt(data: str) -> str:
        enb64_str = base64.b64encode(data.encode('utf-8'))
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
    def hash_md5_encrypt(data: str) -> str:
        md5 = hashlib.md5()
        md5.update(Constant.ENCRYPT_KEY.encode('utf-8'))
        md5.update(data.encode('utf-8'))
        return md5.hexdigest()

    # hashlib sha1加密
    @staticmethod
    def hash_sha1_encrypt(data: str) -> str:
        md5 = hashlib.sha1()
        md5.update(Constant.ENCRYPT_KEY.encode('utf-8'))
        md5.update(data.encode('utf-8'))
        return md5.hexdigest()

    # hashlib sha256加密
    @staticmethod
    def hash_sha256_encrypt(data: str) -> str:
        md5 = hashlib.sha256()
        md5.update(Constant.ENCRYPT_KEY.encode('utf-8'))
        md5.update(data.encode('utf-8'))
        return md5.hexdigest()

    # Crypto AES加密
    @staticmethod
    def crypto_encrypt(data: str) -> str:
        cipher = AES.new(Constant.ENCRYPT_KEY.encode('utf8'), AES.MODE_ECB)
        msg = cipher.encrypt(pad(data.encode('utf-8'), Constant.BLOCK_SIZE))
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

# if __name__ == '__main__':
#     # 加密请执行此处
#     a = DealEncrypt.crypto_encrypt("aa123456")
#     print(a)
#     b = DealEncrypt.crypto_decrypt(a)
#     print(b)
