#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_advance.py
# @DATE: 2021/07/12 Mon
# @TIME: 14:51:13
#
# @DESCRIPTION: 自用进阶方法


import sys
import json
import time
import base64
import requests
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config


"""
@description: 基于 DirectAdmin 面板的自建邮局类
              文档：https://www.directadmin.com/api.html#showallusers
-------
@param:
-------
@return:
"""
class r_a_post_office():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self,
                 username=rab_config.load_package_config(
                     "rab_config.ini", "rab_advance", "rapo_username"),
                 password=rab_config.load_package_config(
                     "rab_config.ini", "rab_advance", "rapo_password"),
                 host=rab_config.load_package_config(
                     "rab_config.ini", "rab_advance", "rapo_host"),
                 port=rab_config.load_package_config(
                     "rab_config.ini", "rab_advance", "rapo_port"),
                 domain=rab_config.load_package_config(
                     "rab_config.ini", "rab_advance", "rapo_domain")):
        # 初始化
        self._username = username
        self._password = password
        self._host = host
        self._port = port
        self._domain = domain
    
    """
    @description: 执行命令
    -------
    @param: command<str>, params<dict>
    -------
    @return: response<requests.Response>
    """
    def execute_command(self, command, params=None):
        # 拼接地址
        url = self._host + ":" + str(self._port) + "/" + command
        try:
            response = requests.post(
                url, auth=(self._username, self._password), data=params)
            return response
        except Exception as e:
            print(e)
            return None
    
    """
    @description: 获取当前所有的邮箱
    -------
    @param:
    -------
    @return: mailboxes<list>
    """
    def get_all_mailboxes(self):
        # 参数
        params = {
            "action": "list",
            "domain": self._domain
        }
        # 请求
        response = self.execute_command("CMD_API_POP", params)
        # 分割和凭借邮箱地址
        mailboxes = []
        for prefix_str in response.text.split("&"):
            prefix_str = prefix_str.replace("list[]=", "")
            mailbox = prefix_str + "@" + self._domain
            mailboxes.append(mailbox)
        return mailboxes
    
    """
    @description: 新建邮箱
    -------
    @param: mailbox_prefix<str>
    -------
    @return: <bool>
    """
    def create_mailbox(self, mailbox_prefix, mailbox_password):
        # 参数
        params = {
            "action": "create",
            "domain": self._domain,
            "user": mailbox_prefix,
            "passwd": mailbox_password
        }
        # 请求
        response = self.execute_command("CMD_API_POP", params)
        if (response.status_code == 200):
            return True
        else:
            print(response.status_code, response.text)
            return False
    
    """
    @description: 删除邮箱
    -------
    @param: mailbox_prefix<str>
    -------
    @return: <bool>
    """
    def delete_mailbox(self, mailbox_prefix):
        # 参数
        params = {
            "action": "delete",
            "domain": self._domain,
            "user": mailbox_prefix
        }
        # 请求
        response = self.execute_command("CMD_API_POP", params)
        if (response.status_code == 200):
            print(response.status_code, response.text)
            return True
        else:
            print(response.status_code, response.text)
            return False

"""
@description: 5sim 接码类
-------
@param:
-------
@return:
"""
class r_a_5sim():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self, token=rab_config.load_package_config(
                     "rab_config.ini", "rab_advance", "ra5_token")):
            self.token = token
    
    """
    @description: 执行命令
    -------
    @param:
    -------
    @return:
    """
    def execute_command(self, route="", params=None):
        url = "https://5sim.net/v1/user" + route
        headers = {
            "Authorization": "Bearer {}".format(self.token),
            "Accept": "application/json"
        }
        try:
            response = requests.get(url, headers=headers, params=params)
            return response
        except Exception as e:
            print(e)
            return None
    
    """
    @description: 购买手机号
    -------
    @param:
    -------
    @return:
    """
    def buy(self, country, operator, product):
        # 路由
        route = "/buy/activation/{}/{}/{}".format(country, operator, product)
        # 请求
        response = self.execute_command(route)
        if (response.status_code == 200):
            return json.loads(response.text)
        else:
            print(response.status_code, response.text)
            return None

    """
    @description: 获取验证码
    -------
    @param:
    -------
    @return:
    """
    def get_sms(self, order_id):
        # 路由
        route = "/check/{}".format(str(order_id))
        # 最多等待一分钟
        for _ in range(0, 30):
            time.sleep(2)
            # 请求
            response = self.execute_command(route)
            if (response.status_code == 200):
                sms_list = json.loads(response.text)["sms"]
                if (len(sms_list) > 0):
                    return sms_list[0]["code"]
            else:
                print(response.status_code, response.text)
                return None
        print("{} 获取短信超过一分钟，停止！")
        return None
    
    """
    @description: 结束这个订单
    -------
    @param:
    -------
    @return:
    """
    def finish(self, order_id):
        # 路由
        route = "/finish/{}".format(str(order_id))
        # 请求
        response = self.execute_command(route)
        if (response.status_code == 200):
            return json.loads(response.text)
        else:
            print(response.status_code, response.text)
            return None


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    r_a_5sim = r_a_5sim()
    order_id = r_a_5sim.buy("russia", "any", "other")["id"]
    print(r_a_5sim.get_sms(str(order_id)))
    print(r_a_5sim.finish(str(order_id)))