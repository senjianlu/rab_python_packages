#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: \rab_python_packages\rab_proxy.py
# @DATE: 2020/12/15 Tue
# @TIME: 19:46:49
#
# @DESCRIPTION: 共通包 代理获取模块


import json
import time
import hashlib
import requests
import psycopg2
import psycopg2.extras
# 切换路径到父级
import sys
sys.path.append("..")
from rab_python_packages import rab_logging
from rab_python_packages import rab_pgsql_driver


# 日志记录
rab_proxy_logger = rab_logging.build_rab_logger()


"""
@description: 从数据库获取所有代理 IP 和其对应代理端口
-------
@param:
-------
@return: proxies<dict>
"""
def get_proxies(database, user, password, host, port, table_name):
    # 连接数据库并执行 SQL 语句
    r_pgsql_driver = rab_pgsql_driver.r_pgsql_driver(database=database,
                                                     user=user,
                                                     password=password,
                                                     host=host,
                                                     port=port)
    r_pgsql_driver.create()
    # 带表列名返回
    r_pgsql_driver.cur = r_pgsql_driver.conn.cursor(
        cursor_factory=psycopg2.extras.RealDictCursor)
    sql = "SELECT * FROM " + str(table_name) + " WHERE 1 = 1"
    select_result = r_pgsql_driver.select(sql)
    # 初始化不同代理池的列表
    proxies = {}
    ips = []
    reverse_ips = []
    http_ips = []
    socks5_ips = []
    # 遍历
    for row in select_result:
        # IP 池
        ips.append(row["sps_ip"])
        # 反向代理
        if (str(row["sps_reverse_proxy_flg"]) == "1"):
            reverse_ips.append(row["sps_ip"]
                                     + ":"
                                     + row["sps_reverse_proxy_port"])
        # HTTP 代理
        if (str(row["sps_http_proxy_flg"]) == "1"):
            http_ips.append(row["sps_ip"]
                                     + ":"
                                     + row["sps_http_proxy_port"])
        # SOCKS5 代理
        if (str(row["sps_socks5_proxy_flg"]) == "1"):
            socks5_ips.append(row["sps_ip"]
                                     + ":"
                                     + row["sps_socks5_proxy_port"])
    proxies["ips"] = ips
    proxies["reverse_ips"] = reverse_ips
    proxies["http_ips"] = http_ips
    proxies["socks5_ips"] = socks5_ips
    return proxies

"""
@description: 初始化代理使用次数统计字典
-------
@param: proxies<dict>
-------
@return: usage_counts<dict>
"""
def init_usage_counts(proxies):
    usage_counts = {}
    usage_counts["reverse_usage_counts"] = {}
    usage_counts["http_usage_counts"] = {}
    usage_counts["socks5_usage_counts"] = {}
    for proxy in proxies["reverse_ips"]:
        usage_counts["reverse_usage_counts"][proxy] = 0
    for proxy in proxies["http_ips"]:
        usage_counts["http_usage_counts"][proxy] = 0
    for proxy in proxies["socks5_ips"]:
        usage_counts["socks5_usage_counts"][proxy] = 0
    return usage_counts

"""
@description: 用讯代理订单号请求返回代理和头
-------
@param: orderno<str>
-------
@return:
"""
def init_xdaili_proxy(orderno, secret):
    # 拼接获取ip的源地址
    ip = "forward.xdaili.cn"
    port = "80"
    ip_port = ip + ":" + port
    # 获取md5加密源
    timestamp = str(int(time.time()))
    string = "orderno=" + orderno + "," + "secret=" + secret + "," \
             + "timestamp=" + timestamp
    # python3转码    
    string = string.encode()
    # md5加密
    md5_string = hashlib.md5(string).hexdigest()
    sign = md5_string.upper()
    auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" \
           + "timestamp=" + timestamp
    # 拼接头和代理信息
    proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
    headers = {
        "Proxy-Authorization": auth,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                      + "AppleWebKit/537.36 (KHTML, like Gecko) " \
                      + "Chrome/86.0.4240.198 Safari/537.36"
    }
    return proxy, headers


