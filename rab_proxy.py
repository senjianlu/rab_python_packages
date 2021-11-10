#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_proxy.py
# @DATE: 2021/07/27 Tue
# @TIME: 17:42:23
#
# @DESCRIPTION: 共通包 代理获取模块


import os
import sys
import requests
import random
import docker
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_logging
from rab_python_packages import rab_ip
from rab_python_packages import rab_postgresql
from rab_python_packages import rab_subscription_node


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: 获取自建代理
-------
@param:
-------
@return:
"""
def get_personal_proxy_infos(location=None):
    personal_proxy_infos = {}
    for personal_proxy in rab_config.load_package_config(
            "rab_config.ini", "common", "proxy"):
        proxy_info = rab_subscription_node.parse_http_or_socks5_node_url(
            personal_proxy)
        if (proxy_info["type"] not in personal_proxy_infos.keys()):
            personal_proxy_infos[proxy_method] = {}
        personal_proxy_info = {
            "host": proxy_info["server"],
            "port": proxy_info["port"],
            "auth": "{}:{}".format(
                proxy_info["username"], proxy_info["password"]),
            "access": {},
            "level": 10
        }
        if (location):
            # 将代理转换并测试代理所在地区
            ip_info = rab_ip.get_ip_info(
                parse_proxy_info(proxy_method, personal_proxy_info))
            if (ip_info["location"] == location):
                personal_proxy_infos[proxy_method][out_ip] = personal_proxy_info
        else:
            personal_proxy_infos[proxy_method][out_ip] = personal_proxy_info
    return personal_proxy_infos

"""
@description: 获取指定地区下所有可用代理
-------
@param:
-------
@return:
"""
@rab_postgresql.change_database(rab_config.load_package_config(
    "rab_config.ini", "rab_proxy", "proxy_database"))
def get_proxy_infos(r_pgsql_driver, location=None, level=None):
    # 代理信息存储
    proxy_infos = {
        "reverse": {},
        "http": {},
        "socks5":{}
    }
    # 如果对代理等级无要求，则从数据库中搜索出其他代理
    if (not level or level < 10):
        # 搜索所有代理
        select_sql = """
            SELECT
                *
            FROM
                (SELECT
                    sp_ip AS host,
                    sp_out_ip AS out_ip,
                    sp_location AS location,
                    '' AS reverse_proxy_port,
                    '' AS reverse_auth_info,
                    sp_http_proxy_port AS http_proxy_port,
                    sp_http_auth_info AS http_auth_info,
                    sp_socks5_proxy_port AS socks5_proxy_port,
                    sp_socks5_auth_info AS socks5_auth_info,
                    sp_access_info AS access_info,
                    sp_status AS status,
                    5 AS level
                FROM
                    sa_proxy
                WHERE
                    1 = 1
                UNION
                SELECT
                    sps_ip AS host,
                    sps_ip AS out_ip,
                    sps_location AS location,
                    sps_reverse_proxy_port AS reverse_proxy_port,
                    '' AS reverse_auth_info,
                    sps_http_proxy_port AS http_proxy_port,
                    sps_http_auth_info AS http_auth_info,
                    sps_socks5_proxy_port AS socks5_proxy_port,
                    sps_socks5_auth_info AS socks5_auth_info,
                    sps_access_info AS access_info,
                    sps_status AS status,
                    8 AS level
                FROM
                    sa_proxy_server
                WHERE
                    1 = 1
                ) proxy
            WHERE
                1 = 1
            AND status = 1
        """
        # 如果有地区限制，多加一行搜索条件
        if (location):
            select_filter_2_append = """
                AND proxy.location IS NOT NULL
                AND proxy.location LIKE '%{}%'
            """.format(location)
            select_sql = select_sql + select_filter_2_append
        # 搜索
        result = r_pgsql_driver.select(select_sql)
        # 乱序搜索结果
        random.shuffle(result)
        # 将搜索出的数据转为代理字典
        for row in result:
            for proxy_method in proxy_infos.keys():
                # 如果端口有服务
                if (row[proxy_method+"_proxy_port"]):
                    # 出口 IP 作为主键
                    out_ip = row["out_ip"]
                    # 代理信息
                    proxy_info = {
                        "host": row["host"],
                        "port": row[proxy_method+"_proxy_port"],
                        "auth": row[proxy_method+"_auth_info"],
                        "access": row["access_info"],
                        "level": row["level"]
                    }
                    proxy_infos[proxy_method][out_ip] = proxy_info
                # 端口无服务说明此代理不存在
                else:
                    pass
    return proxy_infos

"""
@description: 初始化代理使用次数
-------
@param:
-------
@return:
"""
def init_ip_usage_counts(proxy_infos):
    ip_usage_counts = {}
    for proxy_method in proxy_infos.keys():
        for out_ip in proxy_infos[proxy_method]:
            for web in proxy_infos[proxy_method][out_ip]["access"].keys():
                # 如果还不存在这个网站对应的列表则进行新建
                if (web not in ip_usage_counts.keys()):
                    ip_usage_counts[web] = {}
                # 如果可以访问，从 0 开始计数
                if (proxy_infos[proxy_method][out_ip]["access"][web]):
                    ip_usage_counts[web][out_ip] = 0
    return ip_usage_counts

"""
@description: 根据代理信息和协议将代理可用化
-------
@param:
-------
@return:
"""
def parse_proxy_info(proxy_method, proxy_info):
    # 反代
    if (proxy_method == "reverse"):
        return "http://{host}:{port}".format(**proxy_info)
    # HTTP 代理
    elif(proxy_method == "http"):
        return {
            "http": "http://{auth}@{host}:{port}".format(**proxy_info),
            "https": "http://{auth}@{host}:{port}".format(**proxy_info)
        }
    # SOCKS5 代理
    elif(proxy_method == "socks5"):
        return {
            "http": "socks5h://{auth}@{host}:{port}".format(**proxy_info),
            "https": "socks5h://{auth}@{host}:{port}".format(**proxy_info)
        }


"""
@description: r_proxy 类
-------
@param:
-------
@return:
"""
class r_proxy():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self, r_pgsql_driver, location=None, level=None):
        # 数据库连接
        self.r_pgsql_driver = r_pgsql_driver
        # 所有代理信息
        self.proxy_infos = get_proxy_infos(r_pgsql_driver, location, level)
        # 各个网站中各个代理的访问次数
        self.ip_usage_counts = init_ip_usage_counts(self.proxy_infos)
    
    """
    @description: 获取一个可用代理
    -------
    @param:
    -------
    @return:
    """
    def get(self, web, accessable_webs=[], proxy_method="socks5"):
        # 测试所有需要验证的网站是否都有访问可行性数据
        all_webs = [web]
        for accessable_web in accessable_webs:
            all_webs.append(accessable_web)
        for web in all_webs:
            web = web.lower()
            if (web in self.ip_usage_counts.keys()):
                pass
            # 如果没有访问可行性数据，则报错
            else:
                r_logger.warn(
                    "暂时没有针对网站：{} 的代理访问可行性测试！".format(web))
                return None
        # 取出能访问主网站的 IP
        filtered_ip_usage_counts = {}
        for out_ip in self.ip_usage_counts[web]:
            # 如果这个 IP 能支持指定的代理方式
            if (out_ip in self.proxy_infos[proxy_method].keys()):
                filtered_ip_usage_counts[out_ip] \
                    = self.ip_usage_counts[web][out_ip]
        # 如果有其他需要验证可用性的网站则进行二次筛选
        filtered_2x_ip_usage_counts = {}
        if (accessable_webs):
            for out_ip in filtered_ip_usage_counts:
                access_flg = True
                for accessable_web in accessable_webs:
                    if (out_ip in self.ip_usage_counts[accessable_web]):
                        pass
                    else:
                        # 跳过这个 IP
                        access_flg = False
                # 这个 IP 对所有需要访问的网站都可行时加入二次筛选结果
                if (access_flg):
                    filtered_2x_ip_usage_counts[out_ip] \
                        = filtered_ip_usage_counts[out_ip]
            filtered_ip_usage_counts = filtered_2x_ip_usage_counts
        # 获取使用次数最少的那个代理
        least_used_ip = min(
            filtered_ip_usage_counts, key=filtered_ip_usage_counts.get)
        # 将使用次数加 1
        self.ip_usage_counts[web][least_used_ip] += 1
        # 将这个代理的所有信息根据传入协议转换为直接可用的代理
        serviceable_proxy = parse_proxy_info(
            proxy_method, self.proxy_infos[proxy_method][least_used_ip])
        return serviceable_proxy
    
    """
    @description: Ban 掉无法使用的 IP
    -------
    @param:
    -------
    @return:
    """
    def ban(self, out_ip, web=None):
        # 如果不传入网站，则说明节点已经不通，直接去除
        if (web and web in self.ip_usage_counts.keys()):
            if (out_ip in self.ip_usage_counts[web].keys()):
                del self.ip_usage_counts[web][out_ip]
            else:
                pass
        # 如果不传入网站，则说明节点已经不通，直接去除
        else:
            for web in self.ip_usage_counts.keys():
                if (out_ip in self.ip_usage_counts[web].keys()):
                    del self.ip_usage_counts[web][out_ip]
                else:
                    pass
    
    """
    @description: 代理访问网站可行性的临时测试
    -------
    @param:
    -------
    @return:
    """
    def temporary_test_access(self,
                              web,
                              test_url,
                              num_2_test=None,
                              proxy_method="socks5"):
        r_logger.info(
            "代理对站点的临时访问测试开始！站点名：{web} 地址：{test_url}".format(
                web=web, test_url=test_url))
        # 新建这个网站的代理使用次数统计
        self.ip_usage_counts[web] = {}
        # 如果没有指定测试代理数，默认从代理池中取出一半的代理进行测试，最多选出 10 个
        if (not num_2_test
                and len(list(self.proxy_infos[proxy_method].keys())) <= 20):
            num_2_test = len(list(self.proxy_infos[proxy_method].keys())) // 2
        elif(not num_2_test):
            num_2_test = 10
        r_logger.info("总测试代理数：{}".format(str(num_2_test)))
        # 遍历这些代理
        for out_ip in random.sample(list(
                self.proxy_infos[proxy_method].keys()), num_2_test):
            # 如果测试访问通过，记使用次数 1 次
            if (rab_ip.test(test_url, proxies=parse_proxy_info(
                    proxy_method, self.proxy_infos[proxy_method][out_ip]))):
                self.ip_usage_counts[web][out_ip] = 1
        # 最后如果测试完这个网站无可访问节点，则直接删除次数统计
        if (not self.ip_usage_counts[web]):
            del self.ip_usage_counts[web]
            r_logger.info("测试完成，无可访问 {web} 的代理。".format(web=web))
        else:
            r_logger.info("测试完成！访问 {web} 可使用代理的个数：{num}".format(
                web=web, num=str(len(self.ip_usage_counts[web].keys()))))


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    r_pgsql_driver = rab_postgresql.r_pgsql_driver(show_column_name=True)
    try:
        print(get_proxy_infos(r_pgsql_driver))
    except Exception as e:
        r_logger.error("rab_proxy.py 单体测试出错！")
        r_logger.error(e)
    finally:
        r_pgsql_driver.close()