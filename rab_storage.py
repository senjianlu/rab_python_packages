#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /rab_python_packages/rab_storage.py
# @DATE: 2021/01/22 Fri
# @TIME: 14:38:05
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
        self.counter = 0
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
                # 数据插入并计数 + 1
                self.infos.append(info)
                self.counter = self.counter + 1
                self.unlock()
                # 返回成功
                return True
            else:
                time.self(self.wait_time)
        # 返回失败
        return False
    
    """
    @description: 拷贝出数据并清空
    -------
    @param:
    -------
    @return:
    """
    def copy_and_clean(self):
        for i in range(0, self.max_tries):
            if (not self.lock_flg):
                self.lock()
                # 数据插入并计数 + 1
                infos_copy = self.infos
                self.infos = []
                self.unlock()
                # 返回成功
                return infos_copy
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
    print(r_storage.copy_and_clean())
    print(r_storage.infos)
