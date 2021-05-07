#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2021/4/22 2:03 下午
# @Author  : Hanley
# @File    : init_tables.py
# @Desc    :

import os
import sys
import time
import traceback

proPath = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)))  # noqa
sys.path.append(proPath)  # noqa
from commons.initlog import logging
from models.base import *


def generate_subclass(sub_model: list, list_model: list) -> list:
    for item in sub_model:
        if item.__subclasses__():
            generate_subclass(item.__subclasses__(), list_model)
        if item.__name__ not in list_model and len(item.__subclasses__()) == 0:
            list_model.append(item)
    return list_model


def find_orm() -> list:
    sub_model = BaseModel.__subclasses__()
    list_model = generate_subclass(sub_model, [])
    list_model = [item for item in list_model if not item.table_exists()]
    return list_model


def insert_single_data(model, dataList, chunk_size=100):
    with mysql_client.allow_sync():
        with mysql_client.atomic():
            try:
                logging.debug(f"start insert data to {model}")
                for i in range(0, len(dataList), chunk_size):
                    logging.debug(f"data: {dataList[i: i + chunk_size]}")
                    model.insert_many(dataList[i: i + chunk_size]).execute()
            except BaseException:
                logging.error(traceback.format_exc())


def insert_multi_data(modelList, dataDict):
    for model in modelList:
        if model.select().count() > 0:
            logging.debug(f"{model.__name__} already had data, so continue")
            continue
        for key, value in dataDict.items():
            if model.__name__ == key:
                insert_single_data(model, value)


def complete_table():
    """
    补全mysql表
    :return:
    """
    miss_model = find_orm()
    with mysql_client.allow_sync():
        with mysql_client.atomic():
            logging.debug(f"Missing models: "
                      f"{[model.__name__ for model in miss_model]}")
            if len(miss_model):
                logging.debug("start create tables...")
                mysql_client.create_tables(miss_model)
                logging.debug("end create tables")
    logging.debug("complete_table done")


def sync_uri(handlers: list):
    now = time.strftime("%Y-%m-%d %X")
    # 更新接口到数据库

    with mysql_client.allow_sync():
        with mysql_client.atomic():
            existing_config = UriConfig.select().dicts()
            existing_path = {config["path"]: config for config in existing_config}
            running_path = set()
            for handler in handlers:
                path = handler.matcher._path
                pattern = handler.regex.pattern
                running_path.add(path)
                _config = existing_path.get(path)
                _last = UriConfig.select().order_by(-UriConfig.code).first()
                code = _last.code + 1 if _last else 10 << 10
                name = handler.name
                description = handler.handler_class.__doc__
                method = ",".join(handler.handler_class.SUPPORTED_METHODS)
                # 注册新接口
                if not _config:
                    insert_dict = {
                        "code": code,
                        "path": path,
                        "name": name,
                        "description": description.replace(' ', "") if description else "",
                        "method": method,
                        "regex": 1 if pattern else 0,
                        "pattern": pattern
                    }
                    UriConfig.insert(insert_dict).execute()
                    code += 1
                else:
                    update_dict = {
                        "name": name,
                        "description": description.replace(' ', "") if description else "",
                        "method": method,
                        "regex": 1 if pattern else 0,
                        "pattern": pattern,
                        "status": 1,
                        "update_time": now,
                    }
                    UriConfig.update(update_dict).where(
                        UriConfig.path == path).execute()
            effect_existing_path = {path for path in existing_path if existing_path[path]["status"] == 1}
            disabled_path = list(effect_existing_path - running_path)
            if disabled_path:
                UriConfig.update({"status": 0, "update_time": now}).where(
                    UriConfig.path << disabled_path).execute()
    logging.debug(f"sync uri config done")


if __name__ == '__main__':
    complete_table()
