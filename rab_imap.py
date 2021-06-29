#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_imap.py
# @DATE: 2021/06/29 Tue
# @TIME: 13:50:40
#
# @DESCRIPTION: 共通包 IMAP 邮件收发相关类和方法封装


import email
import imaplib


"""
@description: 从邮件 Message 中获取邮件标题
-------
@param:
-------
@return:
"""
def get_mail_title(mail_message):
    return mail_message.get("subject")

"""
@description: 从邮件 Message 中获取邮件内容
-------
@param:
-------
@return:
"""
def get_mail_content(mail_message):
    mail_content = ""
    for row in mail_message.walk():
        if (not row.is_multipart()):            
            mail_content += row.get_payload(decode=True).decode("utf-8")
    return mail_content


"""
@description: IMAP 类
-------
@param:
-------
@return:
"""
class r_imap():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self, imap_url, imap_port, imap_username, imap_password):
        # 邮件服务提供商 IMAP 地址
        self.url = imap_url
        # 端口
        self.port = imap_port
        # 用户名
        self.username = imap_username
        # 密码
        self.password = imap_password
        # IMAP client
        self.client = self.login()

    """
    @description: IMAP 登录
    -------
    @param:
    -------
    @return:
    """
    def login(self):
        client = imaplib.IMAP4_SSL(self.url, self.port)
        client.login(self.username, self.password)
        return client
    
    """
    @description: 获取所有邮件 Message
    -------
    @param:
    -------
    @return:
    """
    def get_all_mails(self):
        all_mails = []
        status, count = r_imap.client.select("Inbox")
        status, mail_no_list_data = r_imap.client.search(None, "ALL")
        mail_no_list = mail_no_list_data[0].split()
        for mail_no in mail_no_list:
            status, mail_data = r_imap.client.fetch(mail_no, "(RFC822)")
            mail_message = email.message_from_string(
                mail_data[0][1].decode("utf-8"))
            all_mails.append(mail_message)
        return all_mails

    """
    @description: 根据标题关键词获取指定邮件列表
    -------
    @param:
    -------
    @return:
    """
    def serach_title(self, keyword_4_search):
        keyword_4_search = keyword_4_search.lower()
        mails = []
        all_mails = self.get_all_mails()
        for mail_message in all_mails:
            if (keyword_4_search in get_mail_title(mail_message).lower()):
                mails.append(mail_message)
        return mails


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    r_imap = r_imap("imap.gmail.com", 993, "username@gmail.com", "password")
    mails = r_imap.serach_title("Welcome")
    for mail in mails:
        print(get_mail_content(mail))
