#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/10/22 上午11:17
# @Author  : Hanley
# @File    : 3party_pay.py
# @Desc    : 

import base64
import configparser
import datetime
import hashlib
import os
import time
import urllib
import uuid
from urllib.parse import urlencode

import rsa
import ujson
import xmltodict
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

from commons.constant import Constant
from commons.initlog import logging
from utils.database_util import RedisConnect

# key = base64.encodebytes(get_random_bytes(16)).strip().decode()
config = configparser.ConfigParser()


class FuncBase(object):

    def get_config_value(self, section=None, file_path=Constant.INI_PATH) -> dict:

        config.read(file_path)
        if isinstance(section, str):
            section = section.lower()
        options = config.options(section)
        dict_result = {}
        for option in options:
            temp = config.get(section, option)
            dict_result.update({option: temp})
        return dict_result

    def dict2xml(self, dict_data, root="xml"):
        """
        字典转xml
        dict_data: 字典数据
        root：根结点标签
        """
        _dictXml = {root: dict_data}
        xmlstr = xmltodict.unparse(_dictXml, pretty=True)
        return xmlstr

    def xml2dict(self, xml_data):
        """
        xml转dict
        xml_data: xml字符串
        return: dict字符串
        """
        data = xmltodict.parse(xml_data, process_namespaces=True)
        return dict(list(data.values())[0])

    def build_sign(self, dict_param, key):
        """
        生成签名
        """
        paramList = sorted(dict_param.keys())
        stringA = ""
        for param in paramList:
            if dict_param[param]:
                stringA += "%s=%s&" % (param, dict_param[param])
        stringSign = "%skey=%s" % (stringA, key)
        md5Sign = self.hash_md5_encrypt(stringSign)
        return md5Sign.upper()

    def build_time(self, minutes=0):
        now = datetime.datetime.now()
        if minutes > 0:
            delta = datetime.timedelta(minutes=minutes)
            now += delta
        return now.strftime('%Y%m%d%H%M%S')

    def generate_uuid(self) -> str:
        _uuid1 = str(uuid.uuid1())
        return str(uuid.uuid3(uuid.NAMESPACE_DNS, _uuid1)).replace('-', '')

    def build_out_trade_no(self, salt):
        return self.hash_md5_encrypt(self.generate_uuid(), salt)

    def hash_md5_encrypt(self, data: (str, bytes), salt=None) -> str:
        if isinstance(data, str):
            data = data.encode('utf-8')
        md5 = hashlib.md5()
        if salt:
            md5.update(salt.encode('utf-8'))
        md5.update(data)
        return md5.hexdigest()

    def crypto_encrypt(self, data: (str, bytes)) -> str:
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

    def crypto_decrypt(self, data: str) -> str:
        decipher = AES.new(Constant.ENCRYPT_KEY.encode('utf8'), AES.MODE_ECB)
        msg_dec = decipher.decrypt(bytes.fromhex(data))
        return unpad(msg_dec, Constant.BLOCK_SIZE).decode()


