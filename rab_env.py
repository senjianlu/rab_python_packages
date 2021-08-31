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
import sys
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config


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
def fix(moudule_name=None):
    # 没有包名的情况下默认安装所有
    if (not moudule_name):
        fix_env_by_yum()
        fix_env_by_pip()
    # rab_chrome 模块
    elif(moudule_name=="rab_chrome"):
        # 下载安装 Chrome 和对应版本的 chromedriver 并建立软连接
        fix_rab_chrome_command = rab_config.load_package_config(
            "rab_linux_command.ini", "rab_env", "fix_rab_chrome")
        os.system(fix_rab_chrome_command)