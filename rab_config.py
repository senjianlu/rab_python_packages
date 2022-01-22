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


"""
@description: 查找包内文件
-------
@param:
-------
@return:
"""
def find_rab_file(rab_file_name):
    paths = [
        # 在项目主目录
        "../",
        "../../",
        # 判断该路径下配置文件是否存在
        None,
        # 不在的话就在共通包中查找
        "rab_python_packages/",
        # 或者在上级路径的共通包中查找
        "../rab_python_packages/",
        "../../rab_python_packages/"
    ]
    for path in paths:
        if (path):
            if (os.path.exists(path+rab_file_name)):
                return path + rab_file_name
        else:
            if (os.path.exists(rab_file_name)):
                return rab_file_name

"""
@description: 查找包路径
-------
@param:
-------
@return:
"""
def find_rab_python_packages_path():
    paths = [
        None,
        "../"
    ]
    for path in paths:
        if (path):
            if (os.path.exists(path+"rab_python_packages")):
                return path
        else:
            if (os.path.exists("rab_python_packages")):
                return path

"""
@description: 获取所有配置信息
-------
@param: file_name<str>
-------
@return: 
"""
def get_config(file_name):
    file_path = find_rab_file(file_name)
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