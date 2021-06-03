#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/6/2 2:10 下午
# @Author  : Hanley
# @File    : kafka_producer.py
# @Desc    :

from functools import partial

import ujson
from kafka import KafkaProducer

from commons.common import singleton, Common
from commons.initlog import logging


def rr_select(N):
    last = N - 1
    while True:
        current = (last + 1) % N
        last = current
        yield current


@singleton
class KafkaEntryPoint():
    LOG_TOPIC = "partsbond_log"
    _init_flag = False

    def __init__(self):
        if not self._init_flag:
            self.init()

    def init(self):
        self.producer = self.make_producer()
        self.partitions = list(self.producer.partitions_for(self.LOG_TOPIC))
        self.partition_selector = rr_select(len(self.partitions))
        self._init_flag = True

    def make_producer(self):
        kafka_config = Common.yaml_config("kafka_cluster")
        connect_config = {}
        connect_config["key_serializer"] = lambda v: ujson.dumps(v).encode('utf-8')
        connect_config["value_serializer"] = lambda v: ujson.dumps(v).encode('utf-8')
        connect_config["max_block_ms"] = 15000
        if all([kafka_config["sasl_plain_username"], kafka_config["sasl_plain_password"]]):
            connect_config.update(kafka_config)
        else:
            connect_config.update(bootstrap_servers=kafka_config["bootstrap_servers"])
        while True:
            producer = KafkaProducer(**connect_config)
            if not producer.bootstrap_connected():
                logging.debug("will retry connect kafka")
                continue
            logging.debug(f"connect kafka cluster "
                          f"{kafka_config['bootstrap_servers']} successful")
            return producer

    @property
    def wrapper_log_send(self):
        return partial(self.producer.send, topic=self.LOG_TOPIC)

    def log_send(self, value=None, key=None, headers=None, timestamp_ms=None):
        partition = self.partition_selector.__next__()
        return self.wrapper_log_send(
            key=key,
            headers=headers,
            value=value,
            partition=partition,
            timestamp_ms=timestamp_ms
        )
