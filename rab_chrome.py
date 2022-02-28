#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_chrome.py
# @DATE: 2021/07/30 Fri
# @TIME: 23:00:08
#
# @DESCRIPTION: 共通包 Chrome 浏览器构建和控制


import re
import os
import sys
import time
import requests
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_logging
from rab_python_packages import rab_node


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: 获取当前操作系统
-------
@param:
-------
@return:
"""
def get_system_type():
    if ("windows" in str(platform.platform()).lower()):
        return "windows"
    else:
        return "linux"

"""
@description: Windows 系统下在指定端口构建 Chrome 浏览器
-------
@param:
-------
@return:
"""
def construct_chrome(port):
    try:
        build_command = 'start "" chrome.exe ' \
            + '--remote-debugging-port= ' + str(port) \
            + '--user-data-dir="C:\selenum\AutomationProfile"'
        os.system(build_command)
        time.sleep(3)
        r_logger.info("Windows 系统下端口 {} 上 Chrome 启动成功！".format(
            str(port)))
    except Exception as e:
        r_logger.error("Windows 系统下端口 {} 上 Chrome 启动失败！".format(
            str(port)))
        r_logger.error(e)

"""
@description: 关闭 GOST
-------
@param:
-------
@return:
"""
def gost_stop(local_proxy_port):
    gost_stop_command = rab_config.load_package_config(
        "rab_linux_command.ini", "rab_chrome", "gost_stop")
    gost_stop_command += " {}".format(str(local_proxy_port))
    os.system(gost_stop_command)

"""
@description: 开启 GOST
-------
@param:
-------
@return:
"""
def gost_start(local_proxy_port, proxy):
    gost_start_command = rab_config.load_package_config(
        "rab_linux_command.ini", "rab_chrome", "gost_start")
    # 添加启动参数
    gost_start_command += " -p {}".format(str(local_proxy_port))
    proxy_info = rab_node.parse_http_or_socks5_node_url(proxy)
    gost_start_command += " -A {}".format(str(proxy_info["type"]))
    gost_start_command += " -U {}".format(str(proxy_info["username"]))
    gost_start_command += " -D {}".format(str(proxy_info["password"]))
    gost_start_command += " -H {}".format(str(proxy_info["server"]))
    gost_start_command += " -P {}".format(str(proxy_info["port"]))
    os.system(gost_start_command)


"""
@description: r_chrome 类
-------
@param:
-------
@return:
"""
class r_chrome():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self,
                 driver=None,
                 port=None,
                 proxy=None,
                 local_proxy_port=1080):
        # chromedriver
        self.driver = driver
        # 浏览器起的端口
        self.port = port
        # 使用的代理
        self.proxy = proxy
        # 需要验证代理转发时所用的本地端口
        self.local_proxy_port = local_proxy_port
        # 需要验证代理转发用 GOST
        self.is_gost_used = False
        # 操作系统
        self.system = get_system_type()
    
    """
    @description: 构建浏览器
    -------
    @param:
    -------
    @return:
    """
    def build(self):
        # 浏览器配置
        capabilities = DesiredCapabilities.CHROME
        capabilities["goog:loggingPrefs"] = {"browser": "ALL"}
        chrome_options = Options()
        # Windows 系统
        if (self.system == "windows"):
            r_logger.info("Windows 系统下 Chrome 构建开始......")
            # 如果指定了端口
            if (self.port):
                # 在指定端口构建浏览器
                construct_chrome(self.port)
                # 接管端口上的浏览器
                chrome_options.add_experimental_option(
                    "debuggerAddress", "127.0.0.1:"+str(self.port))
            # 如果没有指定端口
            else:
                pass
            # 提前将 chromedriver 路径加入环境变量中
            chrome_driver = "chromedriver.exe"
        # Linux 系统
        elif(self.system == "linux"):
            r_logger.info("Linux 系统下 Chrome 构建开始......")
            # Linux 无头无界面浏览器配置
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("window-size=1024,768")
            chrome_options.add_argument("--no-sandbox")
            # 无需认证的代理则直接加上属性即可
            if(self.proxy):
                # 如果需要验证的话
                if ("@" in self.proxy):
                    # 通过 GOST 转发
                    gost_stop(self.local_proxy_port)
                    gost_start(self.local_proxy_port, self.proxy)
                    # 本地代理信息
                    proxy = "socks5://127.0.0.1:{}".format(
                        str(self.local_proxy_port))
                    self.is_gost_used = True
                # 如果不需要验证的话
                else:
                    proxy = self.proxy
                # 浏览器代理的配置
                chrome_options.add_argument(
                    "--proxy-server={}".format(proxy))
                r_logger.info("Linux 系统下 Chrome 使用代理：{}，原代理：{}" \
                    .format(proxy, self.proxy))
            # 提前建立了软连接的 chromedriver
            chrome_driver = "chromedriver"
        # Windows 和 Linux 分开配置完成后，建立浏览器
        try:
            self.driver = webdriver.Chrome(chrome_driver, \
                desired_capabilities=capabilities, options=chrome_options)
            r_logger.info("{} 系统下 Chrome 构建成功！".format(
                self.system.capitalize()))
            return True
        except Exception as e:
            r_logger.error("{} 系统下 Chrome 构建失败！".format(
                self.system.capitalize()))
            r_logger.error(e)
            return False

    """
    @description: 为无界面浏览器导入 jQuery
    -------
    @param:
    -------
    @return:
    """
    def import_jquery(self):
        jquery_js_text = requests.get("https://libs.baidu.com/jquery/2.0.0/" \
            + "jquery.min.js").text
        self.driver.execute_script(jquery_js_text)
        # 循环 10 秒等待导入成功
        for _ in range(0, 10):
            test_jquery_js = "$('head').append('<p>jquery_test</p>');"
            try:
                self.driver.execute_script(test_jquery_js)
                r_logger.info("无头浏览器 jQuery 加载完成！")
                return True
            except Exception as e:
                r_logger.info("无头浏览器等待 jQuery 加载中......")
                time.sleep(1)
        r_logger.error("无头浏览器 jQuery 加载失败！")
        return False
    
    """
    @description: 关闭浏览器
    -------
    @param:
    -------
    @return:
    """
    def close(self):
        # 关闭 GOST
        if (self.is_gost_used):
            gost_stop(self.local_proxy_port)
        # Windows 系统
        if (self.system == "windows"):
            r_logger.info("Windows 系统下开始关闭 Chrome......")
            # 如果指定了端口
            if (self.port):
                # 查找对应端口的进程
                cmd_command = 'netstat -aon|findstr "{}"'.format(str(self.port))
                cmd_driver = os.popen(cmd_command)
                try:
                    cmd_msg = cmd_driver.read().split("\n")[0]
                    cmd_msgs = cmd_msg.split("       ")
                    # 获取端口对应的 PID 用来杀死进程
                    pid = re.findall(r"\d+\.?\d*", cmd_msgs[-1])[0]
                    cmd_driver = os.popen(
                        "taskkill -f /pid {}".format(str(pid)))
                    # 返回信息
                    cmd_msg = cmd_driver.read()
                    if ("成功" in cmd_msg):
                        r_logger.info("Windows 系统下关闭浏览器成功！")
                        return True
                    else:
                        r_logger.error(
                            "Windows 系统下关闭浏览器失败！错误：{}".format(
                                str(cmd_msg)))
                except Exception as e:
                    r_logger.error("Windows 系统下关闭浏览器失败！")
                    r_logger.error(e)
                finally:
                    cmd_driver.close()
                return False
            # 如果没有指定端口
            else:
                self.driver.quit()
                r_logger.info("Windows 系统下关闭浏览器成功！")
                return True
        # Linux 系统
        else:
            r_logger.info("Linux 系统下开始关闭 Chrome......")
            if (self.driver):
                self.driver.quit()
            r_logger.info("Linux 系统下关闭浏览器成功！")
            return True
        
    """
    @description: 等待元素出现
    -------
    @param:
    -------
    @return:
    """
    def wait_appear(self, xpath, max_wait_time=10):
        for _ in range(0, timeout):
            try:
                element = slef.driver.find_element_by_xpath(xpath)
                return True
            except Exception as e:
                time.sleep(1)
        return False

    """
    @description: 重启浏览器
    -------
    @param:
    -------
    @return:
    """
    def restart(self):
        # 关闭现有浏览器
        if (self.driver):
            self.close()
        # 新建浏览器
        self.build()
        

"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    # r_chrome = r_chrome()
    # r_chrome.build()
    # r_chrome.restart()
    # r_chrome.driver.get("https://baidu.com")
    # time.sleep(3)
    # print(r_chrome.driver.page_source)
    # r_chrome.close()
    proxy = "socks5://127.0.0.1:1080"
    gost_start(33333, proxy)