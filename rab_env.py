#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_env.py
# @DATE: 2021/07/15 Thu
# @TIME: 16:31:00
#
# @DESCRIPTION: 运行环境的检测和修复，包括 Docker 镜像的下载和加载等


import os


"""
@description: 查找文件
-------
@param:
-------
@return:
"""
def find_rab_file(rab_file_name):
    paths = [
        # 判断该路径下配置文件是否存在
        None,
        # 不在的话就在共通包中查找
        "rab_python_packages/",
        # 或者在上级路径的共通包中查找
        "../rab_python_packages/"
    ]
    for path in paths:
        if (path):
            if (os.path.exists(path+rab_file_name)):
                return path + rab_file_name
        else:
            if (os.path.exists(rab_file_name)):
                return rab_file_name

"""
@description: 环境安装 Yum
-------
@param:
-------
@return:
"""
def fix_env_by_yum():
    dependence_list = ["epel-release", "postgresql-devel"]
    for dependence in dependence_list:
        print("Yum 开始安装：" + dependence)
        command = "yum -y install " + dependence
        os.system(command)

"""
@description: 环境安装 pip
-------
@param:
-------
@return:
"""
def fix_env_by_pip():
    file_name = "rab_requirements.txt"
    file_path = find_rab_file(file_name)
    print("pip 开始从文件 " + file_path + " 开始安装！")
    command = "pip3 install -r " + file_path
    os.system(command)

"""
@description: 安装运行环境
-------
@param:
-------
@return:
"""
def fix():
    fix_env_by_yum()
    fix_env_by_pip()