#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/Github/rab_python_packages/rab_subscription.py
# @DATE: 2021/05/10 Mon
# @TIME: 14:11:24
#
# @DESCRIPTION: 共通包 Linux 系统下解析订阅


import sys
import json
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_logging
from rab_python_packages import rab_cryptography
from rab_python_packages import rab_requests


# 日志记录
r_logger = rab_logging.r_logger()


class Subscription():
    """
    订阅类
    """

    def __init__(self, kind, url):
        """
        初始化
        """
        self.kind = kind
        self.url = url
        # 是否已经请求
        self.is_request = 0
        # 原始的请求信息
        self.response_content = None
        # 是否已经解析
        self.is_parse = 0
        # 节点数量
        self.nodes_count = None
        # 节点原始信息列表
        self.node_origin_infos = []
        # 节点 ID 列表（PostgreSQL 支持列表格式数据的存取）
        self.node_ids = []
        # 节点认证信息
        self.node_auth_info = None
        # 流量使用模式
        self.traffic_mode = None
        # 流量限制（单位为 mb）
        self.traffic_maximum = None
        # 流量已使用（单位为 mb）
        self.traffic_used = None
        # 流量下次重置日期
        self.traffic_next_reset_date = None
        # 订阅过期日期
        self.expiration_date = None
        # 订阅提供商名字
        self.provider_name = None
        # 订单提供商地址
        self.provider_url = None
        # 订阅提供商登陆用户名
        self.provider_auth_username = None
        # 订阅提供商登陆用户名
        self.provider_auth_password = None


"""
@description: 获取订阅的 Base64 解码前的原始信息
-------
@param:
-------
@return:
"""
def get_subscription_origin_info(subscription_url):
    try:
        # 保险访问
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) " \
                + "AppleWebKit/535.36 (KHTML, like Gecko) " \
                + "Chrome/92.0.4515.131 Safari/537.36"
        }
        e_response = rab_requests.ensure_request(
            "GET", subscription_url, headers=headers)
        if (e_response):
            return e_response.text
        else:
            r_logger.warn("{} 尝试所有自建代理仍无法获取订阅原始信息！".format(
                subscription_url))
    except Exception as e:
        r_logger.error("{} 获取订阅原始信息出错！".format(
            subscription_url))
        r_logger.error(e)
    return None

"""
@description: 获取订阅的原始信息经过 Base64 解码后的各节点链接
-------
@param:
-------
@return:
"""
def get_node_urls(subscription_origin_info):
    node_urls = []
    # 尝试对原始信息进行解码
    try:
        subscription_info = rab_cryptography.b64decode(
            subscription_origin_info).decode("UTF-8")
        # 分割节点链接并放入结果列表
        if (subscription_info):
            for row in subscription_info.split("\n"):
                if (row.strip()):
                    node_urls.append(row.strip())
    except Exception as e:
        r_logger.error("{} 订阅原始信息 Base64 解码失败！".format(
            str(subscription_origin_info)))
        r_logger.error(e)
    return node_urls


"""
@description: 订阅类
-------
@param:
-------
@return:
"""
class r_subscription():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self, subscription_url):
        # 订阅地址
        self.url = subscription_url
        # 订阅原始信息
        self.origin_info = get_subscription_origin_info(subscription_url)
        # 节点链接
        self.node_urls = get_node_urls(self.origin_info)


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":

    from rab_python_packages import rab_postgresql

    r_pgsql_driver=rab_postgresql.r_pgsql_driver(show_column_name=True)
    try:
        # 获取订阅并解析节点链接
        select_sql = """
            SELECT
                *
            FROM
                sa_proxy_subscription
            where
                is_deleted = 0
        """
        select_result = r_pgsql_driver.select(select_sql)
        for row in select_result:
            with open("node_urls", "a") as f:
                for node_url in r_subscription(row["sps_url"]).node_urls:
                    f.write("{}\n".format(node_url))
    except Exception as e:
        r_logger.error("rab_subscription 模块单体测试出错！")
        r_logger.error(e)
    finally:
        r_pgsql_driver.close()