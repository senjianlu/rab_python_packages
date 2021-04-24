#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: \rab_python_packages\rab_steam.py
# @DATE: 2021/02/03 Wed
# @TIME: 17:18:46
#
# @DESCRIPTION: 共通 Steam 模块（操作基本基于 Selenium）


import hmac
import time
import base64
import struct
import selenium
from hashlib import sha1
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from rab_python_packages import rab_logging


# 日志记录
rab_steam_logger = rab_logging.build_rab_logger()


"""
@description: r_steam 类
-------
@param:
-------
@return:
"""
class r_steam:

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self, driver, username, password, token_flg=False, \
            shared_secret=None, identity_secret=None):
        self.driver = driver
        self.username = username
        self.password = password
        # 令牌标识
        self.token_flg = token_flg
        # 令牌分享码
        self.shared_secret = shared_secret
        self.identity_secret = identity_secret

    """
    @description: 切换至 Steam 登录窗口
    -------
    @param:
    -------
    @return:
    """
    def switch_to_steam_login_window(self, exclude_field):
        success_flg = False
        for window_handle in self.driver.window_handles:
            self.driver.switch_to.window(window_handle)
            # 判断不包含排除字段但是包含 STEAM 字段的窗口即为 STEAM 登录窗口
            if (exclude_field.lower() not in str(self.driver.title).lower()
                    and "steam" in str(self.driver.title).lower()):
                success_flg = True
                break
            else:
                continue
        return success_flg
    
    """
    @description: 切换回原窗口
    -------
    @param:
    -------
    @return:
    """
    def switch_to_origin_window(self, fill_field):
        success_flg = False
        for window_handle in self.driver.window_handles:
            self.driver.switch_to.window(window_handle)
            # 包含满足要求字段的窗口即为原窗口
            if (fill_field.lower() in str(self.driver.title).lower()):
                success_flg = True
                break
            else:
                continue
        return success_flg

    """
    @description: 生成 STEAM 登录一次性令牌
    -------
    @param:
    -------
    @return:
    """
    def generate_one_time_code(self):
        timestamp = int(time.time())
        time_buffer = struct.pack(">Q", timestamp//30)
        time_hmac = hmac.new(base64.b64decode(self.shared_secret),
                             time_buffer,
                             digestmod=sha1).digest()
        begin = ord(time_hmac[19:20]) & 0xf
        full_code = struct.unpack(">I",
                                  time_hmac[begin:begin+4])[0] & 0x7fffffff
        chars = "23456789BCDFGHJKMNPQRTVWXY"
        code = ""
        for j in range(5):
            full_code, i = divmod(full_code, len(chars))
            code += chars[i]
        return code

    """
    @description: 在 STEAM 登录界面实现登录
    -------
    @param:
    -------
    @return:
    """
    def do_steam_login(self):
        try:
            # 等待登录按钮出现
            element = WebDriverWait(self.driver, 30, 0.1).until(
                EC.presence_of_element_located((By.XPATH,
                    "//input[@id='imageLogin']")))
            # 检查是否已经登录
            try:
                time.sleep(1)
                # 如果有当前账户名说明已经登录完成了
                account_div = self.driver.find_element_by_class_name(
                    "OpenID_loggedInAccount")
                logined_flg = True
            except Exception as e:
                logined_flg = False
            # 登录的情况下进行登出操作
            if (logined_flg):
                print("Steam 当前已经处于登录状态，尝试登出...")
                # 选择登出这个账号
                logout_div_a = self.driver.find_element_by_xpath(
                    "//div[@class='OpenID_Logout']/a")
                logout_div_a.click()
            # STEAM 用户名输入框
            steam_account_name_input = self.driver \
                                    .find_element_by_id("steamAccountName")
            # STEAM 密码输入框
            steam_password_input = self.driver \
                                    .find_element_by_id("steamPassword")
            # 输入用户名和密码
            steam_account_name_input.send_keys(self.username)
            steam_password_input.send_keys(self.password)
            # 点击登录按钮
            self.driver.find_element_by_id("imageLogin").click()
            # 无令牌的情况下或者当前已经是登录状态就算登录成功
            if (not self.token_flg):
                return True
            else:
                # 等待需要令牌的弹窗出现
                element = WebDriverWait(self.driver, 30, 0.1).until(
                    EC.presence_of_element_located((By.XPATH,
                        "//input[@id='twofactorcode_entry']")))
                twofactorcode_entry_input = self.driver.find_element_by_id(
                    "twofactorcode_entry")
                # 等待三秒弹窗可见后，生成并输入令牌
                time.sleep(3)
                twofactorcode_entry_input.send_keys(
                    self.generate_one_time_code())
                # 提交按钮
                submit_btn = self.driver.find_element_by_xpath(
                    "//div[@id='login_twofactorauth_buttonset_entercode']/div")
                submit_btn.click()
                return True
        except Exception as e:
            # 登录失败
            rab_steam_logger.error("Steam 登录界面操作出错！错误信息：" + str(e))
            return False

    """
    @description: 等待 Steam 登录成功并自动关闭窗口
    -------
    @param:
    -------
    @return:
    """
    def wait_steam_login_success(self, fill_field):
        for i in range(0, 10):
            if (len(self.driver.window_handles) == 1
                    and fill_field.lower() in str(self.driver.title).lower()):
                return True
            else:
                time.sleep(2)
                continue
        return False


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    print("todo...")
