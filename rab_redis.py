#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_redis.py
# @DATE: 2021/10/18 Mon
# @TIME: 17:29:35
#
# @DESCRIPTION: 共通包 Redis 模块


import sys
import redis
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_logging


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: Redis 对象
-------
@param:
-------
@return:
"""
class r_redis():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self,
                 host=rab_config.load_package_config(
                     "rab_config.ini", "rab_redis", "host"),
                 port=rab_config.load_package_config(
                     "rab_config.ini", "rab_redis", "port"),
                 password=rab_config.load_package_config(
                     "rab_config.ini", "rab_redis", "password"),
                 decode_responses=True):
        self.host = host
        self.port = port
        self.password = password
        self.decode_responses = decode_responses
        self.connection = None
    
    """
    @description: 建立连接
    -------
    @param:
    -------
    @return:
    """
    def connect(self):
        try:
            self.connection = redis.Redis(host=self.host, port=self.port, \
                password=self.password, decode_responses=self.decode_responses)
            return True
        except Exception as e:
            r_logger.error("Redis 建立连接时出错！")
            r_logger.error(e)
            return False
    
    """
    @description: 断开连接
    -------
    @param:
    -------
    @return:
    """
    def disconnect(self):
        pass


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    r_redis = r_redis()
    r_redis.connect()