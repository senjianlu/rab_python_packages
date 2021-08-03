#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_storage.py
# @DATE: 2021/07/22 Thu
# @TIME: 13:55:25
#
# @DESCRIPTION: 静态资源上传下载共通模块


import os
import sys
import minio
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config


"""
@description: r_storage 存储类
-------
@param:
-------
@return:
"""
class r_storage():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self):
        # 各个存储站的 Clinet
        self.clinet = {}
        # 静态资源存储站状态
        self.status = {}
        self.check_status()

    """
    @description: 通过配置文件检查存储桶状态
    -------
    @param:
    -------
    @return:
    """
    def check_status(self):
        # MinIO 状态检查
        minio_host = rab_config.load_package_config(
            "rab_config.ini", "rab_storage", "minio_host").lower()
        if (minio_host):
            # 检查是否需要使用了 HTTPS
            if ("https" in minio_host):
                minio_secure = True
                minio_host = minio_host.replace("https://", "")
            elif("http" in minio_host):
                minio_secure = False
                minio_host = minio_host.replace("http://", "")
            # 读取用户名和密码
            minio_user = rab_config.load_package_config(
                "rab_config.ini", "rab_storage", "minio_user")
            minio_password = rab_config.load_package_config(
                "rab_config.ini", "rab_storage", "minio_password")
            # 拼接为连接信息
            minio_conf = {
                "endpoint": minio_host,
                "access_key": minio_user,
                "secret_key": minio_password,
                "secure": minio_secure
            }
            # 尝试连接
            print("MinIO 尝试连接信息：", \
                minio_host, minio_user, minio_password, minio_secure)
            try:
                minio_clint = minio.Minio(**minio_conf)
                minio_buckets = minio_clint.list_buckets()
                # 存储信息
                self.status["minio"] = True
                self.clinet["minio"] = minio_clint
            except Exception as e:
                print("MinIO 尝试连接出错！" + str(e))
    
    """
    @description: 判断文件是否存在
    -------
    @param:
    -------
    @return:
    """
    def object_exists(self, origin_file_path, origin):
        # 存储桶名
        bucket_name = origin_file_path.split("/")[0]
        # 文件名
        origin_file_name = origin_file_path.split("/")[-1]
        # 文件在存储桶中的路径
        origin_file_prefix = origin_file_path.lstrip(
            bucket_name+"/").rstrip(origin_file_name)
        # 检查文件是否存在
        objects = self.clinet[origin].list_objects(
            bucket_name, prefix=origin_file_prefix)
        for obj in objects:
            # 路径+文件名 == 存储桶中的文件名
            if (origin_file_prefix+origin_file_name == obj.object_name):
                return True, bucket_name, origin_file_prefix, origin_file_name
        return False, bucket_name, origin_file_prefix, origin_file_name
        
    """
    @description: 下载文件
    -------
    @param:
    -------
    @return:
    """
    def download(self, origin_file_path, local_file_path=None, origin="minio"):
        # 文件是否存在和获取存储桶、路径等信息
        exist_flg, bucket_name, origin_file_prefix, origin_file_name = \
            self.object_exists(origin_file_path, origin)
        # 如果存在该文件
        if (exist_flg):
            # 如果没有指定下载路径
            if (not local_file_path):
                local_file_path = origin_file_name
            # 下载
            try:
                print(origin_file_name + " 下载中......")
                self.clinet[origin].fget_object(bucket_name,
                    origin_file_prefix+origin_file_name, local_file_path)
                print(origin_file_name + " 下载完成！" + local_file_path)
                return True, local_file_path
            except Exception as e:
                print(origin_file_name + " 下载出错！" + str(e))
        # 如果不存在该文件
        else:
            print("文件不存在！文件路径信息：")
            print(origin, bucket_name, origin_file_prefix, origin_file_name)
        # 下载失败
        return False, None

    """
    @description: 上传文件
    -------
    @param:
    -------
    @return:
    """
    def upload(self, to_file_path, local_file_path, origin="minio"):
        # 文件是否存在和获取存储桶、路径等信息
        exist_flg, bucket_name, to_file_prefix, to_file_name = \
            self.object_exists(to_file_path, origin)
        # 如果不存在则上传
        if (not exist_flg):
            # 判断本地文件是否存在
            if (os.path.exists(local_file_path)):
                # 尝试上传f
                try:
                    print(local_file_path + " 上传中......")
                    self.clinet[origin].fput_object(bucket_name,
                        to_file_prefix+to_file_name, local_file_path)
                    print(local_file_path + " 上传完成！" + to_file_path)
                except Exception as e:
                    print(local_file_path + " 上传出错！" + str(e))
            else:
                print("本地文件不存在！路径：" + local_file_path)
        # 如果存在则不上传
        else:
            print("文件已经存在！文件路径信息：")
            print(origin, bucket_name, to_file_prefix, to_file_name)
        # 上传失败
        return False, None


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    pass