#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/steammarket/rab_python_packages/rab_docker.py
# @DATE: 2021/08/07 Sat
# @TIME: 16:03:08
#
# @DESCRIPTION: Docker 容器管理模块


import docker


# 主 Client
client = docker.from_env()


"""
@description: 获取 Client
-------
@param:
-------
@return:
"""
def get_client():
    return client

"""
@description: 获取所有正在允许的 Docker 容器
-------
@param:
-------
@return:
"""
def get_containers(image_keyword=None, name_keyword=None):
    containers = client.containers.list(all=True)
    # 根据镜像名或关键词来筛选
    if (image_keyword):
        filtered_containers = []
        for container in containers:
            if (image_keyword.lower() in str(container.image).lower()):
                filtered_containers.append(container)
        containers = filtered_containers
    # 根据容器名或关键词来筛选
    if (name_keyword):
        filtered_containers = []
        for container in containers:
            if (name_keyword.lower() in str(container.name).lower()):
                filtered_containers.append(container)
        containers = filtered_containers
    # 如果没有筛选条件则直接返回
    return containers


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    for container in get_containers():
        print(container.name)