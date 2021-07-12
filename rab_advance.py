#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_advance.py
# @DATE: 2021/07/12 Mon
# @TIME: 14:51:13
#
# @DESCRIPTION: 自用进阶方法


import base64
import requests
# 切换路径到父级
import sys
sys.path.append("..")
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
                 username=None,
                 password=None,
                 host=None,
                 port=None,
                 domain=None):
        # 初始化判断
        if (not (username and password and host and port)):
            configuration_items = [
                "rapo_username", "rapo_password", "rapo_host", "rapo_port", \
                    "rapo_domain"]
            username, password, host, port, domain = rab_config \
                .load_package_config("rab_advance", configuration_items)
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
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    pass