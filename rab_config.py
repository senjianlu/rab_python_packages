#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_config.py
# @DATE: 2020/12/29 周二
# @TIME: 19:50:03
#
# @DESCRIPTION: 共通包 配置读取模块


import os
import sys
import json
import configparser
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_env


"""
@description: 获取所有配置信息
-------
@param: file_name<str>
-------
@return: 
"""
def get_config(file_name):
    file_path = rab_env.find_rab_file(file_name)
    config = configparser.RawConfigParser()
    config.read(file_path, encoding="UTF-8")
    return config

"""
@description: 合理化转换
-------
@param:
-------
@return:
"""
def parse_if_need(configuration_item):
    parsed_configuration_item = configuration_item
    # 如果是 list 形式的
    if ("[" in configuration_item and "]" in configuration_item):
        configuration_item = configuration_item.lstrip("[").rstrip("]")
        list_items = configuration_item.split(",")
        parsed_configuration_item = []
        for list_item in list_items:
            list_item = list_item.lstrip().lstrip('"').rstrip('"')
            parsed_configuration_item.append(list_item)
    # 如果是 JSON 形式
    elif(configuration_item.strip().startswith("{")
            and configuration_item.strip().endswith("}")):
        parsed_configuration_item = json.loads(configuration_item)
    return parsed_configuration_item

"""
@description: 读取共通包中的配置文件
-------
@param:
-------
@return:
"""
def load_package_config(file_name, configuration_class, configuration_item):
    package_config = get_config(file_name)
    configuration_value = package_config.get(
        configuration_class, configuration_item)
    # 对部分值进行合理转换，例如：列表
    configuration_value = parse_if_need(configuration_value)
    return configuration_value


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    subscription_urls = load_package_config(
        "rab_config.ini", "rab_subscription", "access_test_urls")
    print(subscription_urls)
    pass