#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: \rab_python_packages\rab_proxy.py
# @DATE: 2020/12/15 Tue
# @TIME: 19:46:49
#
# @DESCRIPTION: 共通包 多线程爬虫数据储存用模块


import time


"""
@description: r_storage 类
-------
@param:
-------
@return:
"""
class r_storage:

    """
    @description: 初始化
    -------
    @param: web<str>, length_limit<int>
    -------
    @return:
    """
    def __init__(self, web, length_limit, infos=[]):
        self.web = web
        self.length_limit = length_limit
        self.infos = infos
        self.lock_flg = False
        self.max_tries = 10
        self.wait_time = 0.1
    
    """
    @description: 上锁
    -------
    @param:
    -------
    @return:
    """
    def lock(self):
        self.lock_flg = True
    
    """
    @description: 解锁
    -------
    @param:
    -------
    @return:
    """
    def unlock(self):
        self.lock_flg = False

    """
    @description: 新增数据
    -------
    @param:
    -------
    @return:
    """
    def append(self, info):
        for i in range(0, self.max_tries):
            if (not self.lock_flg):
                self.lock()
                self.infos.append(info)
                self.unlock()
                # 返回成功
                return True
            else:
                time.self(self.wait_time)
        # 返回失败
        return False


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    r_storage = r_storage("test_web", 100)
    for i in range(0, 10):
        r_storage.append(i)
        print(r_storage.infos)