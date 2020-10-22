#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/10/22 上午11:25
# @Author  : Hanley
# @File    : msg_util.py
# @Desc    : 

import traceback

import jpush

from commons.common import Common, singleton
from commons.initlog import logging


@singleton
class JGMessagePush(object):

    def __init__(self):
        _config = Common.get_config_value("jpush-service")
        self.app_key = _config["app_key"].encode('utf-8')
        self.master_secret = _config["master_secret"].encode('utf-8')
        _jpush = jpush.JPush(self.app_key, self.master_secret, timeout=30, zone="BJ")
        _jpush.set_logging("DEBUG")
        self.push = _jpush.create_push()

    async def message_push(self, jpushid, message, platform, extras=None):

        self.push.audience = {"registration_id": [jpushid]}
        if platform == "ios":
            _ios = jpush.ios(message, extras=extras)
            self.push.notification = jpush.notification(message, ios=_ios)
        elif platform == "android":
            _android = jpush.android(message, extras=extras)
            self.push.notification = jpush.notification(message, android=_android)
        self.push.platform = jpush.all_

        # _options = {
        #     "apns_production": False
        # }
        # self.push.options = _options
        try:
            res = self.push.send()
        except BaseException:
            logging.error(traceback.format_exc())
        else:
            logging.debug("message push response: {}".format(res.payload))

    def alias_push(self, yc_id, message, platform, extras=None):
        self.push.audience = {"alias": [yc_id]}
        if platform == "ios":
            _ios = jpush.ios(alert=message, extras=extras)
            self.push.notification = jpush.notification(message, ios=_ios)
        elif platform == "android":
            _android = jpush.android(alert=message, extras=extras)
            self.push.notification = jpush.notification(message, android=_android)
        self.push.platform = platform
        _options = {
            "apns_production": False
        }
        self.push.options = _options
        self.push.send()
