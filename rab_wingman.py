#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_wingman.py
# @DATE: 2021/07/22 Thu
# @TIME: 15:24:59
#
# @DESCRIPTION: 多线程小帮手


import sys
import time
sys.path.append("..") if ".." not in sys.path else True
from rab_python_packages import rab_logging


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: r_wingman 多线程小帮手类
-------
@param:
-------
@return:
"""
class r_wingman:

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self):
        # 线程字典
        self.thread = {}
        # 线程当前状态
        self.thread_is_over = {}
    
    """
    @description: 启动全部线程
    -------
    @param:
    -------
    @return:
    """
    def start_all(self):
        r_logger.info("开始启动全部线程......")
        for thread_key in self.thread.keys():
            self.thread[thread_key].setDaemon(True)
            self.thread[thread_key].start()
            # 标志线程启动
            self.thread_is_over[thread_key] = False
        for thread_key in self.thread.keys():
            self.thread[thread_key].join()

    """
    @description: 标志线程结束
    -------
    @param:
    -------
    @return:
    """
    def over(self, thread_key):
        r_logger.info("线程 {} 结束。".format(str(thread_key)))
        self.thread_is_over[thread_key] = True

    """
    @description: 是否所有线程均结束
    -------
    @param:
    -------
    @return:
    """
    def is_all_over(self):
        for thread_key in self.thread.keys():
            if (not self.thread_is_over[thread_key]):
                return False
        return True
    
    """
    @description: 等待所有线程结束
    -------
    @param:
    -------
    @return:
    """
    def wait(self):
        while True:
            if (self.is_all_over()):
                r_logger.info("检测到所有线程均已结束！")
                return True
            else:
                r_logger.info("等待所有线程结束中......")
                time.sleep(10)