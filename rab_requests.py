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
import urllib
import requests
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_logging
from rab_python_packages import rab_proxy


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: 根据请求地址和参数拼凑出实际链接
-------
@param:
-------
@return:
"""
def get_true_url(url, params):
    url_parts = list(urllib.parse.urlparse(url))
    url_parts[4] = urllib.parse.urlencode(params)
    return urllib.parse.urlunparse(url_parts)

"""
@description: 不使用代理无法访问的情况下，尝试所有自建代理进行保险访问
-------
@param:
-------
@return:
"""
def ensure_request(method,
                   url,
                   params=None,
                   data=None,
                   headers=None,
                   timeout = int(rab_config.load_package_config(
                       "rab_config.ini", "rab_requests", "timeout")),
                   success_status_codes=[200],
                   error_status_codes=[500]):
    # 不适用代理的情况下访问
    try:
        r = requests.request(method.upper(), url, params=params, \
            data=data, headers=headers, timeout=timeout)
        if (r.status_code in success_status_codes):
            return r
    except Exception as e:
        r_logger.info("无法在不使用代理的情况下访问：{url}！错误信息：{e}".format(
            url=url, e=str(e)))
    r_logger.info("不使用代理无法访问的情况下，开始尝试使用代理访问：{}".format(url))
    # 使用自建 SOCKS5 代理进行访问
    personal_proxy_infos = rab_proxy.get_personal_proxy_infos()
    for proxy_out_ip in personal_proxy_infos["socks5"]:
        proxies = rab_proxy.parse_proxy_info(
            "socks5", personal_proxy_infos["socks5"][proxy_out_ip])
        try:
            r = requests.request(method.upper(), url, params=params, \
                data=data, headers=headers, proxies=proxies, timeout=timeout)
            if (r.status_code in success_status_codes):
                return r
        except Exception as e:
            r_logger.info("在使用代理的情况下也无法访问：{url}！错误信息：{e}" \
                .format(url=url, e=str(e)))
            r_logger.info("使用的代理：{proxies}".format(proxies=str(proxies)))
    r_logger.error(
        "所有自建代理均无法访问：{url} 请检查地址或自建代理！".format(url=url))
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
                r_logger.info("第 {try_no} 次访问出错！{e}".format(
                    try_no=str(try_no), e=str(e)))
                r_logger.info("使用的代理：{}".format(str(_proxies)))
                continue
        # 尝试了最大次数后仍然失败
        r_logger.warn("共 {} 次访问出错，达到上限访问结束！".format(
            str(self.max_retry_num)))
        return None
    
    """
    @description: Post 方法
    -------
    @param:
    -------
    @return:
    """
    def post(self,
             web,
             url,
             params=None,
             headers=None,
             data=None,
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
                r_r = requests.post(url, params=params, headers=headers, \
                    data=data, proxies=_proxies, timeout=timeout)
                return r_r
            except Exception as e:
                r_logger.info("第 {try_no} 次 Post 出错！{e}".format(
                    try_no=str(try_no), e=str(e)))
                r_logger.info("使用的代理：{}".format(str(_proxies)))
                continue
        # 尝试了最大次数后仍然失败
        r_logger.warn("共 {} 次 Post 出错，达到上限访问结束！".format(
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
    # personal_proxy_infos = rab_proxy.get_personal_proxy_infos()
    # print(personal_proxy_infos)
    # for proxy_out_ip in personal_proxy_infos["socks5"]:
    #     print(proxy_out_ip)
    #     print(rab_proxy.parse_proxy_info(
    #         "socks5", personal_proxy_infos["socks5"][proxy_out_ip]))
    # pass
    print(get_true_url("http://baidu.com", {"wd": "中文"}))