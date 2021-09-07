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
import xml
import json
import minio
import urllib
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
def minio_connect():
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
        "secure": minio_secure,
        "region": "us-east-1"
    }
    # 尝试连接
    r_logger.info("开始连接至 MinIO 存储源站......")
    try:
        minio_client = minio.Minio(**minio_conf)
        minio_buckets = minio_client.list_buckets()
        r_logger.info("MinIO 连接成功")
        return minio_client
    except Exception as e:
        r_logger.error("MinIO 尝试出错！")
        r_logger.error(e)
    return None

"""
@description: MinIO 文件是否存在
-------
@param:
-------
@return:
"""
def minio_exist(file_path, client):
    # 存储桶名
    bucket_name = file_path.split("/")[0]
    # 文件名
    file_name = file_path.split("/")[-1]
    # 文件在存储桶中的路径
    file_prefix = file_path.lstrip(bucket_name+"/").rstrip(file_name)
    # 检查文件是否存在
    objects = client.list_objects(bucket_name, prefix=file_prefix)
    for obj in objects:
        # 路径+文件名 == 存储桶中的文件名
        if ((file_prefix+file_name) == obj.object_name):
            return True, file_path
    return False, None

"""
@description: MinIO 检查文件路径是否安全
-------
@param:
-------
@return:
"""
def minio_check(file_path, client):
    # MinIO 在上传创建对象时会自动创建没有的路径
    return True, file_path

"""
@description: 上传至 MinIO
-------
@param:
-------
@return:
"""
def minio_upload(to_file_path, local_file_path, client):
    # 存储桶名
    to_bucket_name = to_file_path.split("/")[0]
    # 文件名
    to_file_name = to_file_path.split("/")[-1]
    # 文件在存储桶中的路径
    to_file_prefix = to_file_path.lstrip(
        to_bucket_name+"/").rstrip(to_file_name)
    try:
        # 上传文件
        client.fput_object(to_bucket_name, (to_file_prefix+to_file_name), \
            local_file_path)
        return True, to_file_path
    except Exception as e:
        r_logger.error("MinIO 上传出错！")
        r_logger.error(e)
    return False, None

"""
@description: 从 MinIO 下载
-------
@param:
-------
@return:
"""
def minio_download(from_file_path, local_file_path, client):
    # 存储桶名
    from_bucket_name = from_file_path.split("/")[0]
    # 文件名
    from_file_name = from_file_path.split("/")[-1]
    # 文件在存储桶中的路径
    from_file_prefix = from_file_path.lstrip(
        from_bucket_name+"/").rstrip(from_file_name)
    try:
        # 下载文件
        client.fget_object(from_bucket_name, \
            (from_file_prefix+from_file_name), local_file_path)
        return True, local_file_path
    except Exception as e:
        r_logger.error("MinIO 下载出错！")
        r_logger.error(e)
    return False, None

"""
@description: 从 MinIO 分享
-------
@param:
-------
@return:
"""
def minio_share(file_path, client):
    # MinIO IP 或域名
    minio_host = rab_config.load_package_config(
        "rab_config.ini", "rab_storage", "minio_host").lower()
    share_url = "{minio_host}/{file_path}".format(
        minio_host=minio_host, file_path=file_path)
    return True, share_url

"""
@description: 连接至腾讯云 COS
-------
@param:
-------
@return:
"""
def cos_connect():
    # todo...
    return None

"""
@description: COS 文件是否存在
-------
@param:
-------
@return:
"""
def cos_exist(file_path, client):
    # todo...
    return False, None

"""
@description: COS 检查文件路径是否安全
-------
@param:
-------
@return:
"""
def cos_check(file_path, client):
    # todo...
    return False, None

"""
@description: 上传至 COS
-------
@param:
-------
@return:
"""
def cos_upload(to_file_path, local_file_path, client):
    # todo...
    return False, None

"""
@description: 从 COS 下载
-------
@param:
-------
@return:
"""
def cos_download(from_file_path, local_file_path, client):
    # todo...
    return False, None

"""
@description: 从 COS 分享
-------
@param:
-------
@return:
"""
def cos_share(file_path, client):
    # todo...
    return False, None

