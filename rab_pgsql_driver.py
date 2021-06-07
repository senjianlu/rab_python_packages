#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: \rab_python_packages\rab_pgsql_driver.py
# @DATE: 2020/12/17 周四
# @TIME: 11:03:40
#
# @DESCRIPTION: 共通包 PostgreSQL 数据库驱动


import psycopg2
import psycopg2.extras
# 切换路径到父级
import sys
sys.path.append("..")
from rab_python_packages import rab_logging


# 日志记录
rab_pgsql_driver_logger = rab_logging.build_rab_logger()


"""
@description: 批量插入数值获取
-------
@param:
-------
@return: batch_size<int>
"""
def get_batch_size():
    return 500


"""
@description: r_proxy 类
-------
@param:
-------
@return:
"""
class r_pgsql_driver():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self, database, user, password, host, port):
        self.database = database
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.cur = None
        self.conn = None

    """
    @description: 建立数据库连接
    -------
    @param:
    -------
    @return:
    """
    def create(self):
        # 创建连接对象
        self.conn = psycopg2.connect(database=self.database,
                                     user=self.user,
                                     password=self.password,
                                     host=self.host,
                                     port=self.port)
        self.cur = self.conn.cursor() #创建指针对象

    """
    @description: 测试数据库连接是否可用
    -------
    @param:
    -------
    @return: bool
    """
    def test_connection(self):
        test_sql = "SELECT 1;"
        try:
            self.cur.execute(test_sql)
            result_list = self.cur.fetchall()
            if (result_list):
                return True
        except Exception:
            return False
        return False

    """
    @description: 数据库重连
    -------
    @param:
    -------
    @return:
    """
    def reconnect(self):
        if (not (self.cur and self.conn)):
            self.create()
        else:
            # 暂时注释以等待较好的重连解决方法
            # self.conn = self.conn.reconnect()
            # self.cur = self.conn.cursor()
            self.create()

    """
    @description: 关闭数据库连接
    -------
    @param:
    -------
    @return:
    """
    def close(self):
        if (self.cur):
            self.cur.close()
        if (self.conn):
            self.conn.close()
        self.cur = None
        self.conn = None

    """
    @description: 清空数据库
    -------
    @param: table_name<str>
    -------
    @return: <bool>
    """
    def delete_all(self, table_name):
        # 测试当前连接是否可用，不可用则重连
        if (not self.test_connection()):
            self.reconnect()
        sql = "DELETE FROM " + str(table_name)
        try:
            self.cur.execute(sql)
            self.conn.commit()
            rab_pgsql_driver_logger.info(str(table_name) + " 表清空成功！")
            result_bool = True
        except Exception as e:
            rab_pgsql_driver_logger.error(str(table_name) \
                                        + " 表清空失败！" \
                                        + str(e))
            result_bool = False
        return result_bool

    """
    @description: 执行单一 SQL 语句
    -------
    @param:
    -------
    @return:
    """
    def execute(self, sql):
        # 测试当前连接是否可用，不可用则重连
        if (not self.test_connection()):
            self.reconnect()
        try:
            self.cur.execute(sql)
            self.conn.commit()
            rab_pgsql_driver_logger.info(str(sql) + " SQL 执行成功！")
            result_bool = True
        except Exception as e:
            rab_pgsql_driver_logger.error(str(sql) \
                                        + " SQL 执行失败！" \
                                        + str(e))
            result_bool = False
        return result_bool

    """
    @description: 根据提供的 SQL 语句处理多条数据
    -------
    @param: sql<str>, data<list>
    -------
    @return: <bool>
    """
    def execute_many(self, sql, data):
        # 测试当前连接是否可用，不可用则重连
        if (not self.test_connection()):
            self.reconnect()
        try:
            # executemany 因为效率问题放弃
            # cur.executemany(sql, data)
            # 改为 execute_batch
            psycopg2.extras.execute_batch(self.cur,
                                          sql,
                                          data,
                                          page_size=get_batch_size())
            self.conn.commit()
            rab_pgsql_driver_logger.info(" 数据处理成功！" \
                                        + "\r SQL 语句：" + str(sql) \
                                        + "\r 数据：" + str(data)[0:40] \
                                        + "..." \
                                        + " 长度：" + str(len(data)))
            result_bool = True
        except Exception as e:
            rab_pgsql_driver_logger.error(" 数据处理失败！" \
                                        + str(e) \
                                        + "\r SQL 语句：" + str(sql) \
                                        + "\r 数据：" + str(data)
                                        + " 长度：" + str(len(data)))
            result_bool = False
        return result_bool

    """
    @description: 查询语句
    -------
    @param: sql<str>, args<list>
    -------
    @return: <list>
    """
    def select(self, sql, args=None):
        # 测试当前连接是否可用，不可用则重连
        if (not self.test_connection()):
            self.reconnect()
        try:
            self.cur.execute(sql, args)
            result_list = self.cur.fetchall()
            info_msg = " 查询成功！" \
                       + "\r SQL 语句：" + str(sql) \
                       + "\r 参数：" + str(args) \
                       + "\r 数据：" \
                       + str(result_list)[0:100] + "..." \
                       + " 长度：" + str(len(result_list))
            rab_pgsql_driver_logger.info(info_msg)
        except Exception as e:
            result_list = []
            err_msg = " 查询失败！" \
                       + str(e) \
                       + "\r SQL 语句：" + str(sql) \
                       + "\r 参数：" + str(args)
            rab_pgsql_driver_logger.error(err_msg)
        return result_list


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    # todo...
    print("todo...")