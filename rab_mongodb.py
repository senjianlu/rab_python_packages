#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_mongodb.py
# @DATE: 2022/03/27 周日
# @TIME: 21:01:48
#
# @DESCRIPTION: 共通包 MongoDB 模块


import sys
import pymongo
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_logging


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: r_mongodb_driver 类
-------
@param:
-------
@return:
"""
class r_mongodb_driver():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self,
                 user=rab_config.load_package_config(
                     "rab_config.ini", "rab_mongodb", "user"),
                 password=rab_config.load_package_config(
                     "rab_config.ini", "rab_mongodb", "password"),
                 host=rab_config.load_package_config(
                     "rab_config.ini", "rab_mongodb", "host"),
                 port=rab_config.load_package_config(
                     "rab_config.ini", "rab_mongodb", "port"),
                 database=None):
        # 用户
        self.user = user
        # 密码
        self.password = password
        # IP 或域名
        self.host = host
        # 端口
        self.port = port
        # 目标数据库
        self.database = database
        # 连接（客户端）
        self.client = None
        # 数据库
        self.db = None

    """
    @description: 建立数据库连接
    -------
    @param:
    -------
    @return:
    """
    def connect(self):
        # 创建连接
        self.client = pymongo.MongoClient("mongodb://{host}:{port}/".format(
            host=self.host, port=self.port))
        # 连接默认数据库
        if (not self.database):
            self.db = self.client["admin"]
        else:
            self.db = self.client[self.database]
        # 认证
        self.db.authenticate(self.user, self.password)
    
    """
    @description: 关闭数据库连接
    -------
    @param:
    -------
    @return:
    """
    def close(self):
        if (self.client):
            self.client.close()
        self.client = None


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    r_mongodb_driver = r_mongodb_driver(database="test")
    r_mongodb_driver.connect()
    print(r_mongodb_driver.client["test"].list_collection_names())
    r_mongodb_driver.close()