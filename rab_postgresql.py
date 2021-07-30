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
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_logging
from rab_python_packages import rab_config


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: 获取批量插入数值
-------
@param:
-------
@return: batch_size<int>
"""
def get_batch_size():
    return int(rab_config.load_package_config(
                "rab_config.ini", "rab_postgresql", "batch_size"))


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
    def __init__(self,
                 database=rab_config.load_package_config(
                     "rab_config.ini", "common", "database"),
                 user=rab_config.load_package_config(
                     "rab_config.ini", "common", "user"),
                 password=rab_config.load_package_config(
                     "rab_config.ini", "common", "password"),
                 host=rab_config.load_package_config(
                     "rab_config.ini", "common", "host"),
                 port=rab_config.load_package_config(
                     "rab_config.ini", "common", "port"),
                 show_column_name=False):
        # 数据库名
        self.database = database
        # 用户
        self.user = user
        # 密码
        self.password = password
        # IP 或域名
        self.host = host
        # 端口
        self.port = port
        # 是否显示列名
        self.show_column_name = show_column_name
        # 指针
        self.cur = None
        # 与数据库之间的连接
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
        #创建指针对象
        if (self.show_column_name):
            self.cur = self.conn.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor)
        else:
            self.cur = self.conn.cursor()

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
        sql = "DELETE FROM {}".format(table_name)
        try:
            self.cur.execute(sql)
            self.conn.commit()
            r_logger.info("{} 表清空成功！".format(table_name))
            return True
        except Exception as e:
            r_logger.error("{} 表清空失败！".format(table_name))
            r_logger.error(e)
            r_logger.error("SQL 文："+str(sql))
            return False

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
            r_logger.info("SQL 执行成功！")
            r_logger.info("SQL 文："+str(sql))
            return True
        except Exception as e:
            r_logger.error("SQL 执行失败！")
            r_logger.error(e)
            r_logger.error("SQL 文："+str(sql))
            return False

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
            r_logger.info("数据插入或更新成功！")
            r_logger.info("SQL 文："+str(sql))
            r_logger.info("数据："+str(data)[0:40]+"......行数："+str(len(data)))
            return True
        except Exception as e:
            r_logger.error("数据插入或更新失败！")
            r_logger.error(e)
            r_logger.error("SQL 文："+str(sql))
            r_logger.error("数据："+str(sql))
            return False

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
            r_logger.info("查询成功！")
            r_logger.info("SQL 文："+str(sql))
            r_logger.info("参数："+str(args)) if args else False
            if (len(str(result_list)) > 120):
                r_logger.info("结果："+str(result_list)[0:100] \
                    +"......行数："+str(len(result_list)))
            else:
                r_logger.info("结果："+str(result_list))
            return result_list
        except Exception as e:
            r_logger.error("查询失败！")
            r_logger.error(e)
            r_logger.error("SQL 文："+str(sql))
            r_logger.error("参数："+str(args)) if args else False
            return []


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    pass