"""
@description: r_proxy 类
-------
@param:
-------
@return:
"""
class r_proxy:

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self, database, user, password, host, port, table_name):
        self.proxies = get_proxies(database=database,
                                   user=user,
                                   password=password,
                                   host=host,
                                   port=port,
                                   table_name=table_name)
        self.usage_counts = init_usage_counts(self.proxies)
        self.web_accesses = {}
        self.web_accesses_usage_counts = {}
        self.xdaili_ordernos = []
        self.xdaili_secret = None
        self.xdaili_ordernos_usage_counts = {}
        self.timeout = 20
        self.http_auth = "rabproxy:12z991"
    
    """
    @description: 获取一个可用代理
    -------
    @param: proxy_method<str>
    -------
    @return: proxies(requests.get用)
    """
    def get_proxy(self, proxy_method=None, web=None):
        # 指定需要代理的网站时
        if (not proxy_method and web):
            web = web.lower()
            proxies_4_choose = self.web_accesses_usage_counts[web
                                                              + "_usage_counts"]
            min_proxy = min(proxies_4_choose, key=proxies_4_choose.get)
            self.web_accesses_usage_counts[web + "_usage_counts"][min_proxy] \
                = proxies_4_choose[min_proxy] + 1
            # 默认为 HTTP 代理形式
            min_proxy = {
                "http": "http://" + self.http_auth + "@" + str(min_proxy),
                "https": "http://" + self.http_auth + "@" + str(min_proxy)
            }
        elif (proxy_method and not web):
            proxy_method = proxy_method.lower()
            # 取使用次数最少的代理返回
            proxies_4_choose = self.usage_counts[proxy_method
                                                + "_usage_counts"]
            min_proxy = min(proxies_4_choose, key=proxies_4_choose.get)
            self.usage_counts[proxy_method + "_usage_counts"][min_proxy] \
                = proxies_4_choose[min_proxy] + 1
            # HTTP 代理获取时，构造指定代理样式返回
            if (proxy_method.lower() == "http"):
                min_proxy = {
                    "http": "http://" + self.http_auth + "@" + str(min_proxy),
                    "https": "http://" + self.http_auth + "@" + str(min_proxy)
                }
        return min_proxy

    """
    @description: 测试所有代理可用性
    -------
    @param: proxy_method<str>
    -------
    @return:
    """
    def test_proxies(self, proxy_method="all"):
        proxy_method = proxy_method.lower()
        # 反向代理
        if (proxy_method == "all" or proxy_method == "reverse"):
            for ip in self.proxies["reverse_ips"]:
                try:
                    url = "http://" + str(ip) + "/market/priceoverview/"
                    params = {
                        "appid": "730",
                        "currency": "1",
                        "market_hash_name": "Clutch Case"
                    }
                    res = requests.get(url,
                                       params=params,
                                       timeout=self.timeout)
                    # 正常返回
                    if (res.status_code != 200):
                        info_msg = str(ip) \
                                    + " 反向代理失效！相应代码：" \
                                    + str(res.status_code) + " " \
                                    + str(res.text)
                        self.usage_counts["reverse_usage_counts"][ip] = 9999
                    else:
                        info_msg = str(ip) + " 反向代理可用！"
                        self.usage_counts["reverse_usage_counts"][ip] += 1
                    rab_proxy_logger.info(info_msg)
                except Exception as e:
                    error_msg = str(ip) + " 反向代理出错！" + str(e)
                    rab_proxy_logger.error(error_msg)
                    self.usage_counts["reverse_usage_counts"][ip] = 9999
        # HTTP 代理
        if (proxy_method == "all" or proxy_method == "http"):
            for ip in self.proxies["http_ips"]:
                try:
                    http_proxies = {
                        "http": "http://" + self.http_auth + "@" + str(ip),
                        "https": "http://" + self.http_auth + "@" + str(ip)
                    }
                    url = "http://ip-api.com/json/?lang=zh-CN"
                    res = requests.get(url,
                                       proxies=http_proxies,
                                       timeout=self.timeout)
                    # 正常返回
                    if (res.status_code != 200):
                        info_msg = str(ip) \
                                    + " HTTP 代理失效！相应代码：" \
                                    + str(res.status_code) + " " \
                                    + str(res.text)
                        self.usage_counts["http_usage_counts"][ip] = 9999
                    else:
                        res_json = json.loads(res.text)
                        if (str(ip).split(":")[0] == res_json.get("query")):
                            info_msg = str(ip) + " HTTP 代理可用！"
                            self.usage_counts["http_usage_counts"][ip] += 1
                        else:
                            info_msg = str(ip) + " HTTP 代理失效！ip不相符！"
                            self.usage_counts["http_usage_counts"][ip] = 9999
                    rab_proxy_logger.info(info_msg)
                except Exception as e:
                    error_msg = str(ip) + " HTTP 代理出错！" + str(e)
                    rab_proxy_logger.error(error_msg)
                    self.usage_counts["http_usage_counts"][ip] = 9999

    """
    @description: 测试网站访问
    -------
    @param: web<str>, web_url<str>, num<int>,
    -------
    @return:
    """
    def test_web_access(self, web, web_url="https://stapi.cn", num=20):
        web = web.lower()
        # STEAM 访问测试（中国网络特殊阻断，需要反代）
        if (web == "steam"):
            steam_access_ips = []
            self.web_accesses_usage_counts["steam_usage_counts"] = {}
            for ip in self.proxies["reverse_ips"]:
                # 如果取到了指定数量，直接返回
                if (len(steam_access_ips) >= num):
                    break
                try:
                    url = "http://" + str(ip) + "/market/priceoverview/"
                    params = {
                        "appid": "730",
                        "currency": "1",
                        "market_hash_name": "Clutch Case"
                    }
                    res = requests.get(url,
                                       params=params,
                                       timeout=self.timeout)
                    # 正常返回
                    if (res.status_code != 200):
                        info_msg = str(ip) \
                                   + " 无法访问 STEAM ！相应代码：" \
                                   + str(res.status_code) + " " \
                                   + str(res.text)
                        self.web_accesses_usage_counts.get(
                            "steam_usage_counts")[ip] = 9999
                    else:
                        info_msg = str(ip) + " 成功访问 STEAM ！"
                        steam_access_ips.append(ip)
                        self.web_accesses_usage_counts.get(
                            "steam_usage_counts")[ip] = 1
                    rab_proxy_logger.info(info_msg)
                except Exception as e:
                    error_msg = str(ip) + " 访问 STEAM 出错！" + str(e)
                    rab_proxy_logger.error(error_msg)
                    self.web_accesses_usage_counts.get(
                        "steam_usage_counts")[ip] = 9999
            self.web_accesses["steam_access_ips"] = steam_access_ips
        else:
            web_access_ips = []
            self.web_accesses_usage_counts[web+"_usage_counts"] = {}
            for ip in self.proxies["http_ips"]:
                # 如果取到了指定数量，直接返回
                if (len(web_access_ips) >= num):
                    break
                try:
                    http_proxies = {
                        "http": "http://" + self.http_auth + "@" + str(ip),
                        "https": "http://" + self.http_auth + "@" + str(ip)
                    }
                    url = web_url
                    res = requests.get(url,
                                       proxies=http_proxies,
                                       timeout=self.timeout)
                    # 正常返回
                    if (res.status_code != 200):
                        info_msg = str(ip) \
                                   + " 无法访问 " \
                                   + web.upper() \
                                   + " ！响应代码：" \
                                   + str(res.status_code) + " " \
                                   + str(res.text)
                        self.web_accesses_usage_counts.get(
                            web+"_usage_counts")[ip] = 9999
                    else:
                        info_msg = str(ip) + " 成功访问 " + web.upper() + " ！"
                        web_access_ips.append(ip)
                        self.web_accesses_usage_counts.get(
                            web+"_usage_counts")[ip] = 1
                    rab_proxy_logger.info(info_msg)
                except Exception as e:
                    error_msg = str(ip) + " 访问 " + web.upper() + " 出错！" \
                                + str(e)
                    rab_proxy_logger.error(error_msg)
                    self.web_accesses_usage_counts.get(
                        web+"_usage_counts")[ip] = 9999
            self.web_accesses[web+"_access_ips"] = web_access_ips

    """
    @description: 设置讯代理用户密钥
    -------
    @param:
    -------
    @return:
    """
    def set_xdaili_secret(self, xdaili_secret):
        self.xdaili_secret = xdaili_secret

    """
    @description: 为讯代理添加一个动态转发订单
    -------
    @param: 
    -------
    @return: <bool>
    """
    def add_xdaili_orderno(self, orderno):
        if (orderno not in self.xdaili_ordernos):
            self.xdaili_ordernos.append(orderno)
            self.xdaili_ordernos_usage_counts[orderno] = 0
            return True
        else:
            return False
    
    """
    @description: 获取一个讯代理转发和头
    -------
    @param:
    -------
    @return:
    """
    def get_xdaili_proxy(self):
        proxies_4_choose = self.xdaili_ordernos_usage_counts
        min_orderno = min(proxies_4_choose, key=proxies_4_choose.get)
        self.xdaili_ordernos_usage_counts[min_orderno] \
            = proxies_4_choose[min_orderno] + 1
        return init_xdaili_proxy(min_orderno, self.xdaili_secret)


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