"""
@description: 连接至 Nextcloud
-------
@param:
-------
@return:
"""
def nextcloud_connect():
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
    # 动作：获取路径下的所有文件
    nextcloud_client.add_action("list", method="PROPFIND", \
        route="/remote.php/dav/files/{user}/{path}",
        basic_params={"format": "json"})
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
    # 动作：获取所有已分享的文件信息
    nextcloud_client.add_action("get_all_shares", method="GET", \
        route="/ocs/v2.php/apps/files_sharing/api/v1/shares",
        basic_params={"format": "json"})
    # 动作：获取指定路径下所有已分享的文件信息
    nextcloud_client.add_action("get_shares_from_path", method="GET", \
        route="/ocs/v2.php/apps/files_sharing/api/v1/shares",
        basic_params={"format": "json", "reshares": "true", "subfiles": "true"})
    return nextcloud_client

"""
@description: Nextcloud 文件是否存在
-------
@param:
-------
@return:
"""
def nextcloud_exist(file_path, client):
    # 文件名
    file_name = file_path.split("/")[-1]
    # 文件路径
    file_prefix = file_path.rstrip(file_name)
    # 执行查询
    nextcloud_response = client.do_action("list", \
        _format={"user": client.auth[0], "path": file_prefix})
    nextcloud_response_str = urllib.parse.unquote(
        nextcloud_response.content.decode("UTF-8"))
    # 转为 XML 对象
    xml_obj = xml.etree.ElementTree.fromstring(nextcloud_response_str)
    file_paths = []
    for href in xml_obj.iter("{DAV:}href"):
        basic_href="/remote.php/dav/files/{}/".format(client.auth[0])
        file_paths.append(href.text.replace(basic_href, ""))
    if (file_path in file_paths):
        return True, file_path
    else:
        return False, None

"""
@description: Nextcloud 检查文件路径是否安全
-------
@param:
-------
@return:
"""
def nextcloud_check(file_path, client):
    # 文件名
    file_name = file_path.split("/")[-1]
    # 文件路径
    file_prefix = file_path.rstrip(file_name)
    # 循环确认每个父文件夹
    _prefix = ""
    try:
        for file_prefix_part in file_prefix.split("/"):
            if (file_prefix_part):
                _prefix += "/{}".format(file_prefix_part)
                nextcloud_response = client.do_action("create_folder", \
                    _format={"user": client.auth[0], "folder_path": _prefix})
        return True, file_path
    except Exception as e:
        r_logger.error("Nextcloud 新建文件夹 {} 出错！".format(_prefix))
        r_logger.error(e)
    return False, None

"""
@description: 上传至 Nextcloud
-------
@param:
-------
@return:
"""
def nextcloud_upload(to_file_path, local_file_path, client):
    try:
        # 执行上传
        nextcloud_response = client.do_action("upload", \
            _format={"user": client.auth[0], "path": to_file_path}, \
            data=open(local_file_path, "rb"))
        return True, to_file_path
    except Exception as e:
        r_logger.error("Nextcloud 上传出错！")
        r_logger.error(e)
    return False, None

"""
@description: 从 Nextcloud 下载
-------
@param:
-------
@return:
"""
def nextcloud_download(from_file_path, local_file_path, client):
    try:
        # 执行下载
        nextcloud_response = client.do_action("download", \
            _format={"user": client.auth[0], "path": to_file_path}, \
            data=open(local_file_path, "rb"))
        # 写入文件
        with open(local_file_path, "wb") as local_file:
            local_file.write(nextcloud_response.content)
        return True, local_file_path
    except Exception as e:
        r_logger.error("Nextcloud 下载出错！")
        r_logger.error(e)
    return False, None

