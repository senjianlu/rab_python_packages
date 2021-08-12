#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_distributed_node.py
# @DATE: 2021/07/25 Sun
# @TIME: 14:54:27
#
# @DESCRIPTION: 分布式系统管理模块


import sys
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config


"""
@description: 获取当前机器的节点 ID
-------
@param:
-------
@return:
"""
def get_node_id():
    node_id = rab_config.load_package_config(
        "rab_config.ini", "rab_distributed_system", "node_id")
    return node_id

"""
@description: 获取此节点延迟
-------
@param:
-------
@return:
"""
def get_node_delay_time():
    # 获取节点所需要等待的单位时间
    node_delay_time = rab_config.load_package_config(
        "rab_config.ini", "rab_distributed_system", "node_delay_time")
    # 获取节点序号，除开 main 之外均需等待
    node_no = get_node_id().split("_")[-1]
    if ("main" ==  node_no.lower()):
        return 0
    elif(node_no.isdigit()):
        return int(node_delay_time)*int(node_no)
    else:
        return 0