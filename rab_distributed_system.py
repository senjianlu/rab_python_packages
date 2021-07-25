#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_distributed_node.py
# @DATE: 2021/07/25 Sun
# @TIME: 14:54:27
#
# @DESCRIPTION: 分布式系统管理模块


# 切换路径到父级
import sys
sys.path.append("..")
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
    node_delay_time = rab_config.load_package_config(
        "rab_config.ini", "rab_distributed_system", "node_delay_time")
    return node_delay_time