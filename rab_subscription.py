#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/Github/rab_python_packages/rab_ssr.py
# @DATE: 2021/05/10 Mon
# @TIME: 14:11:24
#
# @DESCRIPTION: 共通包 Linux 系统下解析机场订阅，并通过 Docker 部署客户端
#               与 rab_proxy 模块不同的是，这里将“域名_端口”作为主键进行区分而非 IP


import os
import time
import json
import base64
import docker
import requests
from urllib.parse import urlparse
# 切换路径到父级
import sys
sys.path.append("..")
from rab_python_packages import rab_config


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
        # 不使用代理、使用上次的 SSR 节点、使用备用节点来访问订阅地址
        try:
            # 不使用代理访问订阅链接
            response = requests.get(subscription_url, timeout=30)
            subscription_origin_infos.append(response.text)
        except Exception as e:
            print(subscription_url + " 不使用代理获取订阅原始信息出错！" \
                + "\r\n出错信息：" + str(e))
    return subscription_origin_infos
            
"""
@description: 用以订阅信息 BASE64 解码的封装
-------
@param:
-------
@return:
"""
def b64decode_4_subscription(str_4_b64decode):
    # 带 - 需要用专用的 URL BASE64 解码
    if ("-" in str_4_b64decode):
        # 最多加 4 次 "=" 以使原始信息符合 BASE64 格式
        for i in range(0, 4):
            try:
                str_after_b64decode = base64.urlsafe_b64decode(str_4_b64decode)
                return str_after_b64decode
            except Exception:
                str_4_b64decode = str_4_b64decode + "="
    # 不包含 - 则试用普通的 BASE64 解码即可
    else:
        # 最多加 4 次 "=" 以使原始信息符合 BASE64 格式
        for i in range(0, 4):
            try:
                str_after_b64decode = base64.b64decode(str_4_b64decode)
                return str_after_b64decode
            except Exception:
                str_4_b64decode = str_4_b64decode + "="
    # 解码失败
    print(str_4_b64decode, "BASE64 解码失败！")
    return None

"""
@description: 从解码后的订阅原始信息中拆分出每个节点的信息
-------
@param:
-------
@return:
"""
def get_node_infos(subscription_info):
    node_infos = {
        "ssr": [],
        "vmess": [],
        "ss": []
    }
    # UTF-8 编码
    subscription_info = subscription_info.decode("UTF-8")
    # 根据换行符分行
    node_infos_4_base64decode = subscription_info.split("\n")
    for node_info_4_base64decode in node_infos_4_base64decode:
        # SSR 节点
        if ("ssr://" in node_info_4_base64decode):
            node_info_4_base64decode = node_info_4_base64decode \
                .replace("ssr://", "").replace("_", "/").replace("-", "+")
            try:
                node_info = b64decode_4_subscription(
                    node_info_4_base64decode).decode("UTF-8")
                node_infos["ssr"].append(node_info)
            except Exception:
                print("SSR 原始信息 BASE64 解码失败：" \
                        + node_info_4_base64decode)
        # VMess 节点
        elif("vmess://" in node_info_4_base64decode):
            node_info_4_base64decode = node_info_4_base64decode \
                .replace("vmess://", "").replace("_", "/").replace("-", "+")
            try:
                node_info = b64decode_4_subscription(
                    node_info_4_base64decode).decode("UTF-8")
                node_infos["vmess"].append(node_info)
            except Exception:
                print("VMESS 原始信息 BASE64 解码失败：" \
                        + node_info_4_base64decode)
        # SS 节点
        elif("ss://" in node_info_4_base64decode):
            # SS 节点信息部分加密，因此只需部分解密即可
            # 去掉协议头
            node_info_4_base64decode = node_info_4_base64decode.lstrip("ss://")
            # 分离出加密的协议和密码
            method_and_password_4_base64decode = node_info_4_base64decode \
                .split("@")[0]
            # 解密协议和密码
            try:
                method_and_password = b64decode_4_subscription(
                    method_and_password_4_base64decode).decode("UTF-8")
            except Exception:
                print("SS 原始信息 BASE64 解码失败：" \
                        + node_info_4_base64decode)
            # 拼接
            node_info = method_and_password + "@" \
                + node_info_4_base64decode.split("@")[1]
            node_infos["ss"].append(node_info)
        # 未知协议
        elif(node_info_4_base64decode):
            print("未知协议的节点信息：" + node_info_4_base64decode)
    return node_infos

