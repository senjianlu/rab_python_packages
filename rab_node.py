#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/sub-2-proxy/rab_python_packages/rab_node.py
# @DATE: 2021/11/05 Fri
# @TIME: 14:37:57
#
# @DESCRIPTION: 共通包 Linux 系统下解析订阅的节点


import re
import sys
import copy
import json
import yaml
import requests
import urllib.parse
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_logging
from rab_python_packages import rab_cryptography


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: 获取指定参数的值
-------
@param:
-------
@return:
"""
def get_param_value(param_key, params_str, delimiter="&"):
    # 使用指定的分割符对字符串进行分割
    param_key_values = params_str.split(delimiter)
    for param_key_value in param_key_values:
        # 如果参数键相等
        if (param_key_value.split("=")[0] == param_key):
            return param_key_value.split("=")[1]
    # 没有对应参数则返回空
    return None

"""
@description: 解析 HTTP 或 SOCKS5 节点信息（暂无 HTTPS 支持）
-------
@param:
-------
@return:
"""
def parse_http_or_socks5_node_url(node_url):
    node_info = {}
    # === 必要参数 ===
    if (node_url.lower().startswith("http")):
        # HTTP 协议
        node_info["type"] = "http"
    else:
        # SOCKS5 协议
        node_info["type"] = "socks5"
    # 服务器 IP 或解析域名
    if ("@" in node_url):
        node_info["server"] = node_info_str.split("@")[1].split(":")[0]
    else:
        node_info["server"] = node_info_str.split(":")[0]
    # 服务器端口
    if ("@" in node_url):
        node_info["port"] = node_info_str.split("@")[1].split(":")[1]
    else:
        node_info["port"] = node_info_str.split(":")[1]
    # === 进阶参数 ===
    # 用户名
    if ("@" in node_url):
        node_info["username"] = node_info_str.split("@")[0].split(":")[0]
    else:
        node_info["username"] = None
    # 密码
    if ("@" in node_url):
        node_info["password"] = node_info_str.split("@")[0].split(":")[1]
    else:
        node_info["password"] = None
    return node_info

"""
@description: 解析 SS 节点信息
-------
@param:
-------
@return:
"""
def parse_ss_node_url(node_url):
    node_info = {}
    # === 必要参数 ===
    # SS 协议
    node_info["type"] = "ss"
    node_info_str = node_url.replace("ss://", "", 1)
    # 部分解码（只有 @ 前的部分需要 Base64 解码）
    node_info_str_4_b64decode = node_info_str.split("@")[0]
    try:
        node_info_str_after_b64decode = rab_cryptography.b64decode(
            node_info_str_4_b64decode).decode("UTF-8")
    except Exception:
        r_logger.error("SS 节点链接部分 Base64 解码失败：{}".format(
            node_info_str_4_b64decode))
        return None
    # 节点名
    node_info["name"] = urllib.parse.unquote(
        node_info_str.split("@")[1].split("#")[1]).rstrip("\n")
    # 服务器 IP 或解析域名
    node_info["server"] = node_info_str.split("@")[1].split("#")[0].split(":")[0]
    # 服务器端口
    node_info["port"] = node_info_str.split("@")[1].split("#")[0].split(":")[1]
    # 加密方式
    node_info["cipher"] = node_info_str_after_b64decode.split(":")[0]
    # 密码
    node_info["password"] = node_info_str_after_b64decode.split(":")[1]
    # UDP（默认关闭）
    node_info["udp"] = "false"
    # === 进阶参数 ===
    # 混淆插件 plugin
    # 暂时未发现有机场配置该参数，无法验证以下方法的正确性，因此注释掉
    # if ("plugin=" in node_info_str):
    #     node_info["plugin"] = get_param_value("plugin", node_info_str)
    #     # 混淆参数
    #     node_info["plugin-opts"] = {}
    #     # 混淆模式
    #     if ("obfs=" in node_info_str):
    #         node_info["plugin-opts"]["mode"] = get_param_value(
    #             "obfs", node_info_str)
    #     # 混淆所用域名
    #     if ("obfs-host=" in node_info_str):
    #         node_info["plugin-opts"]["host"] = get_param_value(
    #             "obfs-host", node_info_str)
    # 返回节点信息
    return node_info

"""
@description: 解析 SSR 节点信息
-------
@param:
-------
@return:
"""
def parse_ssr_node_url(node_url):
    node_info = {}
    # === 必要参数 ===
    # SSR 协议
    node_info["type"] = "ssr"
    node_info_str = node_url.replace("ssr://", "", 1)
    # 全部解码
    try:
        node_info_str = rab_cryptography.b64decode(
            node_info_str).decode("UTF-8")
    except Exception:
        r_logger.error("SSR 节点链接 Base64 解码失败：{}".format(node_info_str))
        return None
    # 节点名
    node_info["name"] = rab_cryptography.b64decode(
        node_info_str.split("/?")[1].split("&")[2].split("=")[1]).decode("UTF-8")
    # 服务器 IP 或解析域名
    node_info["server"] = node_info_str.split("/?")[0].split(":")[0]
    # 服务器端口
    node_info["port"] = node_info_str.split("/?")[0].split(":")[1]
    # 加密方式
    node_info["cipher"] = node_info_str.split("/?")[0].split(":")[3]
    # 密码
    node_info["password"] = rab_cryptography.b64decode(
        node_info_str.split("/?")[0].split(":")[5]).decode("UTF-8")
    # 混淆插件
    node_info["obfs"] = node_info_str.split("/?")[0].split(":")[4]
    # 协议
    node_info["protocol"] = node_info_str.split("/?")[0].split(":")[2]
    # UDP（默认关闭）
    node_info["udp"] = "false"
    # === 进阶参数 ===
    # 混淆参数
    node_info["obfs-param"] = rab_cryptography.b64decode(
        node_info_str.split("/?")[1].split("&")[0].split("=")[1]).decode("UTF-8")
    # 协议参数
    node_info["protocol"] = node_info_str.split("/?")[0].split(":")[2]
    # === 其他参数 ===
    # 节点备注
    node_info["remarks"] = rab_cryptography.b64decode(
        node_info_str.split("/?")[1].split("&")[2].split("=")[1]).decode("UTF-8")
    # 节点分组
    node_info["group"] = rab_cryptography.b64decode(
        node_info_str.split("/?")[1].split("&")[3].split("=")[1]).decode("UTF-8")
    # 返回节点信息
    return node_info

"""
@description: 解析非标准 JSON 格式的 VMess 节点信息
-------
@param:
-------
@return:
"""
def parse_vmess_node_url_ex(node_info_str):
    node_info = {}
    # VMess 协议
    node_info["type"] = "vmess"
    # 如果形如 auto:aaaa-bbbb-cccc-dddd@207.46.123.123:12345 样式
    search_obj = re.search(u"(.*):(.*)@(.*):(.*)", node_info_str)
    if (search_obj):
        # 节点名
        node_info["name"] = node_info_str.split("@")[1].replace(":", "_")
        # 服务器 IP 或解析域名
        node_info["server"] = node_info_str.split("@")[1].split(":")[0]
        # 服务器端口
        node_info["port"] = node_info_str.split("@")[1].split(":")[1]
        # 用户 ID
        node_info["uuid"] = node_info_str.split("@")[0].split(":")[1]
        # 每个请求随机附带的数值的上限（防止同时间戳的请求混杂在一起）
        node_info["alterId"] = 0
        # 加密方式
        node_info["cipher"] = node_info_str.split("@")[0].split(":")[0]
        return node_info
    # 如果形如 Base64乱码?tfo=1&remark=备注&alterId=0&obfs=websocket 样式
    print(node_info_str)
    search_obj = re.search(u"(.*)?(.*)", node_info_str)
    if (search_obj):
        node_info_str_4_b64decode = node_info_str.split("?")[0]
        try:
            node_info_str_after_b64decode = rab_cryptography.b64decode(
                node_info_str_4_b64decode).decode("UTF-8")
        except Exception as e:
            r_logger.error("VMess 节点链接 Base64 解码失败：{}".format(
                node_info_str_4_b64decode))
            return None
        # 节点名（如果节点有 remark 参数就使用它的值，否则就自行拼接）
        if (get_param_value("remark", node_info_str.split("?")[1], "&")):
            node_info["name"] = get_param_value(
                "remark", node_info_str.split("?")[1], "&")
        else:
            node_info["name"] = node_info_str_after_b64decode.split(
                "@")[1].replace(":", "_")
        # 服务器 IP 或解析域名
        node_info["server"] = node_info_str_after_b64decode.split(
            "@")[1].split(":")[0]
        # 服务器端口
        node_info["port"] = node_info_str_after_b64decode.split(
            "@")[1].split(":")[1]
        # 用户 ID
        node_info["uuid"] = node_info_str_after_b64decode.split(
            "@")[0].split(":")[1]
        # 每个请求随机附带的数值的上限（防止同时间戳的请求混杂在一起）
        #（如果节点有 remark 参数就使用它的值，否则就自行拼接）
        if (get_param_value("alterId", node_info_str.split("?")[1], "&")):
            node_info["alterId"] = get_param_value(
                "alterId", node_info_str.split("?")[1], "&")
        else:
            node_info["alterId"] = 0
        # 加密方式
        node_info["cipher"] = node_info_str_after_b64decode.split(
            "@")[0].split(":")[0]
        return node_info
    # 均无匹配则返回空
    return None

"""
@description: 解析 VMess 节点信息
-------
@param:
-------
@return:
"""
def parse_vmess_node_url(node_url):
    node_info = {}
    # === 必要参数 ===
    # VMess 协议
    node_info["type"] = "vmess"
    node_info_str = node_url.replace("vmess://", "", 1)
    # 全部解码
    try:
        node_info_str = rab_cryptography.b64decode(
            node_info_str).decode("UTF-8")
        node_info_json = json.loads(node_info_str)
    except Exception:
        # 尝试用非标准格式解析
        node_info = parse_vmess_node_url_ex(node_info_str)
        if (node_info and "name" in node_info.keys() and node_info["name"]):
            return node_info
        else:
            r_logger.error(
                "VMess 节点链接 Base64 解码失败：{}".format(node_info_str))
            return None
    # 节点名
    node_info["name"] = u"{}".format(node_info_json["ps"])
    # 服务器 IP 或解析域名
    node_info["server"] = node_info_json["add"]
    # 服务器端口
    node_info["port"] = node_info_json["port"]
    # 用户 ID
    node_info["uuid"] = node_info_json["id"]
    # 每个请求随机附带的数值的上限（防止同时间戳的请求混杂在一起）
    node_info["alterId"] = node_info_json["aid"]
    # 加密方式
    node_info["cipher"] = node_info_json["cipher"] if "cipher" in \
        node_info_json.keys() else "auto"
    # === 进阶参数 ===
    # UDP（默认关闭）
    node_info["udp"] = "false"
    # TLS（HTTPS）
    if ("tls" in node_info_json.keys() and node_info_json["tls"]):
        node_info["tls"] = "true"
        # 跳过 HTTPS 证书的认证
        node_info["skip-cert-verify"] = "false" if "verify_cert" in \
            node_info_json.keys() and node_info_json["verify_cert"] else "true"
        # 指定 HTTPS 所通信的域名（应对同一服务上有多个 HTTPS 域名）
        node_info["servername"] = node_info_json["servername"] if "sni" in \
            node_info_json.keys() and node_info_json["sni"] else ""
    else:
        node_info["tls"] = "false"
    # 连接方式（默认为 tcp）
    node_info["network"] = node_info_json["net"] if "net" in \
        node_info_json.keys() and node_info_json["net"] else "tcp"
    # WebSocket 连接模式
    if ("net" in node_info_json.keys() and node_info_json["net"] == "ws"):
        node_info["network"] = "ws"
        # WebSocket 连接参数
        node_info["ws-opts"] = {}
        # ws 路径
        node_info["ws-opts"]["path"] = node_info_json["path"]
        # ws 请求头
        if ("headerType" in node_info_json.keys()
                and str(node_info_json["headerType"]).lower() != "none"):
            node_info["ws-opts"]["headers"] = {}
            # 暂时未发现有机场限制请求头
            # todo...
        # ws max-early-data
        # 暂时未发现有机场配置该参数
        # todo...
        # ws early-data-header-name
        # 暂时未发现有机场配置该参数
        # todo...
    # 其他 TCP 模式均默认为 HTTP 连接模式
    else:
        node_info["network"] = "http"
    # 返回节点信息
    return node_info

"""
@description: 使用 subconverter 进行解析
-------
@param:
-------
@return:
"""
def parse_node_url_by_subconverter(node_url, subconverter_url):
    # 判断转换地址是否带了 /sub，不带则添加
    if (not subconverter_url.endswith("/sub")):
        if (subconverter_url.endswith("/")):
            subconverter_url += "sub"
        else:
            subconverter_url += "/sub"
    # 参数
    params = {
        "target": "clash",
        # 节点链接作为参数时会自动经过 URLEncode 编码
        "url": node_url,
        "insert": "false",
        "emoji": "false",
        "list": "true",
        "udp": "false",
        "tfo": "false",
        "scv": "false",
        "fdn": "false",
        "sort": "false",
        "new_name": "true"
    }
    try:
        response = requests.get(subconverter_url, params=params)
        if (response):
            # 读取 YAML 格式的配置
            proxies = yaml.safe_load(response.text)["proxies"][0]
            return proxies
        else:
            r_logger.warn("{} 无法访问 subconverter 后端以解析节点！" \
                .format(node_url))
    except Exception as e:
        r_logger.error("{} 访问 subconverter 后端解析节点出错！".format(node_url))
        r_logger.error(e)
    return None
    
"""
@description: 解析节点链接以获取节点信息
-------
@param:
-------
@return:
"""
def parse_node_url(node_url, parse_method):
    # 调用 subconverter 后端解析
    if (parse_method == "subconverter"):
        # subconverter 后端地址
        subconverter_url = rab_config.load_package_config(
            "rab_config.ini", "rab_node", "subconverter_url")
        return parse_node_url_by_subconverter(node_url, subconverter_url)
    # 自行解析
    else:
        try:
            if (node_url.startswith("ss://")):
                return parse_ss_node_url(node_url)
            elif(node_url.startswith("ssr://")):
                return parse_ssr_node_url(node_url)
            elif(node_url.startswith("vmess://")):
                return parse_vmess_node_url(node_url)
            elif(node_url.startswith("trojan://")):
                # node = parse_trojan_node_url(node_url)
                pass
            else:
                r_logger.warn("自行解析发现未知协议节点：{}".format(node_url))
        except Exception as e:
            r_logger.error("自行解析节点链接出错！")
            r_logger.error(e)
    return None

"""
@description: 节点类
-------
@param:
-------
@return:
"""
class r_node():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self,
                 node_url,
                 subscription_url=None,
                 parse_method=rab_config.load_package_config(
                     "rab_config.ini", "rab_node", "parse_method")):
        self.url = node_url
        self.subscription_url = subscription_url
        self.info = parse_node_url(self.url, parse_method)
        self.id = self.generate_node_id()
    
    """
    @description: 生成节点的 ID
    -------
    @param:
    -------
    @return:
    """
    def generate_node_id(self):
        if (self.info):
            return "_".join([str(value) for value in self.info.values()])
        else:
            return None
        
    """
    @description: 生成节点配置命令
    -------
    @param:
    -------
    @return:
    """
    def generate_node_configure_command(self, socks_port, client_side="clash"):
        if (self.info):
            # 获取配置命令模板
            node_configure_command_template = rab_config.load_package_config(
                "rab_linux_command.ini", "rab_node", \
                "{}_configure".format(client_side))
            # 替换 SOCKS5 端口
            node_configure_command = node_configure_command_template.replace(
                "{socks-port_4_replace}", str(socks_port))
            # 替换节点信息（将节点名改为 node）
            _node_info = copy.deepcopy(self.info)
            _node_info["name"] = "node"
            node_configure_command = node_configure_command.replace(
                "{node-info_4_replace}", str(_node_info))
            return node_configure_command
        else:
            return None
        

"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    # 对某协议所有节点链接进行解析
    node_urls = []
    with open("node_urls", "r") as f:
        for row in f.readlines():
            node_urls.append(row)
    for node_url in node_urls:
        node = r_node(node_url)
        print(node.id, node.info)
        print(node.generate_node_configure_command(1080))

    # 对单个节点链接进行解析
    # node_url = ""
    # node = r_node(node_url)
    # print(node.id, node.info)
