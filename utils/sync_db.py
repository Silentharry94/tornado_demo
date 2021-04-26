#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/9/15 上午11:24
# @Author  : Hanley
# @File    : sync_db.py
# @Desc    : 

import time
import traceback
from urllib.parse import quote_plus

import pymongo
import redis
from peewee import InterfaceError, OperationalError
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin

from commons.initlog import logging


class MongodbConnect:
    __slots__ = (
        "config",
        "client",
    )
    __conn = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(MongodbConnect, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: dict):
        self.config = config
        self.init_db()

    def init_db(self):
        host = self.config["host"]
        port = self.config["port"]
        user = self.config["user"]
        password = self.config["password"]
        auth_db = self.config["auth_db"]

        peer_conn = "_".join([host, str(port)])
        if user:
            peer_conn += "_" + user
        if self.__conn.get(peer_conn):
            self.client = self.__conn[peer_conn]
            return self.client

        url = "mongodb://"
        domain = "{host}:{port}/".format(
            host=host, port=port
        )
        if user and password and auth_db:
            authentication = "{username}:{password}@".format(
                username=quote_plus(user),
                password=quote_plus(password)
            )
            domain = "{host}:{port}/".format(
                host=host,
                port=port
            )
            param = "?authSource={auth_db}".format(
                auth_db=auth_db
            )
            url = "".join([url, authentication, domain, param])
        else:
            url = "".join([url, domain])

        self.client = pymongo.MongoClient(url, serverSelectionTimeoutMS=5000)
        logging.debug(f"mongodb connect successful")


class MysqlConnect(ReconnectMixin, PooledMySQLDatabase):
    __conn = {}
    reconnect_errors = (
        # Error class, error message fragment (or empty string for all).
        (OperationalError, '2006'),  # MySQL server has gone away.
        (OperationalError, '2013'),  # Lost connection to MySQL server.
        (OperationalError, '2014'),  # Commands out of sync.

        # mysql-connector raises a slightly different error when an idle
        # connection is terminated by the server. This is equivalent to 2013.
        (OperationalError, 'MySQL Connection not available.'),
        # mysql-connector might closed.
        (InterfaceError, '0')
    )

    @staticmethod
    def init_db(config: dict) -> PooledMySQLDatabase:
        peer_db = "_".join([
            config["host"], str(config["port"]), config["database"]])
        if not MysqlConnect.__conn.get(peer_db):
            MysqlConnect.__conn[peer_db] = MysqlConnect(
                database=config["database"],
                max_connections=config['max_connections'],
                stale_timeout=config['timeout'],
                timeout=config['timeout'],
                host=config['host'],
                user=config['user'],
                password=config["password"],
                port=config['port']
            )
        return MysqlConnect.__conn[peer_db]

    def execute_sql(self, sql, params=None, commit=True):
        self._reconnect_errors = {}
        for exc_class, err_fragment in self.reconnect_errors:
            self._reconnect_errors.setdefault(exc_class, [])
            self._reconnect_errors[exc_class].append(err_fragment.lower())
        try:
            return super(MysqlConnect, self).execute_sql(sql, params, commit)
        except Exception as exc:
            exc_class = type(exc)
            if exc_class not in self._reconnect_errors:
                raise exc

            exc_repr = str(exc).lower()
            for err_fragment in self._reconnect_errors[exc_class]:
                if err_fragment in exc_repr:
                    break
            else:
                raise exc
            if not self.is_closed():
                logging.warning(f"will retry connect mysql")
                self.close()
                self.connect()

            return super(MysqlConnect, self).execute_sql(sql, params, commit)


class RedisConnect:
    __slots__ = (
        "config",
        "client"
    )
    __conn = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(RedisConnect, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: dict):
        self.config = config
        self.init_db()

    def init_db(self):
        peer_db = "_".join([
            self.config["host"], str(self.config["port"]), str(self.config["db"])])
        if self.__conn.get(peer_db):
            self.client = self.__conn[peer_db]
            return self.client
        retry = self.config.pop("retry")
        self.client, i = None, 0
        while i < retry:
            try:
                pool = redis.ConnectionPool(**self.config)
                self.client = redis.Redis(connection_pool=pool)
                if self.client:
                    logging.debug(f"redis connect successful")
                    break
                else:
                    logging.warning("第[%d]连接失败，继续" % i)
            except BaseException:
                logging.error(traceback.format_exc())
                time.sleep(1)
            i += 1
        self.__conn[peer_db] = self.client
        return self.client
