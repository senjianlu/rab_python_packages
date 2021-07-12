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
    # 判断该路径下配置文件是否存在
    if (os.path.exists(file_name)):
        config.read(file_name, encoding="utf-8")
    # 不在的话就在上层路径查找
    elif(os.path.exists("../"+file_name)):
        config.read("../"+file_name, encoding="utf-8")
    # 或者在共通包中查找
    elif(os.path.exists("../rab_python_packages/"+file_name)):
        config.read("../rab_python_packages/"+file_name, encoding="utf-8")
    return config

"""
@description: 读取共通包中的配置文件
-------
@param:
-------
@return:
"""
def load_package_config(configuration_class, configuration_items):
    package_config = get_config("rab_config.ini")
    configuration_vaules = []
    for configuration_item in configuration_items:
        configuration_vaules.append(
            package_config.get(configuration_class, configuration_item))
    return configuration_vaules


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    pass

        