"""
@description: 将节点信息整理为 JSON 格式
-------
@param:
-------
@return:
"""
def parse_node_info(node_protocol, node_info):
    # SSR 节点信息解析
    if (node_protocol.lower() == "ssr"):
        # === SSR 基础信息 ===
        # 服务器 IP
        ssr_ip = node_info.split("/?")[0].split(":")[0]
        # 服务器端口
        ssr_port = node_info.split("/?")[0].split(":")[1]
        # 密码
        ssr_password = b64decode_4_subscription(
            node_info.split("/?")[0].split(":")[5]).decode("UTF-8")
        # 加密（chacha20 加密 https://www.icode9.com/content-4-224432.html）
        ssr_method = node_info.split("/?")[0].split(":")[3]
        # 协议
        ssr_protocol = node_info.split("/?")[0].split(":")[2]
        # 混淆
        ssr_obfs = node_info.split("/?")[0].split(":")[4]
        # === SSR 进阶参数 ===
        # 混淆参数
        ssr_obfs_param = b64decode_4_subscription(
            node_info.split("/?")[1].split("&")[0].split("=")[1]) \
                .decode("UTF-8")
        # 协议参数
        ssr_protocol_param = b64decode_4_subscription(node_info.split("/?")[1] \
                                .split("&")[1].split("=")[1]).decode("UTF-8")
        # === SSR 其他信息 ===
        # 备注
        try:
            ssr_remarks = b64decode_4_subscription(node_info.split("/?")[1]
                            .split("&")[2].split("=")[1]).decode("UTF-8")
        except Exception:
            ssr_remarks = ""
        # 分组
        try:
            ssr_group = b64decode_4_subscription(
                node_info.split("/?")[1].split("&")[3] .split("=")[1]) \
                    .decode("UTF-8")
        except Exception:
            ssr_group = ""
        # udpport
        try:
            ssr_udpport = node_info.split("/?")[1].split("&")[4].split("=")[1]
        except Exception:
            ssr_udpport = ""
        # uot
        try:
            ssr_uot = node_info.split("/?")[1].split("&")[5].split("=")[1]
        except Exception:
            ssr_uot = ""
        # 拼接
        ssr_info = {
            "local_address": "127.0.0.1",
            "local_port": "1080",
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
    # VMess 节点解析
    elif(node_protocol.lower() == "vmess"):
        vemss_info = json.loads(node_info)
        vemss_info = {
            "socks_port": "1080",
            "server": json.loads(node_info)["add"],
            "port": json.loads(node_info)["port"],
            "uuid": json.loads(node_info)["id"],
            "alterId": json.loads(node_info)["aid"]
        }
        # 进阶配置
        # net
        if ("net" in json.loads(node_info).keys()):
            vemss_info["network"] = json.loads(node_info)["net"]
        else:
            vemss_info["network"] = " "
        # ws-path
        if ("path" in json.loads(node_info).keys()):
            vemss_info["ws_path"] = json.loads(node_info)["path"]
        else:
            vemss_info["ws_path"] = " "
        # tls
        if ("tls" in json.loads(node_info).keys()):
            vemss_info["tls"] = json.loads(node_info)["tls"]
        else:
            vemss_info["tls"] = " "
        return vemss_info
    # SS 协议
    elif(node_protocol.lower() == "ss"):
        # 服务器地址
        ss_server = node_info.split("@")[1].split(":")[0]
        # 服务器端口
        ss_server_port = node_info.split("@")[1].split(":")[1].split("#")[0]
        # 服务器端口
        ss_method = node_info.split("@")[0].split(":")[0]
        # 密码
        ss_password = node_info.split("@")[0].split(":")[1]
        ss_info = {
            "local_port": "1080",
            "server": ss_server,
            "server_port": ss_server_port,
            "method": ss_method,
            "password": ss_password
        }
        return ss_info
    else:
        print("未知协议：" + node_protocol)

"""
@description: 根据节点协议和信息生成 Docker 内执行的配置更改命令
-------
@param:
-------
@return:
"""
def generate_configure_command(node_protocol, node_info):
    # 将节点信息转为 JSON 格式并修改键值
    parsed_node_info = parse_node_info(node_protocol, node_info)
    # 获取模板指令
    command = rab_config.load_package_config("rab_linux_command.ini",
        "rab_subscription", node_protocol+"_configure")
    for node_info_key in parsed_node_info.keys():
        command = command.replace("{"+node_info_key+"_4_python}",
            str(parsed_node_info[node_info_key]))
    return command

"""
@description: 根据节点信息生成主键 ID
-------
@param:
-------
@return:
"""
def get_node_id(node_protocol, node_info):
    # 将节点信息转为 JSON 格式并修改键值
    parsed_node_info = parse_node_info(node_protocol, node_info)
    if (node_protocol.lower() == "ssr"):
        node_id = "ssr_{server}_{port}_{obfs}_{param}".format(
            server=parsed_node_info["server"],
            port=parsed_node_info["server_port"],
            obfs=parsed_node_info["obfs"],
            param=parsed_node_info["obfs_param"])
    elif(node_protocol.lower() == "vmess"):
        node_id = "vmess_{server}_{port}_{ws_path}".format(
            server=parsed_node_info["server"], port=parsed_node_info["port"],
            ws_path=parsed_node_info["ws_path"])
    elif(node_protocol.lower() == "ss"):
        node_id = "ss_{server}_{port}".format(server=parsed_node_info["server"],
            port=parsed_node_info["server_port"])
    return node_id

"""
@description: 获取这个代理的 IP、地区等信息
-------
@param:
-------
@return:
"""
def get_proxy_info(proxies):
    try:
        r = requests.get("http://ip-api.com/json/?lang=zh-CN",
                         proxies=proxies,
                         timeout=5)
        proxy_info = json.loads(r.text)
        return proxy_info
    except Exception as e:
        print("获取代理信息出错！" + str(e))
    return None


"""
@description: r_subscription 类
-------
@param:
-------
@return:
"""
class r_subscription:

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self,
                 subscription_urls,
                 proxy_port=1080,
                 proxy_location=None,
                 access_test_urls=[],
                 access_test_timeout=5,
                 non_repetitive_node_num=999):
        # 订阅地址
        self.subscription_urls = subscription_urls
        # 节点信息
        self.all_node_infos = {
            "ssr": [],
            "vmess": [],
            "ss": []
        }
        # 可直接使用的代理
        self.proxies = {
            "http": "socks5://127.0.0.1:" + str(proxy_port),
            "https": "socks5://127.0.0.1:" + str(proxy_port)
        }
        # 本地代理端口
        self.proxy_port = proxy_port
        # 当前代理信息
        self.proxy_info = None
        # 所需代理所在地区
        self.proxy_location = proxy_location
        # 使用过的代理 IP
        self.used_proxy_ips = []
        # 需要测试访问的网址
        self.access_test_urls = access_test_urls
        # 对测试网站的超时容忍时间
        self.access_test_timeout = access_test_timeout
        # 使用多少个节点之后重置
        self.non_repetitive_node_num = non_repetitive_node_num
        # 使用过的节点 ID
        self.used_nodes = []
        # 无法访问对应网站的节点 ID
        self.banned_nodes = []
        # Docker Clinet
        self.docker_client = docker.from_env()
        # SSR 节点用容器
        self.ssr_container = None
        # VMess 节点用容器
        self.vmess_container = None
        # SS 节点用容器
        self.ss_container = None
    
    """
    @description: 新建容器
    -------
    @param:
    -------
    @return:
    """
    def create_container(self, node_protocol):
        # 获取镜像名和版本
        image = rab_config.load_package_config(
            "rab_config.ini", "rab_subscription", node_protocol+"_image")
        # GOST 启动命令
        gost_start_command = rab_config.load_package_config(
            "rab_linux_command.ini", "rab_subscription", "gost_start")
        # SSR 协议
        if (node_protocol.lower() == "ssr"):
            # 如果已经有在运行的容器
            if (self.ssr_container):
                # 修改配置
                pass
            # 没有的情况下新建容器
            else:
                self.ssr_container = self.docker_client.containers.run(
                    image=image,
                    command="/bin/bash",
                    # 将 Docker 的 1081 端口映射到本地指定的代理用端口上
                    ports={"1081/tcp": self.proxy_port},
                    tty=True,
                    detach=True)
                # 启动 GOST
                self.ssr_container.exec_run(gost_start_command, detach=True)
        # VMess 协议
        elif(node_protocol.lower() == "vmess"):
            # 如果已经有在运行的容器
            if (self.vmess_container):
                # 修改配置
                pass
            # 没有的情况下新建容器
            else:
                self.vmess_container = self.docker_client.containers.run(
                    image=image,
                    command="/bin/bash",
                    # 将 Docker 的 1081 端口映射到本地指定的代理用端口上
                    ports={"1081/tcp": self.proxy_port},
                    tty=True,
                    detach=True)
                # 启动 GOST
                self.vmess_container.exec_run(gost_start_command, detach=True)
        # SS 协议
        elif(node_protocol.lower() == "ss"):
            # 如果已经有在运行的容器
            if (self.ss_container):
                # 修改配置
                pass
            # 没有的情况下新建容器
            else:
                self.ss_container = self.docker_client.containers.run(
                    image=image,
                    command="/bin/bash",
                    # 将 Docker 的 1081 端口映射到本地指定的代理用端口上
                    ports={"1081/tcp": self.proxy_port},
                    tty=True,
                    detach=True)
                # 启动 GOST
                self.ss_container.exec_run(gost_start_command, detach=True)
        else:
            print("未知协议，无法启动容器。")
    
    """
    @description: 修改容器配置
    -------
    @param:
    -------
    @return:
    """
    def configure_node(self, node_protocol, node_info):
        # 生成修改配置文件的命令
        configure_cmd = generate_configure_command(node_protocol, node_info)
        # print(configure_cmd)
        if (node_protocol.lower() == "ssr"):
            # 关闭 SSR
            print(self.ssr_container.exec_run(rab_config.load_package_config(
                "rab_linux_command.ini", "rab_subscription", "ssr_stop")))
            # 初始化配置文件
            ssr_init_command = rab_config.load_package_config(
                "rab_linux_command.ini", "rab_subscription", "ssr_init")
            self.ssr_container.exec_run(ssr_init_command)
            # 修改配置文件
            print(self.ssr_container.exec_run(configure_cmd))
            # 启动 SSR
            print(self.ssr_container.exec_run(rab_config.load_package_config(
                "rab_linux_command.ini", "rab_subscription", "ssr_start")))
        elif(node_protocol.lower() == "vmess"):
            # 关闭 VMess
            print(self.vmess_container.exec_run(rab_config.load_package_config(
                "rab_linux_command.ini", "rab_subscription", "vmess_stop")))
            # 关闭现有的 Dcoker
            # self.close_container(node_protocol)
            # 新建一个 VMess2Proxy Docker
            # self.create_container(node_protocol)
            # 初始化配置文件
            vmess_init_command = rab_config.load_package_config(
                "rab_linux_command.ini", "rab_subscription", "vmess_init")
            self.vmess_container.exec_run(vmess_init_command)
            # 修改配置文件
            print(self.vmess_container.exec_run(configure_cmd))
            # 启动 VMess
            print(self.vmess_container.exec_run(rab_config.load_package_config(
                "rab_linux_command.ini", "rab_subscription", "vmess_start")))
        elif(node_protocol.lower() == "ss"):
            # 关闭 VMess
            print(self.ss_container.exec_run(rab_config.load_package_config(
                "rab_linux_command.ini", "rab_subscription", "ss_stop")))
            # 关闭现有的 Dcoker
            # self.close_container(node_protocol)
            # 新建一个 VMess2Proxy Docker
            # self.create_container(node_protocol)
            # 初始化配置文件
            ss_init_command = rab_config.load_package_config(
                "rab_linux_command.ini", "rab_subscription", "ss_init")
            self.ss_container.exec_run(ss_init_command)
            # 修改配置文件
            print(self.ss_container.exec_run(configure_cmd))
            # 启动 VMess
            print(self.ss_container.exec_run(rab_config.load_package_config(
                "rab_linux_command.ini", "rab_subscription", "ss_start")))
        # 等待 3 秒等待生效
        time.sleep(3)
    
    """
    @description: 关闭容器
    -------
    @param:
    -------
    @return:
    """
    def close_container(self, node_protocol):
        if (node_protocol.lower() == "ssr"):
            if (self.ssr_container):
                self.ssr_container.stop()
                self.ssr_container = None
        elif(node_protocol.lower() == "vmess"):
            if (self.vmess_container):
                self.vmess_container.stop()
                self.vmess_container = None
        elif(node_protocol.lower() == "ss"):
            if (self.ss_container):
                self.ss_container.stop()
                self.ss_container = None

    """
    @description: 根据订阅连接解析出所有节点信息
    -------
    @param:
    -------
    @return:
    """
    def get_all_node_infos(self):
        for subscription_origin_info in get_subscription_origin_infos(
                self.subscription_urls):
            subscription_info = b64decode_4_subscription(
                subscription_origin_info)
            if (subscription_info):
                node_infos = get_node_infos(subscription_info)
                for node_protocol in node_infos.keys():
                    for node_info in node_infos[node_protocol]:
                        self.all_node_infos[node_protocol].append(node_info)

    """
    @description: 启动容器并配置好代理，因为是本地启动不需要账户密码
    -------
    @param:
    -------
    @return:
    """
    def start(self):
        # 解析订阅
        self.get_all_node_infos()
        # 优先尝试 SSR 节点
        for node_protocol in self.all_node_infos.keys():
            if (self.all_node_infos[node_protocol]):
                # 关闭占用端口的进程
                kill_command = (rab_config.load_package_config(
                    "rab_linux_command.ini", "common", "kill_process_by_port")
                        .replace("{"+"port"+"}", str(self.proxy_port)))
                os.system(kill_command)
                # 启动容器
                self.create_container(node_protocol)
                return True
        # 如果没有节点可用
        print("从订阅获取到的节点列表为空，请检查！")
        return False
    
    """
    @description: 修改容器内配置以更换节点
    -------
    @param:
    -------
    @return:
    """
    def change(self, node_protocol=None):
        # 是否指定协议
        if (node_protocol):
            node_protocols = [node_protocol]
        else:
            node_protocols = self.all_node_infos.keys()
        # 循环所有协议
        for node_protocol in node_protocols:
            # 循环所有节点
            for node_info in self.all_node_infos[node_protocol]:
                # 节点 ID
                node_id = get_node_id(node_protocol, node_info)
                # 判断使用过的节点等信息是否需要清理
                if (len(self.used_nodes) >= self.non_repetitive_node_num):
                    self.clear()
                # 判断节点和 IP 都没有被使用过，并且也不在封禁列表中
                if (not self.is_node_used(node_id)
                        and not node_id in self.banned_nodes):
                    # 关闭非此协议以外的容器
                    other_node_protocols = list(self.all_node_infos.keys())
                    other_node_protocols.remove(node_protocol)
                    for other_node_protocol in other_node_protocols:
                        self.close_container(other_node_protocol)
                    # 开启本协议容器
                    self.create_container(node_protocol)
                    # 修改容器内配置
                    self.configure_node(node_protocol, node_info)
                    # 判断更新后节点的出口 IP 是否被使用过
                    if (not self.is_proxy_ip_used()):
                        # 测试地区是否通过
                        if (not self.is_location_ok()):
                            continue
                        print("测试节点地区正确！")
                        # 测试网站访问是否通过
                        if (not self.is_access_ok()):
                            self.banned_nodes.append(node_id)
                            continue
                        print("测试节点网站访问通过！")
                        print("节点切换完成！")
                        print("至今已使用过的节点：" + str(self.used_nodes))
                        return True
                    # 如果已经被使用过
                    else:
                        continue
                else:
                    continue
        # 如果已经遍历了一遍，则清空所有节点信息
        self.clear()
        return False
    
    """
    @description: 清理已经使用过的节点信息
    -------
    @param:
    -------
    @return:
    """
    def clear(self):
        self.used_nodes = []
        self.banned_nodes = []
        self.used_proxy_ips = []

    """
    @description: 判断此节点是否已经使用过
    -------
    @param:
    -------
    @return:
    """
    def is_node_used(self, node_id):
        # 已经使用过
        if (node_id in self.used_nodes):
            print(node_id, "节点已经使用过了。")
            return True
        # 尚未使用过
        else:
            print(node_id, "节点尚未被使用过！")
            self.used_nodes.append(node_id)
            return False
    
    """
    @description: 判断出口 IP 是否被使用过
    -------
    @param:
    -------
    @return:
    """
    def is_proxy_ip_used(self):
        # 获取这个节点的出口 IP 信息
        self.proxy_info = get_proxy_info(self.proxies)
        # 节点畅通
        if (self.proxy_info):
            print("当前节点出口 IP：" + self.proxy_info["query"])
            print("已经使用过的 IP：" + str(self.used_proxy_ips))
            # 如果这个 IP 已经使用过
            if (self.proxy_info["query"] in self.used_proxy_ips):
                print("节点未使用过但是出口 IP 已经被使用过，废弃......")
                return True
            # 如果这个 IP 尚未使用过
            else:
                print("节点畅通且 IP 未使用过！")
                self.used_proxy_ips.append(self.proxy_info["query"])
                return False
        # 出错情况下也返回已经使用过以跳过
        else:
            print("节点不畅通，废弃......")
            return True

    """
    @description: 判断此节点是否在所属地域
    -------
    @param:
    -------
    @return:
    """
    def is_location_ok(self):
        # 如果没有地区限制或者满足地区限制，返回 True
        if (not self.proxy_location
                or self.proxy_info["country"] in self.proxy_location):
            return True
        else:
            return False
    
    """
    @description: 判断此节点是否可以访问对应网站
    -------
    @param:
    -------
    @return:
    """
    def is_access_ok(self):
        # 循环所有需要测试的网站
        for access_test_url in self.access_test_urls:
            try:
                r = requests.get(access_test_url,
                                 proxies=self.proxies,
                                 timeout=self.access_test_timeout)
                if (r.status_code == 200):
                    continue
                else:
                    return False
            except Exception as e:
                print("获取节点访问网站权限出错！" + str(e))
                return False
        return True


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    # 获取订阅地址
    subscription_urls = rab_config.load_package_config(
        "rab_config.ini", "rab_subscription", "subscription_urls")
    access_test_urls = rab_config.load_package_config(
        "rab_config.ini", "rab_subscription", "access_test_urls")
    r_subscription = r_subscription(
        subscription_urls, access_test_urls=access_test_urls)
    if (r_subscription.start()):
        try:
            no = 1
            # 打印节点信息
            for node_protocol in r_subscription.all_node_infos:
            for node_info in r_subscription.all_node_infos["vmess"]:
                print(no, node_info)
                print(no, parse_node_info("vmess", node_info))
                print(no, generate_configure_command("vmess", node_info))
                no += 1
            # 测试 Docker
            for _ in range(0, 100):
                r_subscription.change("vmess")
                print("以证实可使用 IP：",
                    len(r_subscription.used_proxy_ips), " 个！")
                no += 1
        except Exception as e:
            print(e)
        finally:
            pass
            # 关闭所有容器
            for node_protocol in r_subscription.all_node_infos.keys():
                r_subscription.close_container(node_protocol)