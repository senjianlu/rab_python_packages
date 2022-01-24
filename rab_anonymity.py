#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_anonymity.py
# @DATE: 2022/01/24 Mon
# @TIME: 15:06:30
#
# @DESCRIPTION: 共通匿名模块


import random


"""
@description: 获取随机的 User-Agent
-------
@param:
-------
@return:
"""
def get_random_user_agent():
    # 浏览器信息
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.15 Safari/537.36 Core/1.53.3368.400 QQBrowser/9.6.11974.400",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.15 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.15 Safari/537.36 Mozilla/5.0 (Windows NT 6.1; WOW64 Trident/7.0; rv:11.0) like Gecko Windows NT 6.1; Trident/5.0; InfoPath.2; QIHU 360EE)",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Mozilla/5.0 (Windows NT 6.1; WOW64 Trident/7.0; rv:11.0) like Gecko Windows NT 6.1; Trident/5.0; InfoPath.2; QIHU 360EE)"
    ]
    return random.choice(user_agents)