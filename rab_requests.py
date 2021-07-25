#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_requests.py
# @DATE: 2021/07/12 Mon
# @TIME: 14:40:41
#
# @DESCRIPTION: 基于 Requests 的爬虫用优化版本


import requests
# 切换路径到父级
import sys
sys.path.append("..")
from rab_python_packages import rab_config


"""
@description: 从数据库获取所有代理 IP 和其对应代理端口
-------
@param:
-------
@return:
"""
def r_get(url, timeout=None):
    proxy = rab_config.load_package_config(
        "rab_config.ini", "rab_requests", "proxy")
    if (not timeout):
        timeout = int(rab_config.load_package_config(
            "rab_config.ini", "rab_requests", "timeout"))
    try:
        r_r = requests.get(url, timeout=timeout)
    except Exception as e:
        print(url + " 不使用代理访问出错！开始使用代理尝试......")
    proxies = {
        "http": proxy,
        "https": proxy
    }
    r_r = requests.get(url, proxies=proxies, timeout=timeout)
    return r_r