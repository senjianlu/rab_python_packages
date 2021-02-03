#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: \rab_python_packages\rab_steam.py
# @DATE: 2021/02/03 Wed
# @TIME: 17:18:46
#
# @DESCRIPTION: 共通 Steam 模块（操作基本基于 Selenium）


import selenium


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
    def __init__(self, driver, username, password, \
                    token_flg=False, shared_secret=None):
        self.driver = driver
        self.username = username
        self.password = password
        # 令牌标识
        self.token_flg = token_flg
        # 令牌分享码
        self.shared_secret = shared_secret

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
    @description: 在 STEAM 登录界面实现登录
    -------
    @param:
    -------
    @return:
    """
    def do_steam_login(self):
        try:
            # STEAM 用户名输入框
            steam_account_name_input = self.driver
                                        .find_element_by_id("steamAccountName")
            # STEAM 密码输入框
            steam_password_input = self.driver
                                        .find_element_by_id("steamPassword")
            # 输入用户名和密码
            steam_account_name_input.send_keys(self.username)
            steam_password_input.send_keys(self.steam_password)
            # 点击登录按钮
            self.driver.find_element_by_id("imageLogin").click()
            # 无令牌的情况下就算登录成功
            if (not self.token_flg):
                return True
            else:
                print("todo...")
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
    def wait_steam_login_success(self):
        for i in range(0, 10):
            if (len(self.driver.window_handles) > 1):
                time.sleep(2)
                continue
            else:
                return True
        return False
