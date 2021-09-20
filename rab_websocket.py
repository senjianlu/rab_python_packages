#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_websocket.py
# @DATE: 2021/09/20 Mon
# @TIME: 15:33:54
#
# @DESCRIPTION: 共通包 WebSocket 模块


import sys
import time
import cfscrape
import websocket
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_logging


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: 获取 Cloudflare 的认证信息
-------
@param:
-------
@return:
"""
def get_cloudflare_access_infos(url, user_agent):
    access_infos = []
    token, user_agent = cfscrape.get_cookie_string(url, user_agent)
    cookie_args = token.split(";")
    for cookie_arg in cookie_args:
        cookie_arg = cookie_arg.rstrip().lstrip()
        access_infos.append(cookie_arg.replace("=", ": "))
    access_infos.append("User-Agent: {}".format(user_agent))
    return access_infos

"""
@description: WebSocket 类
-------
@param:
-------
@return:
"""
class r_websocket():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self, url, headers, enable_trace=False, origin=None):
        # WebSocket 地址
        self.url = url
        # WebSocket 连接请求头
        self.headers = headers
        # 是否开启日志
        self.enable_trace = enable_trace
        # 连接时来源
        self.origin = origin
        # WebSocket 连接对象
        self.ws = None
        self.build()
        # 发送的消息
        self.sent_message = {}
        # 收到的消息
        self.received_message = {}
    
    """
    @description: 建立连接
    -------
    @param:
    -------
    @return:
    """
    def build(self):
        # 日志记录
        websocket.enableTrace(self.enable_trace)
        self.ws = websocket.WebSocketApp(
            self.url,
            header=self.headers,
            on_open=lambda ws: self.on_open(ws),
            on_message=lambda ws, message: self.on_message(ws, message),
            on_error=lambda ws, error: self.on_error(ws, error),
            on_close=lambda ws, close_status_code, close_msg: self.on_close(
                ws, close_status_code, close_msg))
    
    """
    @description: 连接
    -------
    @param:
    -------
    @return:
    """
    def connect(self):
        self.ws.run_forever(origin=self.origin)
    
    """
    @description: 发送消息
    -------
    @param:
    -------
    @return:
    """
    def send(self, message):
        r_logger.info("WebSocket 发送消息：{}".format(message))
        self.ws.send(message)
        self.sent_message[time.time()] = message
    
    """
    @description: 关闭连接
    -------
    @param:
    -------
    @return:
    """
    def close(self):
        self.ws.close()

    """
    @description: 建立连接时
    -------
    @param:
    -------
    @return:
    """
    def on_open(self, ws):
        r_logger.info("WebSocket 连接成功！")

    """
    @description: 收到消息时
    -------
    @param:
    -------
    @return:
    """
    def on_message(self, ws, message):
        r_logger.info("WebSocket 收到消息：{}".format(
            message if len(message) <= 100 else (message[0:100] + "......")))
        self.received_message[time.time()] = message
        
    """
    @description: 出错时
    -------
    @param:
    -------
    @return:
    """
    def on_error(self, ws, error):
        r_logger.error("WebSocket 出错！")
        r_logger.error(error)
    
    """
    @description: 连接关闭时
    -------
    @param:
    -------
    @return:
    """
    def on_close(self, ws, close_status_code, close_msg):
        r_logger.info("WebSocket 连接关闭，状态码：{status_code}，消息：{msg}" \
            .format(status_code=str(close_status_code), msg=str(close_msg)))
    

"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    print(time.time())
    test_user_agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/" \
        + "537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36"
    print(get_cloudflare_access_infos("https://google.com", test_user_agent))