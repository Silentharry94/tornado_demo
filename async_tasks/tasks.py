from __future__ import absolute_import, unicode_literals

from celery import Task
from playhouse.pool import PooledMySQLDatabase
from pymongo import MongoClient
from redis.client import Redis

from commons.initlog import celery_log as logging
from commons.common import Common, SyncClientSession
from utils.sync_db import MongodbConnect, RedisConnect, MysqlConnect


class MyTask(Task):

    def on_success(self, retval, task_id, args, kwargs):
        return super(MyTask, self).on_success(retval, task_id, args, kwargs)

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        logging.debug('task fail, reason: {0}, task_id - {1}, '
                      'args - {2}, kwargs - {3}, einfo - {4}'.format(
            exc, task_id, args, kwargs, einfo))
        return super(MyTask, self).on_failure(exc, task_id, args, kwargs, einfo)

    @property
    def mongo(self) -> MongoClient:
        mongo_config = Common.yaml_config("mongo")
        return MongodbConnect(mongo_config).client

    @property
    def redis(self) -> Redis:
        redis_config = Common.yaml_config("redis")
        return RedisConnect(redis_config).client

    @property
    def mysql(self) -> PooledMySQLDatabase:
        mysql_config = Common.yaml_config("mysql")
        return MysqlConnect.init_db(mysql_config)

    @property
    def client(self) -> SyncClientSession:
        return SyncClientSession()
