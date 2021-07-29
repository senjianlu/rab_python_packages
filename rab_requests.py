#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_requests.py
# @DATE: 2021/07/12 Mon
# @TIME: 14:40:41
#
# @DESCRIPTION: 基于 Requests 的爬虫用优化版本


import json
import requests
# 切换路径到父级
import sys
sys.path.append("..")
from rab_python_packages import rab_config


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
    try:
        r = requests.get("http://ip-api.com/json/?lang=zh-CN",
                         proxies=proxy,
                         timeout=timeout)
        return {
            "ip": json.loads(r.text)["query"],
            "location": json.loads(r.text)["country"]
        }
    except Exception as e:
        print("获取 IP 信息出错！" + str(e))
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
            print("测试访问地址：{test_url} 成功！".format(test_url=test_url))
            success_flg = True
        else:
            print("测试访问地址：{test_url} 不通过！响应代码：{status_code}".format(
                test_url=test_url, status_code=str(r.status_code)))
    except Exception as e:
        print("测试访问地址：{test_url} 出错！错误信息：{e}".format(
            test_url=test_url, e=str(e)))
    print("使用的代理：{proxies}".format(proxies=str(proxies)))
    return success_flg


"""
@description: r_requests 类
-------
@param:
-------
@return:
"""
class r_requests():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self, r_proxy):
        # 代理类
        self.r_proxy = r_proxy
        # 超时时间
        self.timeout = int(rab_config.load_package_config(
             "rab_config.ini", "rab_requests", "timeout"))
        # 最大失败尝试次数
        self.max_retry_num = int(rab_config.load_package_config(
             "rab_config.ini", "rab_requests", "max_retry_num"))

    """
    @description: Get 方法
    -------
    @param:
    -------
    @return:
    """
    def get(self,
            web,
            url,
            params=None,
            headers=None,
            proxies=None,
            timeout=None):
        # 最大尝试次数
        for try_no in range(1, self.max_retry_num+1):
            # 判断是否传入了代理
            if (proxies):
                pass
            else:
                proxies = self.r_proxy.get(web=web)
            # 判断是否传入了超时时间
            if (timeout):
                pass
            else:
                timeout = self.timeout
            try:
                r_r = requests.get(url, params=params, headers=headers, \
                    proxies=proxies, timeout=timeout)
                return r_r
            except Exception as e:
                print("r_requests.get 第 {try_no} 次访问出错！{e}".format(
                    try_no=str(try_no), e=str(e)))
                continue
        # 尝试了最大次数后仍然失败
        print("共 {max_retry_num} 次访问出错，达到上限访问结束！".format(
            str(self.max_retry_num)))
        return None


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    pass