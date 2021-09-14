#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_distributed_node.py
# @DATE: 2021/07/25 Sun
# @TIME: 14:54:27
#
# @DESCRIPTION: 分布式系统管理模块


import sys
from datetime import datetime, timezone, timedelta
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_logging
from rab_python_packages import rab_postgresql


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: 获取当前机器的节点 ID
-------
@param:
-------
@return:
"""
def get_node_id():
    node_id = rab_config.load_package_config(
        "rab_config.ini", "rab_distributed_system", "node_id")
    return node_id

"""
@description: 获取此节点延迟
-------
@param:
-------
@return:
"""
def get_node_delay_time():
    # 获取节点所需要等待的单位时间
    node_delay_time = rab_config.load_package_config(
        "rab_config.ini", "rab_distributed_system", "node_delay_time")
    # 获取节点序号，除开 main 之外均需等待
    node_no = get_node_id().split("_")[-1]
    if ("main" ==  node_no.lower()):
        return 0
    elif(node_no.isdigit()):
        return int(node_delay_time)*int(node_no)
    else:
        return 0


"""
@description: 系统状态类
-------
@param:
-------
@return:
"""
class r_status():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self,
                 project,
                 subproject,
                 module=None,
                 function=None,
                 status=None,
                 start_time=None,
                 over_time=None,
                 result=None):
        self.project = project
        self.subproject = subproject
        self.module = module
        self.function = function
        self.status = status
        self.start_time = start_time
        self.over_time = over_time
        self.result = result
    
    """
    @description: 更新
    -------
    @param:
    -------
    @return:
    """
    def update(self, r_pgsql_driver):
        update_sql = """
        INSERT INTO
            sa_status(
                ss_project,
                ss_subproject,
                ss_method,
                ss_function,
                ss_status,
                ss_start_time,
                ss_over_time,
                ss_result,
                ss_history
            ) VALUES(
                %s, %s, %s, %s, %s,
                %s, %s, %s, '{}'
            ) ON CONFLICT(ss_project, ss_subproject, ss_method, ss_function)
            DO UPDATE SET
                ss_status = %s,
                ss_start_time = %s,
                ss_over_time = %s,
                ss_result = %s
        """
        data = [
            self.project,
            self.subproject,
            self.module,
            self.function,
            self.status,
            self.start_time,
            self.over_time,
            self.result,
            self.status,
            self.start_time,
            self.over_time,
            self.result
        ]
        r_pgsql_driver.update(update_sql, data)
    
    """
    @description: 保存运行结果
    -------
    @param:
    -------
    @return:
    """
    def save(self, r_pgsql_driver):
        update_sql = """
            UPDATE
		        sa_status
            SET
	            ss_history = ss_history || JSONB_BUILD_OBJECT(
                    TO_CHAR(ss_start_time AT TIME ZONE 'Asia/Shanghai',
                        'YYYY-MM-DD HH24:MI:SS'),
                    ss_result)
            WHERE
                ss_project = %s
            AND ss_subproject = %s
            AND ss_method = %s
            AND ss_function = %s
        """
        data = [self.project, self.subproject, self.module, self.function]
        r_pgsql_driver.update(update_sql, data)

    """
    @description: 方法开始
    -------
    @param:
    -------
    @return:
    """
    def start(self, r_pgsql_driver, module=None, function=None):
        if (module):
            self.module = module
        if (function):
            self.function = function
        self.status = "running"
        self.start_time = datetime.now(timezone.utc)
        self.over_time = None
        self.result = None
        self.update(r_pgsql_driver)
        r_logger.info("方法 {} 开始！".format(self.function))

    """
    @description: 方法结束
    -------
    @param:
    -------
    @return:
    """
    def over(self, result, r_pgsql_driver, module=None, function=None):
        if (module):
            self.module = module
        if (function):
            self.function = function
        self.status = "over"
        # self.start_time = None
        self.over_time = datetime.now(timezone.utc)
        self.result = result
        self.update(r_pgsql_driver)
        self.save(r_pgsql_driver)
        r_logger.info("方法 {} 结束！".format(self.function))
    
    """
    @description: 方法出错
    -------
    @param:
    -------
    @return:
    """
    def error(self, result, r_pgsql_driver, module=None, function=None):
        if (module):
            self.module = module
        if (function):
            self.function = function
        self.status = "error"
        # self.start_time = None
        self.over_time = datetime.now(timezone.utc)
        self.result = result
        self.update(r_pgsql_driver)
        r_logger.error("方法 {} 出错！".format(self.function))


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":

    import time

    r_pgsql_driver = rab_postgresql.r_pgsql_driver()
    try:
        r_status = r_status("test_project", "test_subproject", "test_module")
        r_status.start(r_pgsql_driver, function="test_function")
        time.sleep(10)
        r_status.over("test_result", r_pgsql_driver, function="test_function")
    except Exception as e:
        r_logger.error("单体测试出错！")
        r_logger.error(e)
    finally:
        r_pgsql_driver.close()