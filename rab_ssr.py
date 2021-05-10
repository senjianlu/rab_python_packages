#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/Github/rab_python_packages/rab_ssr.py
# @DATE: 2021/05/10 Mon
# @TIME: 14:11:24
#
# @DESCRIPTION: 共通包 Linux 服务器端 SSR 订阅的使用
#               整体是对 https://github.com/senjianlu/auto-SSR-update 的封装


import base64
import requests
from urllib.parse import urlparse


"""
@description: 获取订阅的原始信息
-------
@param:
-------
@return:
"""
def get_subscription_origin_infos(subscription_urls):
    subscription_origin_infos = []
    for subscription_url in subscription_urls:
        try:
            # 默认对订阅链接的访问不使用代理
            response = requests.get(subscription_url, timeout=30)
            subscription_origin_infos.append(response.text)
        except Exception as e:
            print(subscription_url + " 获取订阅原始信息出错！" \
                  + "\r\n出错信息：" + str(e))
            break
    return subscription_origin_infos

"""
@description: BASE64 解码的封装
-------
@param:
-------
@return:
"""
def my_b64decode(str_4_b64decode):
    # 带 - 需要用专用的 URL BASE64 解码
    if ("-" in str_4_b64decode):
        # 最多加 4 次 "=" 以使原始信息符合 BASE64 格式
        for i in range(0, 4):
            try:
                str_after_b64decode = base64.urlsafe_b64decode(str_4_b64decode)
                break
            except Exception:
                str_4_b64decode = str_4_b64decode + "="
    # 不包含 - 则试用普通的 BASE64 解码即可
    else:
        # 最多加 4 次 "=" 以使原始信息符合 BASE64 格式
        for i in range(0, 4):
            try:
                str_after_b64decode = base64.b64decode(str_4_b64decode)
                break
            except Exception:
                str_4_b64decode = str_4_b64decode + "="
    return str_after_b64decode

"""
@description: 从订阅原始信息中拆分出每条 SSR 的原始信息
-------
@param:
-------
@return:
"""
def get_ssr_origin_infos(subscription_origin_infos):
    ssr_origin_infos = []
    for subscription_origin_info in subscription_origin_infos:
        # BASE64 解码
        subscription_info = my_b64decode(subscription_origin_info)
        # UTF-8 编码
        subscription_info = subscription_info.decode("UTF-8")
        # 根据换行符分行
        ssr_origin_infos_4_base64decode = subscription_info.split("\n")
        for ssr_origin_info_4_base64decode in ssr_origin_infos_4_base64decode:
            # 去掉最后一个分割出来的空字符
            if (ssr_origin_info_4_base64decode):
                info_4_base64decode = ssr_origin_info_4_base64decode \
                                        .replace("ssr://", "") \
                                        .replace("_", "/") \
                                        .replace("-", "+")
                try:
                    ssr_origin_info = my_b64decode(
                        info_4_base64decode).decode("UTF-8")
                    ssr_origin_infos.append(ssr_origin_info)
                except Exception:
                    print("SSR 原始信息 BASE64 解码失败：" \
                          + ssr_origin_info_4_base64decode)
                    continue
    return ssr_origin_infos

