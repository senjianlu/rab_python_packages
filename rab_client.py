#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_clinet.py
# @DATE: 2021/09/04 周六
# @TIME: 21:46:33
#
# @DESCRIPTION: 长连接模块


import sys
import requests
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_logging


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: 长连接类
-------
@param:
-------
@return:
"""
class r_client():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self, basic_url=None, auth=None, headers=None, proxies=None):
        # 连接
        self.client = requests.session()
        # 基础 API 地址
        self.basic_url = basic_url
        # 默认参数
        self.auth = auth
        self.headers = headers
        self.proxies = proxies
        # 动作
        self.action = {}
    
    """
    @description: 添加动作
    -------
    @param:
    -------
    @return:
    """
    def add_action(self,
                   name,
                   method="GET",
                   route=None,
                   url=None,
                   basic_params=None,
                   basic_data=None):
        self.action[name] = {
            "method": method,
            "route": route,
            "url": url,
            "basic_params": basic_params,
            "basic_data": basic_data
        }
    
    """
    @description: 执行动作
    -------
    @param:
    -------
    @return:
    """
    def do_action(self, name, _format=None, params=None, data=None):
        action_response = None
        # 如果有这个动作
        if (name in self.action.keys()):
            # 获取 API 地址
            if (self.action[name]["route"]):
                url = self.basic_url + self.action[name]["route"]
            else:
                url = action[name]["url"]
            # 如果有需要 _format 的参数
            if (_format):
                url = url.format(**_format)
            print(url)
            # 参数增加
            if (self.action[name]["basic_params"]):
                if (params):
                    basic_params = self.action[name]["basic_params"]
                    basic_params.update(params)
                    params = basic_params
            # 请求数据增加
            if (self.action[name]["basic_data"]):
                # POST 字典类型
                if (type(data) == dict):
                    basic_data = self.action[name]["basic_data"]
                    basic_data.update(data)
                    data = basic_data
                # 文件数据类型
                else:
                    data = data
            # 请求
            # GET
            if (self.action[name]["method"].upper() == "GET"):
                action_response = self.client.get(url, \
                    params=params, \
                    data=data, \
                    auth=self.auth, \
                    headers=self.headers, \
                    proxies=self.proxies)
            # POST
            elif(self.action[name]["method"].upper() == "POST"):
                action_response = self.client.post(url, \
                    params=params, \
                    data=data, \
                    auth=self.auth, \
                    headers=self.headers, \
                    proxies=self.proxies)
            # PUT
            elif(self.action[name]["method"].upper() == "PUT"):
                action_response = requests.request("PUT", url, \
                    params=params, \
                    data=data, \
                    auth=self.auth, \
                    headers=self.headers, \
                    proxies=self.proxies)
            # MKCOL
            elif(self.action[name]["method"].upper() == "MKCOL"):
                action_response = requests.request("MKCOL", url, \
                    params=params, \
                    data=data, \
                    auth=self.auth, \
                    headers=self.headers, \
                    proxies=self.proxies)
            else:
                r_logger.error("{name} 动作不支持 {method} 的操作方式！".format(
                    name=name, method=self.action[name]["method"]))
        else:
            r_logger.error("{} 动作尚不存在！".format(name))
        return action_response


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    pass