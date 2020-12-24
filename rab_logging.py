#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: \rab_python_packages\rab_logging.py
# @DATE: 2020/12/16 Wed
# @TIME: 16:50:21
#
# @DESCRIPTION: 共通包 日志记录模块


import os
import logging
from datetime import datetime


"""
@description: logger 初始化配置
-------
@param:
-------
@return:
"""
def build_rab_logger():
    logging.basicConfig(filemode="a",
                        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        level=logging.INFO)
    logger = logging.getLogger("RAB_LOGGER")
    # 判断路径是否存在，不在的话就在上层路径查找
    if (os.path.exists("log")):
        fh = logging.FileHandler(
            "log/{:%Y-%m-%d}.log".format(datetime.now()))
    elif (os.path.exists("../log")):
        fh = logging.FileHandler(
            "../log/{:%Y-%m-%d}.log".format(datetime.now()))
    # 如果上一层也没有路径，则直接在本包中创建临时日志文件夹
    else:
        if (not os.path.exists("rab_log")):
            os.makedirs("rab_log")
        fh = logging.FileHandler(
            "rab_log/{:%Y-%m-%d}.log".format(datetime.now()))
    formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | " \
                                  + "%(filename)s | %(funcName)s | " \
                                  + "行:%(lineno)04d | %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    rab_logger = build_rab_logger()
    rab_logger.debug("debug")
    rab_logger.info("info")
    rab_logger.warning("warning")
    rab_logger.error("error")
    rab_logger.critical("critical")



