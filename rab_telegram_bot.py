#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: \rab_python_packages\rab_telegram_bot.py
# @DATE: 2020/12/16 Wed
# @TIME: 16:29:07
#
# @DESCRIPTION: 共通包 Telegram Bot 机器人消息推送模块


import json
import requests
# 切换路径到父级
import sys
sys.path.append("..")
from rab_python_packages import rab_logging


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
    def __init__(self, token):
        self.token = token
        self.url = "https://api.telegram.org/bot" + self.token
        # 字典 {chat_id<str>: last_message_id<int>}
        self.chat_id_last_message_id = {}
    
    """
    @description: 获取最新的聊天记录
    -------
    @param:
    -------
    @return:
    """
    def get_latest_messages(self):
        # 获取最新的聊天记录的链接
        get_updates_url = self.url + "/getUpdates"
        try:
            r = requests.get(get_updates_url)
            result = json.loads(r.text)
            # 继上次获取后的新信息列表
            latest_messages = []
            for message in result["result"]:
                # 获取用户 ID
                # from_id = message["message"]["from"]["id"]
                # 获取 CHAT ID
                chat_id = message["message"]["chat"]["id"]
                # 如果第一次获取这个对话消息
                #     或者 message_id 比既存的还要大，即为新的信息
                if (chat_id not in self.chat_id_last_message_id.keys() 
                        or (message["message"]["message_id"] 
                            > self.chat_id_last_message_id[chat_id])):
                    latest_messages.append(message)
                    self.chat_id_last_message_id[chat_id] \
                        = message["message"]["message_id"]
            # 如果有最新的消息
            result["result"] = latest_messages
            if (len(latest_messages) > 0):
                return result
            else:
                return {"ok": False, "description": "暂无新消息！"}
        except Exception as e:
            return {"ok": False, "description": str(e)}
    
    """
    @description: 发送信息
    -------
    @param: chat_id<str>, message<str>
    -------
    @return:
    """
    def send_message(self, chat_id, message):
        # 发送信息的链接
        send_message_url = self.url + "/sendMessage"
        params = {
            "chat_id": chat_id,
            "text": message
        }
        try:
            r = requests.post(send_message_url, params=params)
            return json.loads(r.text)
        except Exception as e:
            return {"ok": False, "description": str(e)}


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    # todo...
    print("todo...")