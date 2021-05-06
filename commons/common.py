#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:21
# @Author  : Hanley
# @File    : common.py
# @Desc    : 公共方法文件

import asyncio
import base64
import configparser
import datetime
import fcntl
import filecmp
import functools
import hashlib
import json
import os
import pathlib
import random
import re
import time
import traceback
import uuid
from decimal import Decimal
from functools import wraps
from random import choice
from string import ascii_letters

import yaml
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from aiohttp import ClientSession, TCPConnector
from cryptography.fernet import Fernet
from requests import Session, adapters

from commons.constant import Constant
from commons.initlog import logging


def str_now(): return time.strftime("%Y-%m-%d %X")


def datetime_now(): return datetime.datetime.now()


def perf_time(): return time.perf_counter()


def cost_time(func):
    def _cost(func_name, start_time):
        end_time = perf_time()
        cost = (end_time - start_time) * 1000
        logging.debug(f">>>function: {func_name} duration: {cost}ms<<<")
        return

    if asyncio.iscoroutinefunction(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = perf_time()
            return_data = await func(*args, **kwargs)
            _cost(func.__name__, start_time)
            return return_data
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = perf_time()
            return_data = func(*args, **kwargs)
            _cost(func.__name__, start_time)
            return return_data
    return wrapper


def singleton(cls):
    _instance = {}

    @wraps(cls)
    def _singleton(*args, **kwargs):
        if cls not in _instance:
            _instance[cls] = cls(*args, **kwargs)
        return _instance[cls]

    return _singleton


def catch_exc(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(e)
            logging.error(traceback.format_exc())

    return wrapper


class Common(object):

    @staticmethod
    def yaml_config(key=None, file_path=Constant.YAML_CONFIG):
        with open(file_path, 'r') as f:
            config = yaml.safe_load(f)
        if key:
            return config.get(key)
        return config

    @staticmethod
    def ini_config(section=None, file_path=Constant.INI_PATH) -> dict:
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
        _mobile_pattern = r"13\d{9}|14\d{9}|15\d{9}|16\d{9}|17\d{9}|18\d{9}|19\d{9}"
        _landline_pattern = r"^[0][1-9]{2,3}-[0-9]{5,10}$"

        mobile_pattern = re.compile(_mobile_pattern)
        landline_pattern = re.compile(_landline_pattern)
        _check = lambda p: p.findall(phone_number)
        if len(phone_number) == 11 and "-" not in phone_number:
            return True if _check(mobile_pattern) else False
        else:
            return True if _check(landline_pattern) else False

    @staticmethod
    def decimal_dict(_dict: dict):
        for k in _dict:
            if isinstance(_dict[k], dict):
                Common.format_decimal(_dict[k])
            else:
                if isinstance(_dict[k], float):
                    _dict[k] = float(round(Decimal(_dict[k]), 2))
                elif isinstance(_dict[k], str):
                    if _dict[k].isdigit():
                        _dict[k] = float(round(Decimal(float(_dict[k])), 2))
                elif isinstance(_dict[k], list):
                    _dict[k] = list([Common.format_decimal(k) for k in _dict[k]])
                else:
                    continue
        return _dict

    @staticmethod
    def format_decimal(data):
        if isinstance(data, dict):
            return Common.decimal_dict(data)
        if isinstance(data, float):
            return float(round(Decimal(data), 2))
        if isinstance(data, str):
            if data.isdigit():
                return float(round(Decimal(float(data)), 2))
            else:
                return data
        if isinstance(data, list):
            return list(([Common.format_decimal(k) for k in data]))
        return data

    @staticmethod
    def cp_file(source_file, target_file):
        if filecmp.cmp(target_file, source_file):
            return
        with open(source_file, 'r') as sf:
            with open(target_file, 'w') as tf:
                fcntl.lockf(tf.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                while True:
                    data = sf.read(4069)
                    if not data:
                        break
                    tf.write(data)

    @staticmethod
    def init_config_file(env: str):
        """
        项目配置文件环境切换
        :param env:
        :return:
        """
        if env not in ("prod", "dev", "local"):
            return
        FILE_MAP = {
            'prod': 'config_prod.yaml',
            'dev': "config_dev.yaml",
            'local': 'config_local.yaml'
        }
        source_file = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__))), FILE_MAP.get(env))
        target_file = os.path.join(
            os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__))), 'config.yaml')
        not os.path.exists(target_file) and pathlib.Path(target_file).touch()

        Common.cp_file(source_file, target_file)

    @staticmethod
    def encode_multipart_formdata(fields, files):
        # 封装multipart/form-data post请求
        boundary = b'WebKitFormBoundaryh4QYhLJ34d60s2tD'
        boundary_u = boundary.decode('utf-8')
        crlf = b'\r\n'
        l = []
        for (key, value) in fields:
            l.append(b'--' + boundary)
            temp = 'Content-Disposition: form-data; name="%s"' % key
            l.append(temp.encode('utf-8'))
            l.append(b'')
            if isinstance(value, str):
                l.append(value.encode())
            else:
                l.append(value)
        key, filename, value = files
        l.append(b'--' + boundary)
        temp = 'Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename)
        l.append(temp.encode('utf-8'))
        temp = 'Content-Type: img/%s' % filename.split('.')[1]
        l.append(temp.encode('utf-8'))
        l.append(b'')
        l.append(value)
        l.append(b'--' + boundary + b'--')
        l.append(b'')
        body = crlf.join(l)
        content_type = 'multipart/form-data; boundary=%s' % boundary_u
        return content_type, body


class GenerateRandom(object):

    @staticmethod
    def generate_random_digit() -> str:
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