# 微信统一支付
class UnifiedFetch(FuncBase):
    req_url = "https://api.mch.weixin.qq.com/pay/unifiedorder"

    def __init__(self, amount, notify_url, attach, body="", **kwargs):
        super(UnifiedFetch, self).__init__()
        self.config = self.get_config_value('wx-pay')
        self.amount = amount
        self.notify_url = notify_url
        self.attach = attach
        self.body = body if body else self.config["body"]
        self.kwargs = kwargs
        self.redis = RedisConnect().client

    def xml_request(self, trade_type, **kwargs):
        """
        attach: 自定义数据,回调中返回
        sign_type: 默认MD5
        detail: 商品详情
        fee_type: 货币类型 默认CNY
        receipt: Y是否开票
        appid：应用ID
        mch_id：商户号ID
        nonce_str：加密串
        sign：参数hash
        body：商品描述-标题
        out_trade_no：订单号
        total_fee：总金额(分)
        spbill_create_ip：终端IP
        """
        param = {
            "total_fee": int(self.amount),
            "notify_url": self.notify_url,
            "body": self.body,
            "attach": self.attach,
            "out_trade_no": self.build_out_trade_no(self.config["channel"]),
            "time_start": self.build_time(int(self.config["expire_time"])),
            "time_expire": self.build_time(int(self.config["expire_time"])),
            "appid": self.config["appid"],
            "mch_id": self.config["mch_id"],
            "nonce_str": self.config["nonce_str"],
            "device_info": "WEB",
            "trade_type": trade_type,
        }
        if trade_type == "NATIVE":
            product_id = self.generate_uuid()
            param["product_id"] = product_id
        if trade_type == "JSAPI":
            param["openid"] = kwargs["openid"]
        param.update({"sign": self.build_sign(param, self.config["secret"])})
        logging.debug(f"request param: {param}")

        param = self.dict2xml(param)
        logging.debug(f"xml param: {param}")
        req = HTTPRequest(self.req_url, method="POST", body=param, validate_cert=False, request_timeout=10)
        return req

    async def refresh_public_access_token(self, refresh_token):
        """
        doc:https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/Wechat_webpage_authorization.html#0
        刷新微信公众号access_token
        """
        logging.debug(f"start refresh wechat public access token.")
        wechatConfig = self.get_config_value('wechat-api')
        wechatApiHost = "https://api.weixin.qq.com"
        uri = "/sns/oauth2/refresh_token?"
        params = {
            "appid": wechatConfig["appid"],
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        url = "".join([wechatApiHost, uri, urlencode(params)])
        request_obj = HTTPRequest(
            url=url,
            request_timeout=Constant.TIME_OUT
        )
        result = await AsyncHTTPClient().fetch(request_obj)
        result = ujson.loads(result.body)
        logging.debug("wechat refresh public token: {}".format(result))
        if "access_token" not in result:
            return
        return result

    async def get_public_access_token(self, code):
        """
        doc:https://developers.weixin.qq.com/doc/offiaccount/OA_Web_Apps/Wechat_webpage_authorization.html#0
        获取微信公众号access_token和openid
        """
        # rkey = "&".join([RedisKey.WECHAT_PUB_OPEN_ID, uid])
        # if self.redis.get(rkey):
        #     return ujson.loads(self.redis.get(rkey))
        logging.debug(f"start get wechat public access token.")
        wechatConfig = self.get_config_value('wechat-api')
        wechatApiHost = "https://api.weixin.qq.com"
        uri = "/sns/oauth2/access_token?"
        params = {
            "appid": wechatConfig["appid"],
            "secret": wechatConfig["appsecret"],
            "code": code,
            "grant_type": "authorization_code"
        }
        url = "".join([wechatApiHost, uri, urlencode(params)])
        request_obj = HTTPRequest(
            url=url,
            request_timeout=Constant.TIME_OUT
        )
        result = await AsyncHTTPClient().fetch(request_obj)
        result = ujson.loads(result.body)
        logging.debug("wechat public token: {}".format(result))
        if "access_token" not in result:
            return
        # self.redis.set(rkey, ujson.dumps(result), ex=RedisKey.WECHAT_PUB_OPEN_ID_EXPIRE)
        return result

    async def get_mini_open_id(self, js_code):
        """
        doc: https://developers.weixin.qq.com/miniprogram/dev/api-backend/open-api/login/auth.code2Session.html
        获取小程序用户open_id
        """
        wechatApiHost = "https://api.weixin.qq.com"
        uri = "/sns/jscode2session?"
        wechatConfig = self.get_config_value('wechat-api')
        params = {
            "appid": wechatConfig["appid"],
            "secret": wechatConfig["appsecret"],
            "js_code": js_code,
            "grant_type": "authorization_code"
        }
        url = "".join([wechatApiHost, uri, urlencode(params)])
        request_obj = HTTPRequest(
            url=url,
            request_timeout=Constant.TIME_OUT
        )
        response = await AsyncHTTPClient().fetch(request_obj)
        response = ujson.loads(response.body)
        logging.debug("wechat get open_id: {}".format(response))
        if response.get("errcode") != 0:
            return
        return response["openid"]

    async def app_fetch(self):
        req = self.xml_request("APP")
        response = await AsyncHTTPClient().fetch(req)
        res = self.xml2dict(response.body)
        logging.debug(f"app request response: {res}")
        if res.get("return_code") == "SUCCESS":
            result = {
                "appid": res["appid"],
                "partnerid": res["mch_id"],
                "prepayid": res["prepay_id"],
                "package": "Sign=WXPay",
                "noncestr": res["nonce_str"],
                "timestamp": int(time.time()),
            }
            result["sign"] = self.build_sign(result, self.config["secret"])
        else:
            return
        logging.debug(f"app_fetch result: {result}")
        return result

    async def web_fetch(self):
        req = self.xml_request("NATIVE")
        response = await AsyncHTTPClient().fetch(req)
        result = self.xml2dict(response.body)
        logging.debug(f"web request response: {result}")
        if result.get("return_code") != 'SUCCESS':
            return
        return result

    async def mini_fetch(self, public_code=None):
        public_data = await self.get_public_access_token(public_code)
        if not public_data:
            return
        openid = public_data["openid"]
        kwargs = {"openid": openid}
        req = self.xml_request("JSAPI", **kwargs)
        response = await AsyncHTTPClient().fetch(req)
        result = self.xml2dict(response.body)
        logging.debug(f"mini request response: {result}")
        if result.get("return_code") != 'SUCCESS':
            return
        return result


# 苹果内购
class ApplyPay(FuncBase):

    def __init__(self, order_id):
        config = self.get_config_value("apply-service")
        self.url = config["url"]
        self.order_id = order_id

    async def check_status(self):
        param = {
            "receipt-data": self.order_id
        }
        request_obj = HTTPRequest(
            url=self.url,
            method="POST",
            headers=Constant.JSON_HEADERS,
            body=ujson.dumps(param),
            request_timeout=Constant.TIME_OUT
        )
        result = await AsyncHTTPClient().fetch(request_obj)
        result = ujson.loads(result.body)
        logging.debug(f"apply pay result: {result}")
        if result.get("status") == 0 or result.get("status") == 21007:
            return 1, ""
        else:
            return result.get("status", 0), Constant.APPLY_STATUS.get(result.get("status", 0))


# 支付宝支付
class AliPay(FuncBase):

    def __init__(self, amount, notify_url, passback_params, body="", **kwargs):
        self.config = self.get_config_value("alipay-service")
        self.amount = amount
        self.notify_url = notify_url
        self.passback_params = passback_params
        self.body = body if body else self.config["body"]

    async def app_pay(self):
        """
           构造唤起支付宝客户端支付时传递的请求串示例：alipay.trade.app.pay
        """

        return self.build_request("alipay.trade.app.pay")

    def build_request(self, method, **kwargs):
        """
        构建支付请求
        """
        # 组织请求参数
        post_data = {
            "app_id": self.config["app_id"],
            "notify_url": self.notify_url,
            "sign_type": self.config["sign_type"],
            "charset": self.config["charset"],
            "version": self.config["version"],
            "format": self.config["format"],
            "method": method
        }

        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        biz_content = {
            "body": self.config["body"],
            "subject": self.config["subject"],
            "out_trade_no": self.build_out_trade_no(self.config["channel"]),
            "total_amount": self.amount,
            "passback_params": self.passback_params,
            "timeout_express": "10m",
        }
        # 在支付二维码请求中，product_code 参数是不存在的
        # if method == "": biz_content["product_code"] = kwargs["product_code"]
        post_data["timestamp"] = timestamp
        post_data["biz_content"] = ujson.dumps(biz_content)

        # 获取sign
        post_data_string = self.build_sign_str(post_data)
        logging.info(f'build_sign_str: {post_data_string}')
        sign_str = self.sign_param(post_data_string.encode())
        logging.info(f'sign_param:{sign_str}')

        # 获取encode的string
        encode_data_string = self.build_encode_str(post_data)

        # 对签名进行组合
        encode_data_string += "&sign={}".format(urllib.parse.quote(sign_str, self.config["charset"]))
        logging.info(f'final string: {encode_data_string}')
        return encode_data_string

    def build_sign_str(self, param_dic):
        """
        生成签名
        """
        string_list = []
        for key in sorted(param_dic.keys()):
            if param_dic[key]:
                # 只操作非空的k,v
                string_list.append("%s=%s" % (key, param_dic[key]))
        stringSign = "&".join(string_list)
        return stringSign

    def build_encode_str(self, param_dic):
        """
        生成签名
        """
        string_list = []
        for key in sorted(param_dic.keys()):
            if param_dic[key]:
                # 只操作非空的k,v
                string_list.append("%s=%s" % (key, urllib.parse.quote(param_dic[key], self.config["charset"])))
        stringSign = "&".join(string_list)
        return stringSign

    def sign_param(self, sign_str, signtype="priv", en_type="SHA-256"):
        """
        为参数做签名
        en_type: MD5	360
              SHA-1	368
              SHA-256	496
              SHA-384	624
              SHA-512	752
        sign_str: 待加密字符串
        signtype: priv:使用私钥  pub: 使用公钥
        """
        if signtype == "priv":
            signkey = self.get_privkey()
        else:
            signkey = self.get_pubkey()
        sign_str = rsa.sign(sign_str, signkey, en_type)
        return base64.b64encode(sign_str)

    def get_privkey(self):
        """
        获取私钥
        """
        path = '{}/utils/rsa_private_key.pem'.format(os.getcwd())
        with open(path, mode='r') as privatefile:
            keydata = privatefile.read().encode()
        privkey = rsa.PrivateKey.load_pkcs1(keydata)
        return privkey

    def get_pubkey(self):
        """
        获取公钥
        rsa.PublicKey.:
            load_pkcs1() ---- file start with -----BEGIN RSA PRIVATE KEY-----
            load_pkcs1_openssl_pem(): file start with —–BEGIN PUBLIC KEY—–
        """
        path = '{}/utils/rsa_public_key.pem'.format(os.getcwd())
        with open(path, mode='r') as pubfile:
            keydata = pubfile.read().encode()
        pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(keydata)
        return pubkey
