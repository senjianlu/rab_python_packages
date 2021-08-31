#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_ip.py
# @DATE: 2021/08/31 Tue
# @TIME: 14:52:20
#
# @DESCRIPTION: 代理或本机 IP 获取方法整合模块


import sys
import json
import requests
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_logging


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: 获取 IP 信息
-------
@param:
-------
@return:
"""
def get_ip_info(proxies=None,
                timeout=int(rab_config.load_package_config(
                    "rab_config.ini", "rab_requests", "timeout"))):
    # 接口：http://ip-api.com/json/?lang=zh-CN
    try:
        r = requests.get("http://ip-api.com/json/?lang=zh-CN",
                         proxies=proxies,
                         timeout=timeout)
        r_json = json.loads(r.text)
        ip = r_json["query"] if "query" in r_json else None
        location = r_json["country"] if "country" in r_json else None
        return {
            "ip": ip,
            "location": location
        }
    except Exception as e:
        r_logger.error("使用 ip-api.com 获取 IP 信息出错！")
        r_logger.error(e)
    # 接口：https://www.ip.cn/api/index?ip=&type=0
    try:
        r = requests.get("https://www.ip.cn/api/index?ip=&type=0",
                         proxies=proxies,
                         timeout=timeout)
        r_json = json.loads(r.text)
        ip = r_json["ip"] if "ip" in r_json else None
        location = r_json["address"] if "address" in r_json else None
        return {
            "ip": ip,
            "location": location
        }
    except Exception as e:
        r_logger.error("使用 ip.cn 获取 IP 信息出错！")
        r_logger.error(e)
    return {"ip": None, "location": None}

"""
@description: 测试访问
-------
@param:
-------
@return:
"""
def test(test_url,
         proxies=None,
         timeout = int(rab_config.load_package_config(
             "rab_config.ini", "rab_requests", "timeout")),
         success_status_codes=[200],
         error_status_codes=[500]):
    success_flg = False
    try:
        r = requests.get(test_url, proxies=proxies, timeout=timeout)
        if (r.status_code in success_status_codes):
            r_logger.info(
                "测试访问地址：{test_url} 成功！".format(test_url=test_url))
            success_flg = True
        else:
            r_logger.info(
                "测试访问地址：{test_url} 不通过！响应代码：{status_code}".format(
                    test_url=test_url, status_code=str(r.status_code)))
    except Exception as e:
        r_logger.info("测试访问地址：{test_url} 出错！错误信息：{e}".format(
            test_url=test_url, e=str(e)))
    r_logger.info("使用的代理：{proxies}".format(proxies=str(proxies)))
    return success_flg