"""
@description: 解析 SSR 原始信息以获取具体的代理信息
-------
@param:
-------
@return:
"""
def parse_ssr_origin_info(ssr_origin_info):
    # === SSR 基础信息 ===
    # 服务器 IP
    ssr_ip = ssr_origin_info.split("/?")[0].split(":")[0]
    # 服务器端口
    ssr_port = ssr_origin_info.split("/?")[0].split(":")[1]
    # 密码
    ssr_password = my_b64decode(ssr_origin_info.split("/?")[0].split(":")[5]) \
                    .decode("UTF-8")
    # 加密（chacha20 加密 https://www.icode9.com/content-4-224432.html）
    ssr_method = ssr_origin_info.split("/?")[0].split(":")[3]
    # 协议
    ssr_protocol = ssr_origin_info.split("/?")[0].split(":")[2]
    # 混淆
    ssr_obfs = ssr_origin_info.split("/?")[0].split(":")[4]
    # === SSR 进阶参数 ===
    # 混淆参数
    ssr_obfs_param = my_b64decode(ssr_origin_info.split("/?")[1].split("&")[0] \
                        .split("=")[1]).decode("UTF-8")
    # 协议参数
    ssr_protocol_param = my_b64decode(ssr_origin_info.split("/?")[1] \
                            .split("&")[1].split("=")[1]).decode("UTF-8")
    # === SSR 其他信息 ===
    # 备注
    try:
        ssr_remarks = my_b64decode(ssr_origin_info.split("/?")[1]
                        .split("&")[2].split("=")[1]).decode("UTF-8")
    except Exception:
        ssr_remarks = ""
    # 分组
    try:
        ssr_group = my_b64decode(ssr_origin_info.split("/?")[1].split("&")[3] \
                        .split("=")[1]).decode("UTF-8")
    except Exception:
        ssr_group = ""
    # udpport
    try:
        ssr_udpport = ssr_origin_info.split("/?")[1].split("&")[4].split("=")[1]
    except Exception:
        ssr_udpport = ""
    # uot
    try:
        ssr_uot = ssr_origin_info.split("/?")[1].split("&")[5].split("=")[1]
    except Exception:
        ssr_uot = ""
    # 拼接
    ssr_info = {
        "server": ssr_ip,
        "server_port": ssr_port,
        "password": ssr_password,
        "method": ssr_method,
        "protocol": ssr_protocol,
        "protocol_param": ssr_protocol_param,
        "obfs": ssr_obfs,
        "obfs_param": ssr_obfs_param,
        "remarks": ssr_remarks,
        "group": ssr_group,
        "udpport": ssr_udpport,
        "uot": ssr_uot
    }
    return ssr_info

"""
@description: 解析 SSR 订阅链接并返回信息列表
-------
@param:
-------
@return:
"""
def parse_ssr_subscription_urls(subscription_urls):
    # 获取 SSR 订阅的原始信息并解码
    # subscription_urls = get_subscription_urls()
    subscription_origin_infos = get_subscription_origin_infos(subscription_urls)
    # 从订阅原始信息中拆分出每条 SSR 的原始信息
    ssr_origin_infos = get_ssr_origin_infos(subscription_origin_infos)
    # 逐条解析 SSR，以获得具体信息
    ssr_infos = []
    for ssr_origin_info in ssr_origin_infos:
        ssr_infos.append(parse_ssr_origin_info(ssr_origin_info))
    return ssr_infos


