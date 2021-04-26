#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/12/25 上午11:54
# @Author  : Hanley
# @File    : async_db.py
# @Desc    : 异步数据库连接类
import aioredis
from aioredis import Redis
from motor.motor_asyncio import AsyncIOMotorClient
from peewee import InterfaceError, OperationalError, DoesNotExist
from peewee_async import Manager
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin

from commons.initlog import logging


class AsyncMongodbConnect:
    """
    motor多连接
    peer_conn = host + port + user
    """
    __conn = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(AsyncMongodbConnect, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: dict):
        self.config = config
        self.init_db()

    def init_db(self):
        config_client = {}
        self.peer_conn = "_".join([
            self.config["host"], str(self.config["port"]), self.config["user"]])
        if not self.__conn.get(self.peer_conn):
            self.config = self.config
            self.client = AsyncIOMotorClient(**self.config)
            config_client.setdefault("config", self.config)
            config_client.setdefault("client", self.client)
            self.__conn.setdefault(self.peer_conn, config_client)
        else:
            self.client = self.__conn[self.peer_conn]["client"]
            self.config = self.__conn[self.peer_conn]["config"]


class AsyncMySQLConnect(ReconnectMixin, PooledMySQLDatabase):
    """
    异步MySQL连接
    peer_conn: pid + host + port + database
    """
    __conn = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(AsyncMySQLConnect, cls).__new__(cls)
        return cls._instance

    reconnect_errors = (
        (OperationalError, '2006'),  # MySQL server has gone away.
        (OperationalError, '2013'),  # Lost connection to MySQL server.
        (OperationalError, '2014'),  # Commands out of sync.
        # mysql-connector raises a slightly different error when an idle
        # connection is terminated by the server. This is equivalent to 2013.
        (OperationalError, 'MySQL Connection not available.'),
        (OperationalError, 'Attempting to close database while '
                           'transaction is open.'),
        # mysql-connector might closed.
        (InterfaceError, '0')
    )

    @staticmethod
    def init_db(config: dict) -> PooledMySQLDatabase:
        peer_conn = "_".join([
            config["host"], str(config["port"]), config["database"]])
        if not AsyncMySQLConnect.__conn.get(peer_conn):
            _database = PooledMySQLDatabase(
                database=config["database"],
                max_connections=config['max_connections'],
                host=config['host'],
                user=config['user'],
                password=config["password"],
                port=config['port']
            )
            AsyncMySQLConnect.__conn[peer_conn] = _database
        return AsyncMySQLConnect.__conn[peer_conn]

    def execute_sql(self, sql, params=None, commit=True):
        self._reconnect_errors = {}
        for exc_class, err_fragment in self.reconnect_errors:
            self._reconnect_errors.setdefault(exc_class, [])
            self._reconnect_errors[exc_class].append(err_fragment.lower())
        try:
            return super(AsyncMySQLConnect, self).execute_sql(sql, params, commit)
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

            return super(AsyncMySQLConnect, self).execute_sql(sql, params, commit)


class AsyncManager(Manager):
    """
    peewee_async高级API
    """

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(AsyncManager, cls).__new__(cls)
        return cls._instance

    async def get_or_none(self, source_, *args, **kwargs):
        try:
            return await self.get(source_, *args, **kwargs)
        except DoesNotExist:
            return


class AsyncRedis:
    """
    异步Redis连接
    peer_conn: address + db
    """
    __conn = {}

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            cls._instance = super(AsyncRedis, cls).__new__(cls)
        return cls._instance

    def __init__(self, config: dict):
        self.config = config

    async def init_db(self) -> Redis:
        peer_conn = "_".join([
            self.config["address"], str(self.config["db"])])
        if self.__conn.get(peer_conn):
            self.client = self.__conn[peer_conn]
        else:
            redis_pool = await aioredis.create_redis_pool(**self.config)
            self.__conn[peer_conn] = redis_pool
        return self.__conn[peer_conn]
