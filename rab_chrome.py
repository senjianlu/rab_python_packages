#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: \rab_python_packages\rab_chrome.py
# @DATE: 2020/12/16 Wed
# @TIME: 17:31:00
#
# @DESCRIPTION: 共通包 Chrome 浏览器构建


import os
import re
import time
import urllib
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
# 切换路径到父级
import sys
sys.path.append("..")
from rab_python_packages import rab_logging


# 日志记录
rab_chrome_logger = rab_logging.build_rab_logger()


"""
@description: 在指定端口构建浏览器
-------
@param: port_num<int>
-------
@return:
"""
def build_chrome(port_num, headless=False):
    # Linux 下什么都不做
    if (headless):
        return True
    # Windows 下在对应端口起浏览器
    else:
        try:
            cmd_command = 'start "" chrome.exe --remote-debugging-port=' \
                        + str(port_num) \
                        + ' --user-data-dir="C:\selenum\AutomationProfile_"' \
                        + str(port_num)
            cmd_driver = os.system(cmd_command)
            time.sleep(1)
        except Exception as e:
            rab_chrome_logger.error("创建浏览器时出错：" + str(e))

"""
@description: 检查指定端口是否有浏览器进程
-------
@param: port_num<int>
-------
@return:
"""
def check_chrome(port_num, headless=False):
    # Linux 下什么都不做
    if (headless):
        return True
    # Windows 下检验对应端口是否被占用
    else:
        try:
            cmd_command = 'netstat -aon|findstr "' + str(port_num) + '"'
            cmd_driver = os.popen(cmd_command)
            cmd_msg = cmd_driver.read()
            cmd_driver.close()
            # 如果返回值为空 创建失败
            if (cmd_msg):
                return True
            else:
                rab_chrome_logger.error("浏览器没有创建！")
                return False
        except Exception as e:
            rab_chrome_logger.error("检查浏览器时出错：" + str(e))
            cmd_driver.close()
            return False

"""
@description: 关闭指定端口的浏览器进程
-------
@param: port_num<int>
-------
@return:
"""
def close_chrome(port_num, headless=False):
    # Linux 下什么都不做
    if (headless):
        return True
    # Windows 下杀指定端口的进程
    else:
        try:
            cmd_command = 'netstat -aon|findstr "' + str(port_num) + '"'
            cmd_driver = os.popen(cmd_command)
            cmd_msg = cmd_driver.read().split("\n")[0]
            cmd_msgs = cmd_msg.split("       ")
            # 获取端口对应的 PID 用来杀死进程
            pp_id = re.findall(r"\d+\.?\d*", cmd_msgs[-1])[0]
            cmd_driver = os.popen('taskkill -f /pid '+str(pp_id))
            cmd_msg = cmd_driver.read()
            cmd_driver.close()
            if ("成功" in cmd_msg):
                return True
            else:
                rab_chrome_logger.error("关闭浏览器失败！")
                return False
        except Exception as e:
            rab_chrome_logger.error("关闭浏览器时出错：" + str(e))
            cmd_driver.close()
            return False

"""
@description: Windows 下在指定端口创建浏览器并在指定秒数后关闭
-------
@param: port_num<int>, wait_second<int>
-------
@return:
"""
def build_chrome_and_wait(port_num, wait_second):
    build_chrome(port_num)
    time.sleep(int(wait_second))
    close_chrome(port_num)

"""
@description: 接管指定端口的浏览器并返回 driver
-------
@param:
-------
@return:
"""
def get_driver(port_num, headless=False):
    capabilities = DesiredCapabilities.CHROME
    capabilities['loggingPrefs'] = { 'browser':'ALL' }
    chrome_options = Options()
    # Linux 下，不启动 Chrome 界面
    if (headless):
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument("window-size=1024,768")
        chrome_options.add_argument("--no-sandbox")
        # 需要提前建立软连接
        # ln -f /home/opc/selenium-online/chromedriver /usr/bin/chromedriver
        chrome_driver = "chromedriver"
        driver = webdriver.Chrome(chrome_driver,
                                  desired_capabilities=capabilities,
                                  options=chrome_options)
    # Windows 下接管对应端口的浏览器
    else:
        chrome_options.add_experimental_option("debuggerAddress",
                                            "127.0.0.1:"+str(port_num))
        x86_chrome_path = "C:\Program Files (x86)\Google" \
                        + "\Chrome\Application"
        x32_chrome_path = "C:\Program Files\Google" \
                        + "\Chrome\Application"
        if (os.path.exists(x86_chrome_path)):
            chrome_driver = x86_chrome_path + "\chromedriver.exe"
        else:
            chrome_driver = x32_chrome_path + "\chromedriver.exe"
        driver = webdriver.Chrome(chrome_driver,
                                  desired_capabilities=capabilities,
                                  options=chrome_options)
    return driver

"""
@description: 在本地起 Chrome 并执行 JS 后关闭
-------
@param: port_num<int>, web_url<str>, js<str>
-------
@return: <json>
"""
def build_chrome_and_execute_script(port_num,
                                    web_url,
                                    js,
                                    build_wait_time=3,
                                    get_wait_time=3,
                                    headless=False):
    # Linux 下启动无界面 Chrome 并导入 Jquery 后执行 JS
    if (headless):
        try:
            driver = get_driver(port_num, headless)
            # 前往地址
            driver.get(web_url)
            time.sleep(get_wait_time)
            # 导入 Jquery
            import_jquery_js = """
            var importJs = document.createElement("script");
            importJs.setAttribute("type","text/javascript")
            importJs.setAttribute("src",
                'https://ajax.aspnetcdn.com/ajax/jQuery/jquery-3.1.0.min.js')
            document.getElementsByTagName("head")[0].appendChild(importJs)
            """
            driver.execute_script(import_jquery_js)
            # 等待 5 秒 Jquery 加载完成
            time.sleep(5)
            rab_chrome_logger.info("Liunx 下无头浏览器" \
                                    + " 网址：" + str(web_url) \
                                    + "\r执行 JS：" + str(js))
            result = driver.execute_script(js)
        except Exception as e:
            err_msg = "Linux 下无头起 CHROMR 并执行 JS 时出错！" + str(e)
            rab_chrome_logger.error(err_msg)
        finally:
            driver.close()
    # Windows 下在指定端口建浏览器并执行 JS，然后关闭浏览器
    else:
        try:
            if (not check_chrome(port_num)):
                build_chrome(port_num)
                time.sleep(build_wait_time)
            driver = get_driver(port_num)
            # 设置页面加载超时时长
            # driver.set_page_load_timeout(get_wait_time)
            # driver.set_script_timeout(get_wait_time)
            # 只确保网址正确以应对接口的跨域禁止问题
            if (not driver.current_url.split("://")[1].split("/")[0]
                    == web_url.split("://")[1].split("/")[0]):
                try:
                    driver.get(web_url)
                    time.sleep(get_wait_time)
                # 超时则停止网页加载
                except:
                    driver.execute_script("window.stop()")
            if (js):
                js = urllib.parse.unquote(js)
            rab_chrome_logger.info("端口：" + str(port_num) \
                                   + " 网址：" + str(web_url) \
                                   + "\r执行 JS：" + str(js))
            result = driver.execute_script(js)
        except Exception as e:
            err_msg = "本地起 CHROMR 并执行 JS 时出错！" + str(e)
            rab_chrome_logger.error(err_msg)
        finally:
            close_chrome(port_num)
    return result


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    build_chrome(9222)
    time.sleep(2)
    check_chrome(9222)
    time.sleep(2)
    close_chrome(9222)
