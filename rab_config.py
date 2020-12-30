#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: E:\Github\rab_python_packages\rab_config.py
# @DATE: 2020/12/29 周二
# @TIME: 19:50:03
#
# @DESCRIPTION: 共通包 配置读取模块


import os
import configparser


"""
@description: 获取所有配置信息
-------
@param: file_name<str>
-------
@return: 
"""
def get_config(file_name):
    config = configparser.ConfigParser()
    # 判断路径是否存在，不在的话就在上层路径查找
    if (os.path.exists(file_name)):
        config.read(file_name, encoding="utf-8")
    elif (os.path.exists("../"+file_name)):
        config.read("../"+file_name, encoding="utf-8")
    return config


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    # todo...
    print("todo...")

        
