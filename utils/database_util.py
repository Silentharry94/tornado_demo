#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2019/12/19 下午4:25
# @Author  : Hanley
# @File    : database_util.py
# @Desc    : 数据库连接基础文件

import time
import traceback
from urllib.parse import quote_plus

import pymongo
import redis
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin

from commons.common import Common, DealEncrypt, Singleton
from commons.initlog import logging


@Singleton
class MongodbConnect(object):

    def __init__(self):
        config = Common.get_config_value("mongodb")
        self.host = config["host"]
        self.port = config["port"]
        self.auth_db = config.get("auth_db", None)
        self.user = config.get("user", None)
        if config.get("password", None):
            self.password = DealEncrypt.crypto_decrypt(config["password"])
        else:
            self.password = None
        self.database = config.get("database", None)
        self.client = self.connect_mongodb()

    def connect_mongodb(self):

        url = "mongodb://"
        domain = "{host}:{port}/".format(
            host=self.host, port=self.port
        )

        if self.user and self.password and self.auth_db:
            authentication = "{username}:{password}@".format(
                username=quote_plus(self.user),
                password=quote_plus(self.password)
            )
            domain = "{host}:{port}/".format(
                host=self.host,
                port=self.port
            )
            param = "?authSource={auth_db}".format(
                auth_db=self.auth_db
            )
            url = "".join([url, authentication, domain, param])
        else:
            url = "".join([url, domain])

        client = pymongo.MongoClient(url, serverSelectionTimeoutMS=5000)
        host, port = client.address
        logging.debug("success connect mongodb: "
                      "{}:{}".format(host, port))

        return client[self.database] if self.database is not None else client


class RetryConnectMysql(ReconnectMixin, PooledMySQLDatabase):
    _instance = None

    @staticmethod
    def connect_mysql():
        if not RetryConnectMysql._instance:
            config = Common.get_config_value("mysql")
            RetryConnectMysql._instance = RetryConnectMysql(
                database=config["database"],
                max_connections=int(config['max_connections']),
                stale_timeout=int(config['timeout']),
                host=config['host'],
                user=config['user'],
                password=DealEncrypt.crypto_decrypt(config["password"]),
                port=int(config['port'])
            )
            logging.debug("success connect mysql: "
                          "{}:{}".format(config["host"], config["port"]))

        return RetryConnectMysql._instance


@Singleton
class RedisConnect():

    def __init__(self):
        config_dict = Common.get_config_value('redis')
        self.host = config_dict["host"]
        self.port = int(config_dict["port"])
        self.db = config_dict['db']
        self.retry = int(config_dict["retry"])
        self.client = self.connect_redis()

    def connect_redis(self):

        r, i = None, 0

        while i < self.retry:
            try:
                pool = redis.ConnectionPool(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    decode_responses=True
                )
                r = redis.Redis(connection_pool=pool, decode_responses=True)
                if not r:
                    logging.debug("第[%d]连接失败，继续" % i)
                else:
                    logging.debug("success connect redis: {}", format(r))
                    break
            except BaseException:
                logging.error(traceback.format_exc())
                time.sleep(1)
            i += 1

        return r