"""
@description: 从 Nextcloud 分享
-------
@param:
-------
@return:
"""
def nextcloud_share(file_path, client):
    # 文件名
    file_name = file_path.split("/")[-1]
    # 文件路径
    file_prefix = file_path.rstrip(file_name)
    # 获取当前已经分享的文件
    nextcloud_response = client.do_action(
        "get_shares_from_path", params={"path": file_prefix})
    # 如果有现场的分享就直接使用
    if (json.loads(nextcloud_response.text)["ocs"]["meta"]["status"].lower()
            == "ok"):
        nextcloud_response_str = nextcloud_response.content.decode("UTF-8")
        shares = json.loads(nextcloud_response_str)["ocs"]["data"]
        for share in shares:
            if (share["path"].lstrip("/") == file_path):
                return True, share["url"]
    # 文件没有被分享过则新建分享
    nextcloud_response = client.do_action("create_share", \
        params={"path": file_path, "shareType": 3})
    return True, json.loads(
        nextcloud_response.content.decode("UTF-8"))["ocs"]["data"]["url"]


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
    def __init__(self, origins=["MinIO", "COS", "Nextcloud"]):
        # 存储源站
        self.origins = origins
        # 静态资源存储站状态
        self.status = {}
        # 各个存储站的 Client
        self.client = {}
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
        for origin in self.origins:
            # 如果有该存储源的配置文件
            host = rab_config.load_package_config(
                "rab_config.ini", "rab_storage", "{}_host".format(
                    origin.lower())).lower()
            if (host):
                # MinIO
                if (origin.lower() == "minio"):
                    client = minio_connect()
                # COS
                elif(origin.lower() == "cos"):
                    client = cos_connect()
                # Nextcloud
                elif(origin.lower() == "nextcloud"):
                    client = nextcloud_connect()
                # 判断是否连接成功
                if (client):
                    self.client[origin.lower()] = client
                    self.status[origin.lower()] = True
                else:
                    self.status[origin.lower()] = False
            else:
                r_logger.error(
                    "配置文件中没有 {} 存储源站的连接信息！".format(origin))
        
    """
    @description: 判断文件是否存在
    -------
    @param:
    -------
    @return:
    """
    def exist(self, file_path):
        # 结果
        result = {}
        # 所有需要判断的存储源
        for origin in self.origins:
            # 判断是否连接
            if (not self.status[origin.lower()]):
                r_logger.warn("{} 未连接！".format(origin))
            # 开始判断
            result[origin.lower()] = {}
            exist_flg = False
            _file_path = None
            # MinIO
            if (origin.lower() == "minio"):
                exist_flg, _file_path = minio_exist(
                    file_path, self.client["minio"])
            # COS
            elif(origin.lower() == "cos"):
                exist_flg, _file_path = cos_exist(
                    file_path, self.client["nextcloud"])
            # Nextcloud
            elif(origin.lower() == "nextcloud"):
                exist_flg, _file_path = nextcloud_exist(
                    file_path, self.client["nextcloud"])
            # 文件判断结束
            result[origin.lower()]["is_exist"] = exist_flg
            result[origin.lower()]["file_path"] = _file_path
        return result
    
    """
    @description: 检查文件（文件路径是否存在，不在则新建）
    -------
    @param:
    -------
    @return:
    """
    def check(self, file_path):
        # 结果
        result = {}
        # 所有需要检查的存储源
        for origin in self.origins:
            result[origin.lower()] = {}
            # MinIO
            if (origin.lower() == "minio"):
                check_flg, _file_path = minio_check(file_path, \
                    self.client[origin.lower()])
            # COS
            elif(origin.lower() == "cos"):
                check_flg, _file_path = cos_check(file_path, \
                    self.client[origin.lower()])
            # Nextcloud
            elif(origin.lower() == "nextcloud"):
                check_flg, _file_path = nextcloud_check(file_path, \
                    self.client[origin.lower()])
            # 文件检查完成
            result[origin.lower()]["check_flg"] = check_flg
            result[origin.lower()]["file_path"] = _file_path
        return result


    """
    @description: 上传文件
    -------
    @param:
    -------
    @return:
    """
    def upload(self, to_file_path, local_file_path):
        # 结果
        result = {}
        # 上传前检查文件路径
        origin_check = self.check(to_file_path)
        # 判断存储源文件是否存在
        origin_exist = self.exist(to_file_path)
        # 本地文件是否存在
        if (not os.path.exists(local_file_path)):
            r_logger.warn("{} 文件不存在！".format(local_file_path))
            return False, None
        # 所有需要上传的存储源
        for origin in self.origins:
            print(self.origins, to_file_path, local_file_path)
            result[origin.lower()] = {}
            # 文件路径检查未通过
            if (not origin_check[origin.lower()]["check_flg"]):
                result[origin.lower()]["is_exist"] = False
                result[origin.lower()]["upload_flg"] = False
                result[origin.lower()]["file_path"] = None
                continue
            # 存储源是否已存在文件（其中有判断是否连接的过程）
            if (origin_exist[origin.lower()]["is_exist"]):
                result[origin.lower()]["is_exist"] = True
                result[origin.lower()]["upload_flg"] = False
                result[origin.lower()]["file_path"] = None
                continue
            # 开始上传，失败传回空文件路径
            upload_flg = False
            _to_file_path = None
            # MinIO
            if (origin.lower() == "minio"):
                upload_flg, _to_file_path = minio_upload(to_file_path, \
                    local_file_path, self.client[origin.lower()])
            # COS
            elif(origin.lower() == "cos"):
                upload_flg, _to_file_path = cos_upload(to_file_path, \
                    local_file_path, self.client[origin.lower()])
            # Nextcloud
            elif(origin.lower() == "nextcloud"):
                upload_flg, _to_file_path = nextcloud_upload(to_file_path, \
                    local_file_path, self.client[origin.lower()])
            # 文件上传完成
            result[origin.lower()]["is_exist"] = False
            result[origin.lower()]["upload_flg"] = upload_flg
            result[origin.lower()]["file_path"] = _to_file_path
        return result
    
    """
    @description: 下载文件
    -------
    @param:
    -------
    @return:
    """
    def download(self, from_file_path, local_file_path):
        # 判断存储源文件是否存在
        origin_exist = self.exist(from_file_path)
        # 本地文件是否存在
        if (os.path.exists(local_file_path)):
            r_logger.warn("本地 {} 文件已存在！".format(local_file_path))
            return False, None
        # 所有可下载的存储源
        for origin in self.origins:
            # 存储源是否存在文件（其中有判断是否连接的过程），不存在就跳过
            if (not origin_exist[origin.lower()]["is_exist"]):
                r_logger.warn("{origin} 源 {from_file_path} 文件不存在！".format(
                    origin=origin, from_file_path=from_file_path))
                continue
            # MinIO
            if (origin.lower() == "minio"):
                download_flg, _local_file_path = minio_download(from_file_path, \
                    local_file_path, self.client[origin.lower()])
            # COS
            elif(origin.lower() == "cos"):
                download_flg, _local_file_path = cos_download(
                    from_file_path, local_file_path, self.client[origin.lower()])
            # Nextcloud
            elif(origin.lower() == "nextcloud"):
                download_flg, _local_file_path = nextcloud_download(
                    from_file_path, local_file_path, self.client[origin.lower()])
            # 下载成功就返回，失败则使用下一个源
            if (download_flg):
                return download_flg, _local_file_path
            else:
                continue
        # 所有源都下载失败，返回失败和空路径
        return False, None
    
    """
    @description: 分享文件
    -------
    @param:
    -------
    @return:
    """
    def share(self, file_path):
        # 结果
        result = {}
        # 判断存储源文件是否存在
        origin_exist = self.exist(file_path)
        # 所有需要分享的文件路径
        for origin in self.origins:
            result[origin.lower()] = {}
            # 存储源是否已存在文件（其中有判断是否连接的过程）
            if (not origin_exist[origin.lower()]["is_exist"]):
                result[origin.lower()]["is_exist"] = False
                result[origin.lower()]["share_url"] = None
                continue
            # MinIO
            if (origin.lower() == "minio"):
                share_url = minio_share(file_path, self.client[origin.lower()])
            # COS
            elif(origin.lower() == "cos"):
                share_url = cos_share(file_path, self.client[origin.lower()])
            # Nextcloud
            elif(origin.lower() == "nextcloud"):
                share_url = nextcloud_share(
                    file_path, self.client[origin.lower()])
            # 文件分享完成
            result[origin.lower()]["is_exist"] = False
            result[origin.lower()]["share_url"] = share_url
        return result


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    # 存储类中方法测试
    r_storage = r_storage(origins=["MinIO", "Nextcloud"])
    # 检查文件存在
    # print(r_storage.exist("test/rab_python_packages.png"))
    # 检查文件不存在
    # print(r_storage.exist("test/not_exist.png"))
    # 检查路径
    # print(r_storage.check("test/check_folder.png"))
    # 新建路径
    # print(r_storage.check("test/new/check_folder.png"))
    # 上传图片
    print(r_storage.upload("test/new/README.md", "README.md"))
    print(r_storage.upload("test/new/new/README.md", "README.md"))
    # 下载图片
    # print(r_storage.download("test/new/README.md", "README_new.md"))