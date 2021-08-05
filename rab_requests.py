#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_requests.py
# @DATE: 2021/07/12 Mon
# @TIME: 14:40:41
#
# @DESCRIPTION: 基于 Requests 的爬虫用优化版本


import sys
import json
import requests
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_logging
from rab_python_packages import rab_proxy


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
    try:
        r = requests.get("http://ip-api.com/json/?lang=zh-CN",
                         proxies=proxy,
                         timeout=timeout)
        return {
            "ip": json.loads(r.text)["query"],
            "location": json.loads(r.text)["country"]
        }
    except Exception as e:
        r_logger.error("获取 IP 信息出错！")
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
@description: 不使用代理无法访问的情况下，尝试所有自建代理进行保险访问
-------
@param:
-------
@return:
"""
def ensure_get(url,
               timeout = int(rab_config.load_package_config(
                    "rab_config.ini", "rab_requests", "timeout")),
               success_status_codes=[200],
               error_status_codes=[500]):
    # 不适用代理的情况下访问
    try:
        r = requests.get(url, timeout=timeout)
        if (r.status_code in success_status_codes):
            return r
    except Exception as e:
        r_logger.info("无法在不使用代理的情况下访问：{url}！错误信息：{e}".format(
            url=url, e=str(e)))
    r_logger.info("不使用代理无法访问的情况下，开始尝试使用代理访问：{}".format(url))
    # 使用自建 SOCKS5 代理进行访问
    personal_proxy_infos = rab_proxy.get_personal_proxy_infos()
    for proxy_info in personal_proxy_infos["socks5"]:
        proxies = rab_proxy.parse_proxy_info("socks5", proxy_info)
        try:
            r = requests.get(url, proxies=proxies, timeout=timeout)
        except Exception as e:
            r_logger.info("在使用代理的情况下也无法访问：{url}！错误信息：{e}" \
                .format(url=url, e=str(e)))
            r_logger.info("使用的代理：{proxies}".format(proxies=str(proxies)))
    r_error("所有自建代理均无法访问：{url} 请检查地址或自建代理！".format(url=url))
    return None


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
                _proxies = proxies
            else:
                _proxies = self.r_proxy.get(web=web)
            # 判断是否传入了超时时间
            if (timeout):
                pass
            else:
                timeout = self.timeout
            try:
                r_r = requests.get(url, params=params, headers=headers, \
                    proxies=_proxies, timeout=timeout)
                return r_r
            except Exception as e:
                r_logger.info("r_requests.get 第 {try_no} 次访问出错！{e}".format(
                    try_no=str(try_no), e=str(e)))
                r_logger.info("使用的代理：{}".format(str(_proxies)))
                continue
        # 尝试了最大次数后仍然失败
        r_logger.warn("共 {} 次访问出错，达到上限访问结束！".format(
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