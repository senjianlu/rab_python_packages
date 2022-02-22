#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_crontab.py
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
    if (method == "minute"):
        return ((timestamp//60)) * 60
    elif(method == "hour"):
        return ((timestamp//3600)) * 3600
    elif(method == "day"):
        return ((timestamp//86400)) * 86400
    elif(method == "month"):
        return int(time.mktime(datetime.date(
            datetime.date.today().year, \
            datetime.date.today().month, 1).timetuple()))
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
    if (method == "minute"):
        return ((timestamp//60)+1) * 60
    elif(method == "hour"):
        return ((timestamp//3600)+1) * 3600
    elif(method == "day"):
        return ((timestamp//86400)+1) * 86400
    elif(method == "month"):
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
        # 单个小时
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
    # 获取需要定时执行的天数（以月为单位，并且会拓展到下个月 1 日 24 点）
    day = day_of_month
    days = []
    week, days_num = calendar.monthrange(
        datetime.datetime.now().year, datetime.datetime.now().month)
    if (day != "*"):
        # 单个日期
        if (day.isdigit()):
            days = [int(day)]
        # 手动设定多个
        elif("," in day):
            for d in day.split(","):
                days.append(int(d))
        # 每隔固定时间执行
        elif("/" in day):
            # 每月 1 日必定符合
            days.append(0)
            # 循环剩余日期
            for d in range(1, days_num+1):
                if (d%int(day.split("/")[1]) == 0):
                    days.append(int(d))
    else:
        days = list(range(0, days_num+1))
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
                this_timestamp = get_last_whole_timestamp(method="month") \
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
        self.task[task_name] = {
            "crontab_time_setting": crontab_time_setting,
            "run_timestamps": get_run_timestamps(crontab_time_setting),
            "no_stop": False}
    
    """
    @description: 续约任务
    -------
    @param:
    -------
    @return:
    """
    def renew(self, task_name):
        self.task[task_name]["run_timestamps"] = get_run_timestamps(
            self.task[task_name]["crontab_time_setting"])
    
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
        # 如果接下来剩下少于一个可用的时间戳则进行续约
        available_run_timestamps = []
        for run_timestamp in self.task[task_name]["run_timestamps"]:
            if (run_timestamp >= int(time.time())):
                available_run_timestamps.append(run_timestamp)
        if (len(available_run_timestamps) <= 1):
            self.renew(task_name)

    """
    @description: 获取下一次运行的时间戳
    -------
    @param:
    -------
    @return:
    """
    def get_next_run_timestamp(self, task_name):
        for run_timestamp in self.task[task_name]["run_timestamps"]:
            if (run_timestamp > int(time.time())):
                return run_timestamp
        return None
    
    """
    @description: 到了运行的时间点
    -------
    @param:
    -------
    @return:
    """
    def is_time_2_run(self, task_name):
        # 如果是不间断运行则直接返回 True
        if (self.task[task_name]["no_stop"]):
            return True
        # 如果曾经开始并结束过
        if ("last_run_over_timestamp" in self.task[task_name].keys()
                and self.task[task_name]["last_run_over_timestamp"]):
            # 遍历所有需要运行的时间戳
            for run_timestamp_index, run_timestamp in enumerate(
                    self.task[task_name]["run_timestamps"]):
                # 判断当前时间戳是否比上次运行时间点的下一次时间戳还要大
                if ((self.task[task_name]["last_run_over_timestamp"] \
                            >= run_timestamp)
                        and (self.task[task_name]["last_run_over_timestamp"] \
                            < self.task[task_name]["run_timestamps"][(
                                run_timestamp_index+1)])
                        and (int(time.time()) >= self.task[task_name][
                            "run_timestamps"][(run_timestamp_index+1)])):
                    return True
            # 时间戳循环结束返回 False
            return False
        # 未开始过则直接开始
        else:
            return True

    """
    @description: 等待下一次运行时间的到来
    -------
    @param:
    -------
    @return:
    """
    def wait(self, task_name):
        # 如果是不间断运行则直接返回 True
        if (self.task[task_name]["no_stop"]):
            return True
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
                        task_name]["last_run_start_timestamp"], "minute")) \
                            >= 60):
                    return True
                else:
                    return False
            elif (method=="hour"):
                if ((int(time.time())-get_last_whole_timestamp(self.task[
                        task_name]["last_run_start_timestamp"], "hour")) \
                            >= 3600):
                    return True
                else:
                    return False
            elif (method=="day"):
                if ((int(time.time())-get_last_whole_timestamp(self.task[
                        task_name]["last_run_start_timestamp"], "day")) \
                            >= 86400):
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
    r_crontab.add("test", ["*/3", "*", "*", "*", "*"])
    print(len(r_crontab.task["test"]["run_timestamps"]))
    # r_crontab.wait("test")

    # 测试到点执行
    # while True:
    #     time.sleep(10)
    #     if (r_crontab.is_time_2_run("test")):
    #         r_crontab.run("test")
    #         print("run")
    #         r_crontab.over("test")
    #     print("wait next: {}".format(r_crontab.get_next_run_timestamp("test")))