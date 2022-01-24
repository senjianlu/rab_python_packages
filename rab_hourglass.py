#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_hourglass.py
# @DATE: 2022/01/24 Mon
# @TIME: 20:32:05
#
# @DESCRIPTION: 沙漏计时


import time
from threading import Thread


"""
@description: 沙漏类
-------
@param:
-------
@return:
"""
class r_hourglass():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self, countdown_seconds, function_2_execute):
        self.countdown_seconds = countdown_seconds
        self.function_2_execute = function_2_execute
        self.last_seconds = 0
        self.countdown_thread = None
    
    """
    @description: 倒计时
    -------
    @param:
    -------
    @return:
    """
    def countdown(self):
        while(self.last_seconds > 0):
            time.sleep(1)
            self.last_seconds = self.last_seconds - 1
            print("沙漏剩余 {} 秒......".format(
                str(self.last_seconds)))
        return self.function_2_execute()
    
    """
    @description: 沙漏开始
    -------
    @param:
    -------
    @return:
    """
    def start(self):
        print("沙漏开始计时！")
        self.last_seconds = self.countdown_seconds
        self.countdown_thread = Thread(target=self.countdown)
        self.countdown_thread.setDaemon(True)
        self.countdown_thread.start()

    """
    @description: 重置沙漏
    -------
    @param:
    -------
    @return:
    """
    def reset(self):
        print("沙漏被重置！")
        self.last_seconds = self.countdown_seconds


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    def test_function():
        print("我被执行了！")
    r_hourglass = r_hourglass(15, test_function)
    r_hourglass.start()
    time.sleep(20)
