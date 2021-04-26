#!/usr/bin/env python
# -*- coding: utf-8 -*-

# @Time    : 2020/10/22 上午11:08
# @Author  : Hanley
# @File    : init_mysql.py
# @Desc    : 


import os
import sys
import threading
import traceback
from pprint import pprint

proPath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # noqa
sys.path.append(proPath)  # noqa
import ujson

from models.base import _mysql


class InsertData(threading.Thread):

    def __init__(self, model, dataList):
        super(InsertData, self).__init__()
        self.model = model
        self.dataList = dataList

    def insert_data(self, chunk_size=100):
        """
        数据批插入
        :param chunk_size:
        :return:
        """
        with _mysql.atomic():
            with _mysql.atomic():
                for i in range(0, len(self.dataList), chunk_size):
                    self.model.insert_many(self.dataList[i: i + chunk_size]).execute()
        return

    def data_pre(self):
        """
        数据预处理
        :return:
        """
        pass

    def run(self):
        try:
            self.data_pre()
            self.insert_data()
            pprint(f"insert {self.model.__name__} successful")
        except BaseException:
            pprint(traceback.format_exc())
            pprint(f"insert {self.model.__name__} fail")


def initData(modelList, continueList=None):
    dataPath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'init_data.json')

    with open(dataPath, 'r') as f:
        dataDict = ujson.load(f)
    thread_pool = []
    for model in modelList:
        if continueList:
            if model.__name__ in continueList:
                continue
        if model.select().count() > 0:
            pprint(f"{model.__name__} already had data, so continue")
            continue
        for key, value in dataDict.items():
            if model.__name__ == key:
                thread_pool.append(InsertData(model, value))
    for t in thread_pool:
        t.start()
        t.join()


if __name__ == '__main__':
    create_model = []
    baseModelList = [ChannelConfig]
    userModelList = []
    commonModelList = []
    create_model.extend(baseModelList)
    create_model.extend(userModelList)
    create_model.extend(commonModelList)
    list_model = [item for item in create_model if not item.table_exists()]
    print("Start create models: " + ",".join([item.__name__ for item in list_model]))
    _mysql.create_tables(list_model)

    print("End create models successful")
    dataModelList = []
    dataModelList.extend(baseModelList)
    dataModelList.extend(commonModelList)
    dataModelList.extend(userModelList)
    initData(dataModelList)