class Encrypt(object):

    @staticmethod
    def pad(s):
        AES_BLOCK_SIZE = 16  # Bytes
        return s + (AES_BLOCK_SIZE - len(s) % AES_BLOCK_SIZE) * \
               chr(AES_BLOCK_SIZE - len(s) % AES_BLOCK_SIZE)

    @staticmethod
    def unpad(s):
        return s[:-ord(s[len(s) - 1:])]

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
    def hash_md5_encrypt(data: (str, bytes), salt=None) -> str:
        if isinstance(data, str):
            data = data.encode('utf-8')
        md5 = hashlib.md5()
        if salt:
            if isinstance(salt, str):
                salt = salt.encode('utf-8')
            md5.update(salt)
        md5.update(data)
        return md5.hexdigest()

    # hashlib sha1加密
    @staticmethod
    def hash_sha1_encrypt(data: (str, bytes), salt=None) -> str:
        if isinstance(data, str):
            data = data.encode('utf-8')
        md5 = hashlib.sha1()
        if salt:
            if isinstance(salt, str):
                salt = salt.encode('utf-8')
            md5.update(salt)
        md5.update(data)
        return md5.hexdigest()

    # hashlib sha256加密
    @staticmethod
    def hash_sha256_encrypt(data: (str, bytes), salt=None) -> str:
        if isinstance(data, str):
            data = data.encode('utf-8')
        md5 = hashlib.sha256()
        if salt:
            if isinstance(salt, str):
                salt = salt.encode('utf-8')
            md5.update(salt)
        md5.update(data)
        return md5.hexdigest()

    @staticmethod
    def generate_secret(block_size=16):
        return base64.encodebytes(
            get_random_bytes(
                block_size)).strip().decode()

    @staticmethod
    def generate_fernet_key():
        return Fernet.generate_key()

    @staticmethod
    def build_sign(dict_param: dict) -> str:
        """
        生成字典参数签名
        """
        param_list = sorted(dict_param.keys())
        string = ""
        for param in param_list:
            if dict_param[param]:
                string += f"{param}={dict_param[param]}&"
        md5_sign = Encrypt.hash_md5_encrypt(string)
        return md5_sign.upper()

    @staticmethod
    @catch_exc
    def aes_encrypt(key, data):
        '''
        AES的ECB模式加密方法
        :param key: 密钥
        :param data:被加密字符串（明文）
        :return:密文
        '''
        key = key.encode('utf8')
        # 字符串补位
        data = Encrypt.pad(data)
        cipher = AES.new(key, AES.MODE_ECB)
        # 加密后得到的是bytes类型的数据，使用Base64进行编码,返回byte字符串
        result = cipher.encrypt(data.encode())
        encodestrs = base64.b64encode(result)
        enctext = encodestrs.decode('utf8')
        return enctext

    @staticmethod
    @catch_exc
    def aes_decrypt(key, data):
        '''
        :param key: 密钥
        :param data: 加密后的数据（密文）
        :return:明文
        '''
        key = key.encode('utf8')
        data = base64.b64decode(data)
        cipher = AES.new(key, AES.MODE_ECB)
        # 去补位
        text_decrypted = Encrypt.unpad(cipher.decrypt(data))
        text_decrypted = text_decrypted.decode('utf8')
        return text_decrypted

    @staticmethod
    @catch_exc
    def set_auth_cookies(key, data):
        '''
        加密cookies
        :param token:
        :param cookies:
        :return:
        '''
        f = Fernet(key)
        cookies_json = json.dumps(data)
        token = f.encrypt(cookies_json.encode())
        cookies_json = token.decode()
        return cookies_json

    @staticmethod
    @catch_exc
    def get_auth_cookies(key, data):
        '''
        解密cookies
        :param token:
        :param cookies:
        :return:
        '''
        f = Fernet(key)
        cookie_json = f.decrypt(data.encode()).decode()
        cookies_data = json.loads(cookie_json)
        return cookies_data


class SyncClientSession(Session):

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(SyncClientSession, cls).__new__(cls)
        return cls._instance

    def __init__(self, time_out=2, pool_num=10, pool_max_size=50, max_retries=3):
        super(SyncClientSession, self).__init__()
        self._time_out = time_out
        self._pool_num = pool_num
        self._pool_max_size = pool_max_size
        self._max_retries = max_retries
        self.mount("http://", adapters.HTTPAdapter(
            pool_connections=self._pool_num,
            pool_maxsize=self._pool_max_size,
            max_retries=self._max_retries
        ))
        self.mount("https://", adapters.HTTPAdapter(
            pool_connections=self._pool_num,
            pool_maxsize=self._pool_max_size,
            max_retries=self._max_retries
        ))

    def request(self, method, url, headers=None, timeout=None, **kwargs):
        timeout = timeout or self._time_out
        headers = headers or {}
        if not headers.get("X-Request-ID"):
            headers["X-Request-ID"] = uuid.uuid4().hex
        return super().request(
            method, url, headers=headers, timeout=timeout, **kwargs)


class AsyncClientSession:
    """
    async aiohttp client
    """
    __slots__ = (
        "session",
    )

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(AsyncClientSession, cls).__new__(cls)
        return cls._instance

    async def init_session(self) -> ClientSession:
        tcp_connector = TCPConnector(
            keepalive_timeout=15,
            limit=600,
            limit_per_host=300,
        )
        self.session = ClientSession(connector=tcp_connector)
        return self.session

    async def request(self, method, url, **kwargs):
        return await self.session.request(method, url, **kwargs)

    @cost_time
    async def fetch_json(self, method, url, **kwargs):
        async with self.session.request(method, url, **kwargs) as response:
            return await response.json()

    async def close(self):
        await self.session.close()
