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
from singleton_decorator import singleton
# 切换路径到父级
import sys
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_env
from rab_python_packages import rab_config


"""
@description: logger 初始化配置
-------
@param:
-------
@return:
"""
def build_logger():
    # 默认打印和记录日志等级为：info
    logging.basicConfig(filemode="a",
                        format="%(asctime)s %(name)s:%(levelname)s:%(message)s",
                        datefmt="%Y/%m/%d %H:%M:%S",
                        level=logging.INFO)
    logger = logging.getLogger("RAB_LOGGER")
    # 在 rab_python_packages 同级目录下创建 rab_logs 日志存放用文件夹
    path = rab_env.find_rab_python_packages_path()
    # 判断是否存在现有的 rab_logs 日志存放用文件夹
    if (path):
        rab_logs_path = path + "rab_logs"
    else:
        rab_logs_path = "rab_logs"
    if (not os.path.exists(rab_logs_path)):
        os.makedirs(rab_logs_path)
    # 以天为单位存储日志
    fh = logging.FileHandler(
        (rab_logs_path+"/{:%Y%m%d}.log").format(datetime.now()))
    # 日志存储格式
    formatter = logging.Formatter("%(asctime)s | %(levelname)-8s | " \
                                  + "%(filename)s | %(funcName)s | " \
                                  + "行:%(lineno)04d | %(message)s")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger

"""
@description: 获取 logging 的等级对象
-------
@param:
-------
@return:
"""
def get_logging_level(level):
    if (level.lower() == "debug"):
        return logging.DEBUG
    elif(level.lower() == "info"):
        return logging.INFO
    elif(level.lower() == "warn"):
        return logging.WARN
    elif(level.lower() == "error"):
        return logging.ERROR
    elif(level.lower() == "critical"):
        return logging.CRITICAL

"""
@description: log 等级比较
-------
@param:
-------
@return:
"""
def get_weight(level):
    if (level):
        level_weight = {
            "debug": 1,
            "info": 2,
            "warn": 3,
            "error": 4,
            "critical": 5
        }
        return level_weight[level]
    else:
        return 0


"""
@description: r_logger 类
-------
@param:
-------
@return:
"""
# 单例模式
@singleton
class r_logger():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self,
                 level="info",
                 logger=build_logger(),
                 telegarm_notice_level=rab_config.load_package_config(
                     "rab_config.ini", "rab_logging", "level").lower(),
                 qq_notice_level=None):
        # logger 对象
        self.logger = logger
        # 修改 logger 对象的日志记录等级
        self.logger.setLevel(get_logging_level(level))
        # Telegram 机器人通知等级（大于等于这个等级的都进行通知，None 为不通知）
        self.telegarm_notice_level = telegarm_notice_level
        # QQ 机器人通知等级
        self.qq_notice_level = qq_notice_level
    
    """
    @description: 机器人通知
    -------
    @param:
    -------
    @return:
    """
    def send_log(self, log_level, log):
        # Telegram 机器人通知
        if (get_weight(log_level) >= get_weight(self.telegarm_notice_level)):
            pass
        # QQ 机器人通知
        if (get_weight(log_level) >= get_weight(self.qq_notice_level)):
            pass

    """
    @description: debug 日志等级方法重写
    -------
    @param:
    -------
    @return:
    """
    def debug(self, log):
        self.send_log("debug", log)
        self.logger.debug(log)
    
    """
    @description: info 日志等级方法重写
    -------
    @param:
    -------
    @return:
    """
    def info(self, log):
        self.send_log("info", log)
        self.logger.info(log)
    
    """
    @description: warn 日志等级方法重写
    -------
    @param:
    -------
    @return:
    """
    def warn(self, log):
        self.send_log("warn", log)
        self.logger.warning(log)
    
    """
    @description: error 日志等级方法重写
    -------
    @param:
    -------
    @return:
    """
    def error(self, log):
        # 单纯的消息直接记录
        if (type(log) == str):
            pass
        # 如果是错误类
        else:
            error = log
            # 获取错误行号
            error_no = str(error.__traceback__.tb_lineno)
            # 获取出错的文件
            error_file = str(error.__traceback__.tb_frame.f_globals["__file__"])
            # 错误信息
            error_msg = str(error).strip()
            # 具体日志
            log = "出错！文件 {error_file} 第 {error_no} 行，报错：{error_msg}" \
                .format(error_file=error_file, error_no=error_no, \
                    error_msg=error_msg)
        self.send_log("error", log)
        self.logger.error(log)
    
    """
    @description: critical 日志等级方法重写
    -------
    @param:
    -------
    @return:
    """
    def critical(self, log):
        self.send_log("critical", log)
        self.logger.critical(log)
    

"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    r_logger = r_logger("warn")
    r_logger.debug("debug")
    r_logger.info("info")
    r_logger.warn("warn")
    r_logger.error("error")
    try:
        a = 123
        b = 456
        import aaa
    except Exception as e:
        r_logger.error(e)
    r_logger.critical("critical")