"""
@description: r_ssr 类
-------
@param:
-------
@return:
"""
class r_ssr:

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self,
                 subscription_urls,
                 ssr_config_path="/usr/local/share/shadowsocksr",
                 ssr_port=1080,
                 access_test_urls=[],
                 access_test_timeout=10,
                 proxy_location=["香港", "台湾"],
                 linkage_used_ips_limit=2):
        # SSR 订阅地址
        self.subscription_urls = subscription_urls
        # 本机 SSR config 配置文件所在路径
        self.ssr_config_path = ssr_config_path
        # 本机 SSR 开启的端口
        self.ssr_port = ssr_port
        # 测试能访问的站点
        self.access_test_urls = access_test_urls
        # 测试超时时间
        self.access_test_timeout = access_test_timeout
        # 限制代理区域等
        self.proxy_location = proxy_location
        # 当前 IP
        self.ip = None
        # 已经使用过的代理 IP 列表
        self.linkage_used_ips = []
        # 代理 IP 列表最大长度，如果为 2 的话则是在两个 IP 中循环
        self.linkage_used_ips_limit = linkage_used_ips_limit
    
    """
    @description: 修改 SSR 的配置文件
    -------
    @param:
    -------
    @return:
    """
    def update_ssr_config(self, ssr_info):
        try:
            # 获取 SSR 绑定的本地端口
            ssr_port_dict = {
                "local_port": self.ssr_port
            }
            # 读取既存配置并更新
            with open(self.ssr_config_path+"/config.json", "r") as f:
                origin_config_str = ""
                for line in f.readlines():
                    line = line.replace("\n", "").replace("\r", "").strip()
                    # 去掉双斜杠的数值
                    if ("//" in line):
                        line = line.split("//")[0]
                    if (line):
                        origin_config_str = origin_config_str + line
                origin_config = json.loads(origin_config_str)
                # 更新 SSR 代理信息
                origin_config.update(ssr_info)
                origin_config.update(ssr_port_dict)
                origin_config = json.dumps(origin_config,
                                           sort_keys=True,
                                           indent=4,
                                           separators=(',', ':'))
            # 开始写入更新后的代理信息
            with open(self.ssr_config_path+"/config.json", "w", \ 
                    encoding="UTF-8") as f:
                f.write(origin_config)
            print("已更新代理信息！代理信息：")
            print(ssr_info)
            return True
        except Exception as e:
            print("修改 SSR 的配置文件时出错！错误信息：" + str(e))
            return False
    
    """
    @description: 测试代理对测试网站是否可以访问
    -------
    @param:
    -------
    @return:
    """
    def test_ssr_access(self):
        proxy = {
            "http": "socks5://127.0.0.1:" + str(self.ssr_port),
            "https": "socks5://127.0.0.1:" + str(self.ssr_port)
        }
        for access_test_url in self.access_test_urls:
            try:
                response = requests.get(access_test_url,
                                        proxies=proxy,
                                        timeout=self.access_test_timeout)
                if (response.status_code == 200):
                    continue
                else:
                    print("测试代理访问网站失败！" + str(response.status_code))
                    return False
            except Exception as e:
                print("测试代理访问网站出错！错误信息：" + str(e))
                return False
        return True
    
    """
    @description: 测试代理是否满足限制条件
    -------
    @param:
    -------
    @return:
    """
    def test_proxy_limit(self):
        proxy = {
            "http": "socks5://127.0.0.1:" + str(self.ssr_port),
            "https": "socks5://127.0.0.1:" + str(self.ssr_port)
        }
        try:
            res = url = requests.get("http://ip-api.com/json/?lang=zh-CN",
                                     proxies=proxy,
                                     timeout=self.access_test_timeout)
            # 地域
            location = json.loads(res.text)["country"]
            # IP
            ip = json.loads(res.text)["query"]
            # 可以切换为代理的两个条件，缺一不可：
            # 1、代理在指定地域内
            # 2、代理 IP 不在已经使用过的 IP 列表中
            if (location in self.proxy_location
                    and ip not in self.linkage_used_ips):
                print("更新前 IP：" + str(self.linkage_used_ips))
                print("更新后 IP：" + ip)
                self.ip = ip
                return True
        except Exception as e:
            print("测试代理是否满足限制条件时出错！" + str(e))
        return False
    
    """
    @description: 更新操作
    -------
    @param:
    -------
    @return:
    """
    def update(self):
        ssr_infos = ssr_parser.parse_ssr_subscription_urls(
                        self.ssr_subscription_urls)
        # 为了防止出现没有更多的满足条件的 IP 的情况，使用 change_flg 加以判断
        change_flg = False
        # 循环每个代理信息
        for ssr_info in ssr_infos:
            # 修改 ssr_config 并测试是否可以网页
            self.update_ssr_config(ssr_info)
            # 重启 SSR
            os.system("ssr stop")
            os.system("ssr start")
            # 首先测试该代理是否满足限制条件
            if (self.test_proxy_limit()):
                # 测试此代理是否可以访问所有测试页面
                if (self.test_ssr_access()):
                    print("代理测试通过！当前代理信息：")
                    print(ssr_info)
                    change_flg = True
                    break
        return change_flg

    """
    @description: 带判断的主更新操作
    -------
    @param:
    -------
    @return:
    """
    def do_update(self)
        change_flg = self.update()
        # 判断是否进行了更改
        if (change_flg):
            self.linkage_used_ips.append(self.ip)
            if (len(self.linkage_used_ips) > self.linkage_used_ips_limit):
                self.linkage_used_ips.pop(0)
        else:
            self.linkage_used_ips = []
            # 如果还是没有更新 SSR 信息，说明出了问题
            if (not self.update()):
                return False
        return True

