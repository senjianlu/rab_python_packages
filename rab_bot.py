#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_telegram_bot.py
# @DATE: 2020/12/16 Wed
# @TIME: 16:29:07
#
# @DESCRIPTION: 共通包 Telegram Bot 机器人消息推送模块


import sys
import json
import requests
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_logging


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: r_bot 类
-------
@param:
-------
@return:
"""
class r_bot:

    """
    @description: 初始化
    -------
    @param: token<str>
    -------
    @return:
    """
    def __init__(self,
                 proxies=None,
                 token=rab_config.load_package_config(
                     "rab_config.ini", "rab_bot", "telegram_token")):
        self.token = token
        self.url = "https://api.telegram.org/bot" + self.token
        self.proxies = proxies
        self.is_connected = False
        # 测试连接
        self.test()
        # 存放收到各用户最后一条消息的 message_id
        self.chat_id_last_message_id = {}
    
    """
    @description: 测试对 Telegram 的访问
    -------
    @param:
    -------
    @return:
    """
    def test(self):
        # 先尝试不使用代理或使用传入代理进行访问测试
        try:
            result = requests.get("https://core.telegram.org/bots",
                proxies=self.proxies, timeout=5)
            if (result.status_code == 200):
                self.is_connected = True
                r_logger.info("Telegram Bot 使用代理 {} 访问测试成功！".format(
                    str(self.proxies)))
            else:
                self.is_connected = False
                r_logger.error("Telegram Bot 使用代理 {} 访问测试失败！".format(
                    str(self.proxies)))
        except Exception:
            self.is_connected = False
            r_logger.error("Telegram Bot 使用代理 {} 访问测试出错！".format(
                str(self.proxies)))
            r_logger.error(e)
        # 如果不能连接则尝试配置文件中的代理
        if (not self.is_connected):
            r_logger.info("Telegram Bot 开始尝试配置文件中的代理......")
            for proxy in rab_config.load_package_config(
                    "rab_config.ini", "common", "proxy"):
                try:
                    proxies = {
                        "http": proxy,
                        "https": proxy
                    }
                    result = requests.get("https://core.telegram.org/bots",
                        proxies=proxies, timeout=5)
                    if (result.status_code == 200):
                        self.proxies = proxies
                        self.is_connected = True
                        r_logger.info("Telegram Bot 开始使用代理：{}".format(
                            str(proxies)))
                        break
                    else:
                        r_logger.error("Telegram Bot 无法使用代理：{}".format(
                            str(proxies)))
                except Exception as e:
                    r_logger.error("Telegram Bot 尝试代理 {} 出错！".format(
                        str(proxies)))
                    r_logger.error(e)
            r_logger.error("Telegram Bot 尝试所有配置文件中的代理均无法访问！")


    """
    @description: 获取最新的聊天记录
    -------
    @param:
    -------
    @return:
    """
    def get_latest_messages(self):
        # 判断是否能连接 Telegram 服务器
        if (self.is_connected):
            # 获取聊天记录的 API 地址
            get_updates_url = self.url + "/getUpdates"
            try:
                response = requests.get(get_updates_url, proxies=self.proxies,
                    verify=False)
                messages = json.loads(response.text)
                # 继上次获取后的新信息列表
                latest_messages = []
                for message in messages["result"]:
                    # 获取 CHAT ID
                    chat_id = message["message"]["chat"]["id"]
                    # 如果第一次收到信息，或 message_id 比既存的还要大
                    if (chat_id not in self.chat_id_last_message_id.keys() 
                            or (message["message"]["message_id"] 
                                > self.chat_id_last_message_id[chat_id])):
                        # 时间较早的在队列前面
                        latest_messages.append(message)
                        self.chat_id_last_message_id[chat_id] \
                            = message["message"]["message_id"]
                # 将新消息替换响应中消息列表
                messages["result"] = latest_messages
                if (len(latest_messages) > 0):
                    return {
                        "ok": True,
                        "result":latest_messages,
                        "description": "共 {} 条新消息！".format(
                            len(latest_messages))
                    }
                else:
                    return {"ok": True, "result":[], "description": "无新消息！"}
            except Exception as e:
                return {"ok": False, "description": "出错：{}".format(str(e))}
        else:
            return {"ok": False, "description": "无法连接到 Telegram 服务器！"}
    
    """
    @description: 发送信息
    -------
    @param: chat_id<str>, message<str>
    -------
    @return:
    """
    def send_message(self,
                     message,
                     chat_id=rab_config.load_package_config(
                         "rab_config.ini", "rab_bot", "telegram_chat_id"),
                     parse_mode=None):
        # 判断是否能连接 Telegram 服务器
        if (self.is_connected):
            # 发送聊天信息的 API 地址
            send_message_url = self.url + "/sendMessage"
            params = {
                "parse_mode": parse_mode
            }
            data = {
                "chat_id": chat_id,
                "text": message
            }
            try:
                response = requests.post(send_message_url, params=params, \
                    data=data, proxies=self.proxies, verify=False)
                return json.loads(response.text)
            except Exception as e:
                return {"ok": False, "description": "出错：{}".format(str(e))}
        else:
            return {"ok": False, "description": "无法连接到 Telegram 服务器！"}


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    r_bot = r_bot()
    # 测试基础功能
    print(r_bot.get_latest_messages())
    print(r_bot.send_message("*"*45))
    # 测试表格
    message = """
```
| BBB |
| AAA |
| Symbol | Price | Change |
|--------|-------|--------|
| ABC    | 20.85 |  1.626 |
| DEF    | 78.95 |  0.099 |
| GHI    | 23.45 |  0.192 |
| JKL    | 98.85 |  0.292 |
```
"""
    print(r_bot.send_message(message, parse_mode="Markdown"))