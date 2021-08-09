#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/Github/rab_python_packages/rab_subscription.py
# @DATE: 2021/05/10 Mon
# @TIME: 14:11:24
#
# @DESCRIPTION: 共通包 Linux 系统下解析订阅和节点


import re
import sys
import time
import json
import urllib
import base64
import requests
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_requests
from rab_python_packages import rab_logging
from rab_python_packages import rab_docker
from rab_python_packages import rab_postgresql


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: 用以订阅信息 BASE64 解码的方法
-------
@param:
-------
@return:
"""
def b64decode(str_4_b64decode):
    str_4_b64decode = str_4_b64decode.replace("_", "/")
    str_4_b64decode = str_4_b64decode.replace("-", "+")
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
    r_logger.error("BASE64 解码失败！待解码内容：{}".format(str_4_b64decode))
    return None

"""
@description: 获取指定参数的值
-------
@param:
-------
@return:
"""
def get_param_value(param_key, url):
    search_obj = re.search(".*{}=(.*)#.*".format(param_key), url)
    if ("&" in search_obj.group(1)):
        return search_obj.group(1).split("&")[0]
    else:
        return search_obj.group(1)

"""
@description: 解析 SSR 节点信息
-------
@param:
-------
@return:
"""
def parse_ssr_node_url(node_url):
    node_info = node_url.replace("ssr://", "")
    try:
        node_info = b64decode(node_info).decode("UTF-8")
    except Exception:
        r_logger.error("SSR 原始信息 BASE64 解码失败：{}".format(node_info))
        return None
    node = {}
    node["name"] = b64decode(
        node_info.split("/?")[1].split("&")[2].split("=")[1]).decode("UTF-8")
    node["type"] = "ssr"
    # === SSR 基础信息 ===
    # 服务器 IP
    node["server"] = node_info.split("/?")[0].split(":")[0]
    # 服务器端口
    node["port"] = node_info.split("/?")[0].split(":")[1]
    # 加密
    node["cipher"] = node_info.split("/?")[0].split(":")[3]
        # 密码
    node["password"] = b64decode(
        node_info.split("/?")[0].split(":")[5]).decode("UTF-8")
    # 协议
    node["protocol"] = node_info.split("/?")[0].split(":")[2]
    # 协议参数
    node["protocol-param"] = b64decode(
        node_info.split("/?")[1].split("&")[1].split("=")[1]).decode("UTF-8")
    # 混淆
    node["obfs"] = node_info.split("/?")[0].split(":")[4]
    node["obfs-param"] = b64decode(
        node_info.split("/?")[1].split("&")[0].split("=")[1]).decode("UTF-8")
    # 备注
    node["remarks"] = b64decode(
        node_info.split("/?")[1].split("&")[2].split("=")[1]).decode("UTF-8")
    # 分组
    node["group"] = b64decode(
        node_info.split("/?")[1].split("&")[3].split("=")[1]).decode("UTF-8")
    # UDP
    node["udp"] = "false"
    # 节点 ID
    node["id"] = "{type}_{server}_{port}_{obfs}_{obfs-param}".format(
        **node)
    return node

"""
@description: 解析 SS 节点信息
-------
@param:
-------
@return:
"""
def parse_ss_node_url(node_url):
    node_info = node_url.replace("ss://", "")
    # 部分解密
    node_info_4_b64decode = node_info.split("@")[0]
    try:
        node_info_4_b64decode = b64decode(node_info_4_b64decode).decode("UTF-8")
    except Exception:
        print("SS 原始信息 BASE64 解码失败：{}".format(node_info_4_b64decode))
        return None
    node = {}
    node["name"] = urllib.parse.unquote(node_info.split("@")[1].split("#")[1])
    node["type"] = "ss"
    node["server"] = node_info.split("@")[1].split("#")[0].split(":")[0]
    node["port"] = node_info.split("@")[1].split("#")[0].split(":")[1]
    node["cipher"] = node_info_4_b64decode.split(":")[0]
    node["password"] = node_info_4_b64decode.split(":")[1]
    node["udp"] = "false"
    if ("plugin=" in node_info):
        node["plugin"] = get_param_value("plugin", node_info)
    else:
        node["plugin"] = ""
    if (node["plugin"]):
        node["plugin-opts"] = {}
        if ("obfs=" in node_info):
            node["mode"] = get_param_value("obfs", node_info)
        if ("obfs-host=" in node_info):
            node["host"] = get_param_value("obfs-host", node_info)
    # 节点 ID
    node["id"] = "{type}_{server}_{port}".format(**node)
    return node

"""
@description: 解析 VMess 节点信息
-------
@param:
-------
@return:
"""
def parse_vmess_node_url(node_url):
    node_info = node_url.replace("vmess://", "")
    try:
        node_info = b64decode(node_info).decode("UTF-8")
        node_info = json.loads(node_info)
    except Exception:
        print("Vmess 原始信息 BASE64 解码失败：{}".format(node))
        return None
    node = {}
    node["name"] = u"{}".format(node_info["ps"])
    node["type"] = "vmess"
    node["server"] = node_info["add"] if "add" in node_info.keys() else ""
    node["port"] = node_info["port"]
    node["uuid"] = node_info["id"]
    node["alterId"] = node_info["aid"]
    node["cipher"] = "auto"
    node["udp"] = "false"
    node["tls"] = node_info["tls"] if "tls" in node_info.keys() else ""
    if (node["tls"]):
        node["tls"] = "true"
    node["servername"] = node_info["sni"] if "sni" in node_info.keys() else ""
    node["network"] = node_info["net"] if "net" in node_info.keys() else ""
    if (node["network"] == "tcp"):
        node["network"] = ""
    elif(node["network"] == "ws"):
        node["ws-path"] = node_info["path"] if "path" in node_info.keys() else ""
        node["ws-headers"] = {}
        if ("host" in node_info.keys()):
            node["ws-headers"]["Host"] = node_info["host"]
    # 节点 ID
    if (not node["network"]):
        node["id"] = "{type}_{server}_{port}".format(**node)
    elif(node["network"] == "ws"):
        node["id"] = "{type}_{server}_{port}_{ws-path}".format(**node)
    return node

"""
@description: 解析 Trojan 节点信息
-------
@param:
-------
@return:
"""
def parse_trojan_node_url(node_url):
    node_info = node_url.replace("trojan://", "")
    node = {}
    node["name"] = urllib.parse.unquote(node_info.split("#")[1])
    node["type"] = "trojan"
    node["server"] = node_info.split("@")[1].split("?")[0].split(":")[0]
    node["port"] = node_info.split("@")[1].split("?")[0].split(":")[1]
    node["password"] = node_info.split("@")[0]
    node["udp"] = "false"
    if ("allowInsecure=" in node_info):
        node["allowInsecure"] = get_param_value("allowInsecure", node_info)
        if (node["allowInsecure"] and node["allowInsecure"] == "1"):
            node["skip-cert-verify"] = "true"
        del node["allowInsecure"]
    if ("peer=" in node_info):
        node["peer"] = get_param_value("peer", node_info)
    else:
        node["peer"] = ""
    if ("sni=" in node_info):
        node["sni"] = get_param_value("sni", node_info)
    else:
        node["sni"] = ""
    node["remark"] = urllib.parse.unquote(node_info.split("#")[1])
    # 节点 ID
    if (not node["sni"]):
        node["id"] = "{type}_{server}_{port}".format(**node)
    else:
        node["id"] = "{type}_{server}_{port}_{sni}".format(**node)
    return node

"""
@description: 获取订阅的 BASE64 解码前的原始信息
-------
@param:
-------
@return:
"""
def get_subscription_origin_infos(subscription_urls):
    subscription_origin_infos = {}
    for subscription_url in subscription_urls:
        try:
            # 保险访问
            e_response = rab_requests.ensure_get(subscription_url)
            subscription_origin_infos[subscription_url] = e_response.text
        except Exception as e:
            r_logger.error("{} 不使用代理获取订阅原始信息出错！".format(
                subscription_url))
            r_logger.error(e)
    return subscription_origin_infos

"""
@description: 获取订阅的 BASE64 解码后并分割后的各节点链接
-------
@param:
-------
@return:
"""
def get_node_urls(subscription_origin_info):
    node_urls = []
    subscription_info = b64decode(subscription_origin_info).decode("UTF-8")
    for row in subscription_info.split("\n"):
        if (row.strip()):
            node_urls.append(row.strip())
    return node_urls

"""
@description: 解析节点链接以获取节点信息
-------
@param:
-------
@return:
"""
def parse_node_url(node_url):
    if (node_url.startswith("ssr://")):
        node = parse_ssr_node_url(node_url)
    elif(node_url.startswith("ss://")):
        node = parse_ss_node_url(node_url)
    elif(node_url.startswith("vmess://")):
        node = parse_vmess_node_url(node_url)
    elif(node_url.startswith("trojan://")):
        node = parse_trojan_node_url(node_url)
    return node

"""
@description: 筛选掉通知用节点
-------
@param:
-------
@return:
"""
def filter_nodes(nodes):
    filter_keywords = rab_config.load_package_config(
        "rab_config.ini", "rab_subscription", "filter_keywords")
    filtered_nodes = []
    for node in nodes:
        filter_flg = False
        for filter_keyword in filter_keywords:
            if (filter_keyword.lower() in node["name"].lower()):
                filter_flg = True
                break
        if (not filter_flg):
            filtered_nodes.append(node)
    return filtered_nodes

"""
@description: 获取所有节点
-------
@param:
-------
@return:
"""
def get_nodes(subscription_urls):
    nodes = []
    subscription_origin_infos = get_subscription_origin_infos(subscription_urls)
    for subscription_url in subscription_origin_infos.keys():
        node_urls = get_node_urls(subscription_origin_infos[subscription_url])
        for node_url in node_urls:
            node = parse_node_url(node_url)
            node["subscription_url"] = subscription_url
            nodes.append(node)
    # 筛选节点
    nodes = filter_nodes(nodes)
    return nodes

"""
@description: 生成 Clash 节点
-------
@param:
-------
@return:
"""
def generate_clash_proxy(node):
    # 可能回包含中文导致转码失败的无用字段
    useless_config_keys = rab_config.load_package_config(
        "rab_config.ini", "rab_subscription", "useless_config_keys")
    # 遍历配置
    clash_proxy = '- {{name: {},'.format(node["type"])
    for node_config_key in node.keys():
        # 跳过无用字段
        if (node_config_key in useless_config_keys):
            continue
        # 如果节点配置值不是字典类型
        if (type(node[node_config_key]) != dict
                and node[node_config_key]):
            clash_proxy += ' {key}: {value},'.format(
                key=node_config_key, value=node[node_config_key])
        # 如果节点配置是字典类型的
        if (type(node[node_config_key]) == dict
                and node[node_config_key]):
            node_config_dict_str = "{"
            for node_config_dict_key in node[node_config_key]:
                if (node[node_config_key][node_config_dict_key]):
                    node_config_dict_str += '"{key}": {value},'.format(
                        key=node_config_dict_key, value=node[
                            node_config_key][node_config_dict_key])
            # 如果为空，跳过这个配置字段
            if (node_config_dict_str == "{"):
                continue
            else:
                node_config_dict_str = node_config_dict_str[::-1].replace(
                    ",", "", 1)[::-1]
                node_config_dict_str += "}"
                clash_proxy += " {key}: {value},".format(
                    key=node_config_key, value=node_config_dict_str)
    # 循环结束后修改格式
    clash_proxy = clash_proxy[::-1].replace(",", "", 1)[::-1]
    clash_proxy += "}"
    return clash_proxy

"""
@description: 生成修改配置文件的 Linux 命令
-------
@param:
-------
@return:
"""
def generate_configure_command(node, local_address="127.0.0.1", local_port=1080):
    clash_proxy = generate_clash_proxy(node)
    # 获取这个协议的配置命令模板
    command_template = rab_config.load_package_config(
        "rab_linux_command.ini", "rab_subscription", "{}_configure".format(
            node["type"]))
    # 批量替换信息
    configure_command = command_template
    # 基础的本地代理配置
    configure_command = configure_command.replace(
        "{socks-port_4_python}", "{}".format(str(local_port)))
    # 节点配置
    configure_command = configure_command.replace(
        "{clash-proxy_4_python}", clash_proxy)
    return configure_command

"""
@description: 修改容易内代理配置
-------
@param:
-------
@return:
"""
def configure_node(container, node):
    print("====== 开始修改容器内的配置文件并重启...... ======")
    # 生成修改配置文件的命令
    configure_command = generate_configure_command(node)
    # 关闭代理软件
    print(container.exec_run(
        rab_config.load_package_config("rab_linux_command.ini", \
            "rab_subscription", "{}_stop".format(node["type"]))))
    # 初始化配置文件
    print(container.exec_run(
        rab_config.load_package_config("rab_linux_command.ini", \
            "rab_subscription", "{}_init".format(node["type"]))))
    # 修改配置文件
    print(container.exec_run(configure_command))
    # 启动代理软件
    print(container.exec_run(
        rab_config.load_package_config("rab_linux_command.ini", \
            "rab_subscription", "{}_start".format(node["type"]))))
    print("====== 容器内的配置文件修改并重启完成！ ======")

"""
@description: 获取订阅地址
-------
@param:
-------
@return:
"""
def get_subscription_urls(origin="config", r_pgsql_driver=None):
    subscription_urls = []
    # 从配置文件中读取
    if (origin == "config"):
        subscription_urls = rab_config.load_package_config(
            "rab_config.ini", "rab_subscription", "subscription_urls")
    # 从数据库中读取
    else:
        # 如果是临时创建连接则需要及时关闭数据库连接
        close_flg = False
        if (not r_pgsql_driver):
            r_pgsql_driver = rab_postgresql.r_pgsql_driver(
                show_column_name=True)
            close_flg = True
        # 在数据库中搜索
        select_sql = """
            SELECT
                *
            FROM
                sa_proxy_subscription
        """
        select_result = r_pgsql_driver.select(select_sql)
        if (close_flg):
            r_pgsql_driver.close()
        for row in select_result:
            subscription_urls.append(row["spb_url"])
    return subscription_urls


"""
@description: 在本地开启代理用的类
-------
@param:
-------
@return:
"""
class r_subscription():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self,
                 subscription_urls=[],
                 local_port=1080,
                 proxy_location=None,
                 access_test_urls=rab_config.load_package_config(
                    "rab_config.ini", "rab_subscription", "access_test_urls"),
                 access_test_timeout=int(rab_config.load_package_config(
                    "rab_config.ini", "rab_requests", "timeout")),
                 non_repetitive_node_num=999):
        # 订阅地址
        self.subscription_urls = subscription_urls
        # 节点信息
        self.all_nodes = {}
        # 可直接使用的代理
        self.proxies = {
            "http": "socks5://127.0.0.1:" + str(local_port),
            "https": "socks5://127.0.0.1:" + str(local_port)
        }
        # 本地代理端口
        self.local_port = local_port
        # 当前代理信息
        self.proxy_info = None
        # 所需代理所在地区
        self.proxy_location = proxy_location
        # 使用过的代理 IP
        self.used_proxy_out_ips = []
        # 需要测试访问的网址
        self.access_test_urls = access_test_urls
        # 对测试网站的超时容忍时间
        self.access_test_timeout = access_test_timeout
        # 使用多少个节点之后重置
        self.non_repetitive_node_num = non_repetitive_node_num
        # 使用过的节点 ID
        self.used_node_ids = []
        # 无法访问对应网站的节点 ID
        self.banned_node_ids = []
        # 节点用容器
        self.container = None

    """
    @description: 新建容器
    -------
    @param:
    -------
    @return:
    """
    def create(self):
        # 获取镜像名和版本
        image = rab_config.load_package_config(
            "rab_config.ini", "rab_subscription", "image")
        # GOST 启动命令
        gost_start_command = rab_config.load_package_config(
            "rab_linux_command.ini", "rab_subscription", "gost_start")
        # 如果已经有在运行的容器
        if (self.container):
            # 修改配置
            pass
        # 没有的情况下新建容器
        else:
            # 容器名
            container_name = "proxy_port_{}".format(str(self.local_port))
            # 关闭和删除旧容器
            old_containers = rab_docker.get_containers(
                name_keyword=container_name)
            if (old_containers):
                for old_container in old_containers:
                    old_container.stop()
                    old_container.remove()
            # 建立新容器
            self.container = rab_docker.get_client().containers.run(
                image=image,
                name=container_name,
                command="/bin/bash",
                # 将 Docker 的 1081 端口映射到本地指定的代理用端口上
                ports={"1081/tcp": str(self.local_port)},
                tty=True,
                detach=True)
            # 启动 GOST
            self.container.exec_run(gost_start_command, detach=True)
        return self.container
    
    """
    @description: 修改容器配置
    -------
    @param:
    -------
    @return:
    """
    def configure(self, node):
        # 修改容器内的配置
        configure_node(self.container, node)
        # 等待 3 秒等待生效
        time.sleep(3)
    
    """
    @description: 根据订阅连接解析出所有节点信息
    -------
    @param:
    -------
    @return:
    """
    def get_all_nodes(self):
        self.all_nodes = get_nodes(self.subscription_urls)
    
    """
    @description: 启动容器并配置好代理，因为是本地启动不需要账户密码
    -------
    @param:
    -------
    @return:
    """
    def start(self, origin="config", r_pgsql_driver=None):
        # 获取所有订阅链接
        self.subscription_urls = get_subscription_urls(origin, r_pgsql_driver)
        # 解析订阅
        self.get_all_nodes()
        # 启动容器
        self.create()
        return True
    
    """
    @description: 修改容器内配置以更换节点
    -------
    @param:
    -------
    @return:
    """
    def change(self):
        # 循环所有节点
        for node in self.all_nodes:
            # 判断使用过的节点等信息是否需要清理
            if (len(self.used_node_ids) >= self.non_repetitive_node_num):
                self.clear()
            # 判断节点和 IP 都没有被使用过，并且也不在封禁列表中
            if (node["id"] not in self.used_node_ids
                    and node["id"] not in self.banned_node_ids):
                # 将节点记为已使用
                self.used_node_ids.append(node["id"])
                r_logger.info("使用节点：{}".format(str(node)))
                # 修改容器内配置
                self.configure(node)
                # 判断更新后节点的出口 IP 是否被使用过
                if (not self.is_proxy_out_ip_used()):
                    # 测试地区是否通过
                    if (not self.is_location_ok()):
                        r_logger.info("节点地区并不符合要求，跳过！")
                        continue
                    r_logger.info("测试节点地区符合要求！")
                    # 测试网站访问是否通过
                    if (not self.is_access_ok()):
                        self.banned_node_ids.append(node["id"])
                        continue
                    r_logger.info("测试节点网站访问通过！")
                    r_logger.info("节点切换完成！")
                    r_logger.debug("至今已使用过的节点：{}".format(
                        str(self.used_node_ids)))
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
        self.used_proxy_out_ips = []

    """
    @description: 判断出口 IP 是否被使用过
    -------
    @param:
    -------
    @return:
    """
    def is_proxy_out_ip_used(self):
        # 获取这个节点的出口 IP 信息
        self.proxy_info = rab_requests.get_ip_info(self.proxies)
        # 节点畅通
        if (self.proxy_info["ip"]):
            r_logger.info("当前节点出口 IP：{}".format(
                str(self.proxy_info["ip"])))
            r_logger.info("已经使用过的 IP：{}".format(
                str(self.used_proxy_out_ips)))
            # 如果这个 IP 已经使用过
            if (self.proxy_info["ip"] in self.used_proxy_out_ips):
                r_logger.info(
                    "节点未使用过但是出口 IP 已经被使用过，废弃......")
                return True
            # 如果这个 IP 尚未使用过
            else:
                r_logger.info("节点畅通且 IP 未使用过！")
                self.used_proxy_out_ips.append(self.proxy_info["ip"])
                return False
        # 出错情况下也返回已经使用过以跳过
        else:
            r_logger.info("节点不畅通，废弃......")
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
                or self.proxy_info["location"] in self.proxy_location):
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
                r_logger.info("获取节点访问网站权限出错！错误信息：{}".format(
                    str(e)))
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
    pass
    # 解析每个订阅链接
    # with open("nodes/subscription_urls.txt", "r") as f:
    #     subscription_urls = f.readlines()
    # _subscription_urls = []
    # for subscription_url in subscription_urls:
    #     _subscription_urls.append(subscription_url.replace("\n", ""))
    # with open("nodes/all.txt", "w") as f:
    #     nodes = get_nodes(_subscription_urls)
    #     for node in nodes:
    #         f.write("{}\n".format(generate_configure_command(node)))

    # 对比节点链接和配置获取是否正确的测试
    # subscription_origin_infos = get_subscription_origin_infos([
    #     ""])
    # for subscription_url in subscription_origin_infos.keys():
    #     node_urls = get_node_urls(subscription_origin_infos[subscription_url])
    #     print(subscription_url)
    #     print("="*20)
    #     for node_url in node_urls:
    #         # print(node_url)
    #         print(parse_node_url(node_url))
    #     print("="*20)

    # 对节点链接参数获取的测试
    # url = ""
    # print(get_param_value("allowInsecure", url))
    # serach_obj = re.search(r".*allowInsecure=(.*)#.*", url)
    # if (serach_obj):
    #     print(serach_obj.group())
    #     print(serach_obj.group(1))

    # 类测试
    # r_subscription = r_subscription()
    # r_subscription.start()
    # for _ in range(0, 5):
    #     r_subscription.change()