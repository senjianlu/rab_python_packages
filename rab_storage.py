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
import requests
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_logging
from rab_python_packages import rab_client


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: 连接至 MinIO
-------
@param:
-------
@return:
"""
def connect_minio():
    # MinIO IP 或域名
    minio_host = rab_config.load_package_config(
        "rab_config.ini", "rab_storage", "minio_host").lower()
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
    r_logger.info("开始连接至 MinIO 存储源站......")
    try:
        minio_clint = minio.Minio(**minio_conf)
        minio_buckets = minio_clint.list_buckets()
        r_logger.info("MinIO 连接成功")
        return minio_clint
    except Exception as e:
        r_logger.error("MinIO 尝试出错！")
        r_logger.error(e)
    return None

"""
@description: 连接至腾讯云 COS
-------
@param:
-------
@return:
"""
def connect_cos():
    pass

"""
@description: 连接至 Nextcloud
-------
@param:
-------
@return:
"""
def connect_nextcloud():
    # Nextcloud IP 或域名
    nextcloud_host = rab_config.load_package_config(
        "rab_config.ini", "rab_storage", "nextcloud_host").lower()
    # 读取用户名和密码
    nextcloud_user = rab_config.load_package_config(
        "rab_config.ini", "rab_storage", "nextcloud_user")
    nextcloud_password = rab_config.load_package_config(
        "rab_config.ini", "rab_storage", "nextcloud_password")
    # 请求头
    headers = {
        "OCS-APIRequest": "true",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/" \
            + "537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36",
        "referrer-policy": "no-referrer"
    }
    # 建立连接
    nextcloud_client = rab_client.r_client(basic_url=nextcloud_host, \
        auth=(nextcloud_user, nextcloud_password), \
        headers=headers)
    # 动作：获取所有已分享的文件信息
    nextcloud_client.add_action("get_all_shares", method="GET", \
        route="/ocs/v2.php/apps/files_sharing/api/v1/shares",
        basic_params={"format": "json"})
    # 动作：获取指定路径下所有已分享的文件信息
    nextcloud_client.add_action("get_shares_from_path", method="GET", \
        route="/ocs/v2.php/apps/files_sharing/api/v1/shares",
        basic_params={"format": "json", "reshares": "true", "subfiles": "true"})
    # 动作：创建一个文件夹
    nextcloud_client.add_action("create_folder", method="MKCOL", \
        route="/remote.php/dav/files/{user}/{folder_path}")
    # 动作：上传文件
    nextcloud_client.add_action("upload", method="PUT", \
        route="/remote.php/dav/files/{user}/{path}")
    # 动作：下载文件
    nextcloud_client.add_action("download", method="GET", \
        route="/remote.php/dav/files/{user}/{path}")
    # 动作：分享文件
    nextcloud_client.add_action("create_share", method="POST", \
        route="/ocs/v2.php/apps/files_sharing/api/v1/shares",
        basic_params={"format": "json"})
    return nextcloud_client


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
    def __init__(self, origins=["minio", "cos", "nextcloud"]):
        # 存储源站
        self.origins = origins
        # 静态资源存储站状态
        self.status = {}
        # 各个存储站的 Clinet
        self.clinet = {}
        # 开启与各源站间的连接
        self.connect()

    """
    @description: 开启与各源站间的连接
    -------
    @param:
    -------
    @return:
    """
    def connect(self):
        for origin in origins:
            # MinIO
            if (origin.lower() == "minio"):
                minio_host = rab_config.load_package_config(
                    "rab_config.ini", "rab_storage", "minio_host").lower()
                if (minio_host):
                    # 连接
                    minio_clint = minio_connect()
                    if (minio_clint):
                        self.clinet["minio"] = minio_clint
                        self.status["minio"] = True
                    else:
                        self.status["minio"] = False
                else:
                    r_logger.error("配置文件中没有 MinIO 存储源站的连接信息！")
            # COS
            if (origin.lower() == "cos"):
                pass
            # Nextcloud
            if (origin.lower() == "nextcloud"):
                pass

    
    # """
    # @description: 判断文件是否存在
    # -------
    # @param:
    # -------
    # @return:
    # """
    # def object_exists(self, origin_file_path, origin):
    #     # 存储桶名
    #     bucket_name = origin_file_path.split("/")[0]
    #     # 文件名
    #     origin_file_name = origin_file_path.split("/")[-1]
    #     # 文件在存储桶中的路径
    #     origin_file_prefix = origin_file_path.lstrip(
    #         bucket_name+"/").rstrip(origin_file_name)
    #     # 检查文件是否存在
    #     objects = self.clinet[origin].list_objects(
    #         bucket_name, prefix=origin_file_prefix)
    #     for obj in objects:
    #         # 路径+文件名 == 存储桶中的文件名
    #         if (origin_file_prefix+origin_file_name == obj.object_name):
    #             return True, bucket_name, origin_file_prefix, origin_file_name
    #     return False, bucket_name, origin_file_prefix, origin_file_name
        
    # """
    # @description: 下载文件
    # -------
    # @param:
    # -------
    # @return:
    # """
    # def download(self, origin_file_path, local_file_path=None, origin="minio"):
    #     # 文件是否存在和获取存储桶、路径等信息
    #     exist_flg, bucket_name, origin_file_prefix, origin_file_name = \
    #         self.object_exists(origin_file_path, origin)
    #     # 如果存在该文件
    #     if (exist_flg):
    #         # 如果没有指定下载路径
    #         if (not local_file_path):
    #             local_file_path = origin_file_name
    #         # 下载
    #         try:
    #             print(origin_file_name + " 下载中......")
    #             self.clinet[origin].fget_object(bucket_name,
    #                 origin_file_prefix+origin_file_name, local_file_path)
    #             print(origin_file_name + " 下载完成！" + local_file_path)
    #             return True, local_file_path
    #         except Exception as e:
    #             print(origin_file_name + " 下载出错！" + str(e))
    #     # 如果不存在该文件
    #     else:
    #         print("文件不存在！文件路径信息：")
    #         print(origin, bucket_name, origin_file_prefix, origin_file_name)
    #     # 下载失败
    #     return False, None

    # """
    # @description: 上传文件
    # -------
    # @param:
    # -------
    # @return:
    # """
    # def upload(self, to_file_path, local_file_path, origin="minio"):
    #     # 文件是否存在和获取存储桶、路径等信息
    #     exist_flg, bucket_name, to_file_prefix, to_file_name = \
    #         self.object_exists(to_file_path, origin)
    #     # 如果不存在则上传
    #     if (not exist_flg):
    #         # 判断本地文件是否存在
    #         if (os.path.exists(local_file_path)):
    #             # 尝试上传f
    #             try:
    #                 print(local_file_path + " 上传中......")
    #                 self.clinet[origin].fput_object(bucket_name,
    #                     to_file_prefix+to_file_name, local_file_path)
    #                 print(local_file_path + " 上传完成！" + to_file_path)
    #             except Exception as e:
    #                 print(local_file_path + " 上传出错！" + str(e))
    #         else:
    #             print("本地文件不存在！路径：" + local_file_path)
    #     # 如果存在则不上传
    #     else:
    #         print("文件已经存在！文件路径信息：")
    #         print(origin, bucket_name, to_file_prefix, to_file_name)
    #     # 上传失败
    #     return False, None


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    nextcloud_client = connect_nextcloud()
    # r = nextcloud_client.do_action(
    #     "create_share",
    #     params={
    #         "path": "test/test.jpg",
    #         "shareType": 3
    #     })
    r = nextcloud_client.do_action("download", _format={
        "user": nextcloud_client.auth[0], "path": "test/test.jpg"})
    with open("test.jpg", "wb") as f:
        f.write(r.content)
    print(r.status_code)