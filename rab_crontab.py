#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/steammarket/rab_python_packages/rab_crontab.py
# @DATE: 2021/08/12 Thu
# @TIME: 09:30:35
#
# @DESCRIPTION: 定时任务模块


import sys
import time
import calendar
import datetime
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_logging


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: 获取上一个整分、整时、整天的时间戳
-------
@param:
-------
@return:
"""
def get_last_whole_timestamp(timestamp=int(time.time()), method="minute"):
    if (method=="minute"):
        return ((timestamp//60)) * 60
    elif(method=="hour"):
        return ((timestamp//3600)) * 3600
    elif(method=="day"):
        return ((timestamp//86400)) * 86400
    elif(method=="month"):
        return int(time.mktime(datetime.date(
            datetime.date.today().year, \
            datetime.date.today().month,1).timetuple()))
    else:
        return None

"""
@description: 获取下一个整分、整时、整天的时间戳
-------
@param:
-------
@return:
"""
def get_next_whole_timestamp(timestamp=int(time.time()), method="minute"):
    if (method=="minute"):
        return ((timestamp//60)+1) * 60
    elif(method=="hour"):
        return ((timestamp//3600)+1) * 3600
    elif(method=="day"):
        return ((timestamp//86400)+1) * 86400
    elif(method=="month"):
        return int(time.mktime(datetime.date(
            datetime.date.today().year, \
            datetime.date.today().month,1).timetuple()))
    else:
        return None

"""
@description: 解析 crontab 时间规则以获取分、时、日
-------
@param:
-------
@return:
"""
def parse_crontab_time_setting(crontab_time_setting):
    minute = crontab_time_setting[0]
    hour = crontab_time_setting[1]
    day_of_month = crontab_time_setting[2]
    month = crontab_time_setting[3]
    day_of_week = crontab_time_setting[4]
    # 暂不支持每周和每月固定日期执行
    if (month != "*" and day_of_week != "*"):
        r_logger.error("定时任务模块暂不支持指定月和指定星期执行！")
        return None
    # 获取需要定时执行的分钟数
    minutes = []
    if (minute != "*"):
        # 单个分钟
        if (minute.isdigit()):
            minutes = [int(minute)]
        # 手动设定多个
        elif("," in minute):
            for m in minute.split(","):
                minutes.append(int(m))
        # 每隔固定时间执行
        elif("/" in minute):
            for m in range(0, 60):
                if (m%int(minute.split("/")[1]) == 0):
                    minutes.append(int(m))
    else:
        minutes = list(range(0, 60))
    # 获取需要定时执行的小时数
    hours = []
    if (hour != "*"):
        # 单个分钟
        if (hour.isdigit()):
            hours = [int(hour)]
        # 手动设定多个
        elif("," in hour):
            for h in hour.split(","):
                hours.append(int(h))
        # 每隔固定时间执行
        elif("/" in hour):
            for h in range(0, 24):
                if (h%int(hour.split("/")[1]) == 0):
                    hours.append(int(h))
    else:
        hours = list(range(0, 24))
    # 获取需要定时执行的天数（以月为单位）
    day = day_of_month
    days = []
    week, days_num = calendar.monthrange(
        datetime.datetime.now().year, datetime.datetime.now().month)
    if (day != "*"):
        # 单个分钟
        if (day.isdigit()):
            days = [int(day)]
        # 手动设定多个
        elif("," in day):
            for d in day.split(","):
                days.append(int(d))
        # 每隔固定时间执行
        elif("/" in day):
            for d in range(1, days_num+1):
                if (d%int(day.split("/")[1]) == 0):
                    days.append(int(d))
    else:
        days = list(range(1, days_num+1))
    return minutes, hours, days

"""
@description: 获取当月所有满足要求的时间点时间戳
-------
@param:
-------
@return:
"""
def get_run_timestamps(crontab_time_setting):
    # 先生成所有符合 crontab 要求的时间戳
    run_timestamps = []
    minutes, hours, days = parse_crontab_time_setting(
        crontab_time_setting)
    for day in days:
        for hour in hours:
            for minute in minutes:
                this_timestamp = get_last_whole_timestamp("month") \
                    + day*86400 + hour*3600 + minute*60
                run_timestamps.append(this_timestamp)
    return run_timestamps


"""
@description: r_crontab 类
-------
@param:
-------
@return:
"""
class r_crontab():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self):
        self.task = {}
    
    """
    @description: 新增任务，默认周期为 30 天
    -------
    @param:
    -------
    @return:
    """
    def add(self, task_name, crontab_time_setting):
        self.task[task_name] = {"crontab_time_setting": crontab_time_setting}
    
    """
    @description: 运行一次任务以记录时间戳
    -------
    @param:
    -------
    @return:
    """
    def run(self, task_name):
        self.task[task_name]["last_run_over_timestamp"] = None
        self.task[task_name]["last_run_start_timestamp"] = int(time.time())
    
    """
    @description: 记录运行结束
    -------
    @param:
    -------
    @return:
    """
    def over(self, task_name):
        self.task[task_name]["last_run_over_timestamp"] = int(time.time())

    """
    @description: 获取下一次运行的时间戳
    -------
    @param:
    -------
    @return:
    """
    def get_next_run_timestamp(self, task_name):
        run_timestamps = get_run_timestamps(
            self.task[task_name]["crontab_time_setting"])
        for run_timestamp in run_timestamps:
            if (run_timestamp > int(time.time())):
                return run_timestamp
    
    """
    @description: 等待下一次运行时间的到来
    -------
    @param:
    -------
    @return:
    """
    def wait(self, task_name):
        next_run_timestamp = self.get_next_run_timestamp(task_name)
        r_logger.info("下一次 {task_name} 任务执行的时间：{time}".format(
            task_name=task_name, time=time.strftime(
                "%Y-%m-%d %H:%M:%S",time.localtime(next_run_timestamp))))
        r_logger.info("等待中......")
        while True:
            if (int(time.time()) > next_run_timestamp):
                return True
            else:
                time.sleep(1)
    
    """
    @description: 距上次运行结束是否是新的分钟、小时、天
    -------
    @param:
    -------
    @return:
    """
    def is_new(self, task_name, method="day"):
        # 如果没有开始过
        if ("last_run_start_timestamp" not in self.task[task_name].keys()):
            return True
        # 如果还没结束
        elif(not "last_run_over_timestamp"):
            return False
        # 如果开始过则判定是否到了新的时间点
        else:
            if (method=="minute"):
                if ((int(time.time())-get_last_whole_timestamp(self.task[
                        task_name]["last_run_over_timestamp"], "minute")) >= 60):
                    return True
                else:
                    return False
            elif (method=="hour"):
                if ((int(time.time())-get_last_whole_timestamp(self.task[
                        task_name]["last_run_over_timestamp"], "hour")) >= 3600):
                    return True
                else:
                    return False
            elif (method=="day"):
                if ((int(time.time())-get_last_whole_timestamp(self.task[
                        task_name]["last_run_over_timestamp"], "day")) >= 86400):
                    return True
                else:
                    return False


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    r_crontab = r_crontab()
    r_crontab.add("test", ["0", "0", "*", "*", "*"])
    r_crontab.run("test")
    r_crontab.over("test")
    # r_crontab.wait("test")
    while True:
        time.sleep(10)
        print("是否到了新的分钟：{}".format(
            str(r_crontab.is_new("test", "minute"))))
        print("是否到了新的小时：{}".format(
            str(r_crontab.is_new("test", "hour"))))