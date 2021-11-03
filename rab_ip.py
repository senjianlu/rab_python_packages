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
@description: 解析 IP 接口返回的数据
-------
@param:
-------
@return:
"""
def parse_ip_info(api_url, r_json):
    ip_info = {
        "ip": None,
        "location": None
    }
    if (api_url == "http://ip-api.com/json/?lang=zh-CN"):
        ip_info["ip"] = r_json["query"] if "query" in r_json else None
        ip_info["location"] = r_json["country"] if "country" in r_json else None
    elif(api_url == "https://www.ip.cn/api/index?ip=&type=0"):
        ip_info["ip"] = r_json["ip"] if "ip" in r_json else None
        ip_info["location"] = r_json["address"] if "address" in r_json else None
    elif(api_url == "https://ip-api.io/json"):
        ip_info["ip"] = r_json["ip"] if "ip" in r_json else None
        ip_info["location"] = r_json["country_name"] \
            if "country_name" in r_json else None
    elif(api_url == "https://api.ipify.org/?format=json"):
        ip_info["ip"] = r_json["ip"] if "ip" in r_json else None
        ip_info["location"] = None
    return ip_info

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
    api_urls = [
        "http://ip-api.com/json/?lang=zh-CN",
        "https://www.ip.cn/api/index?ip=&type=0",
        "https://ip-api.io/json",
        # 只会返回 IP 的接口
        "https://api.ipify.org/?format=json"
    ]
    for api_url in api_urls:
        try:
            r = requests.get(api_url, proxies=proxies, timeout=timeout)
            r_json = json.loads(r.text)
            ip_info = parse_ip_info(api_url, r_json)
            # 如果访问成功了有 IP 信息了则退出
            if (ip_info["ip"] or ip_info["location"]):
                return ip_info
        except Exception as e:
            r_logger.error("使用 {} 获取 IP 信息出错！".format(api_url))
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


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    print(get_ip_info())
