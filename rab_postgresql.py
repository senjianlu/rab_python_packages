#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_postgresql.py
# @DATE: 2020/12/17 周四
# @TIME: 11:03:40
#
# @DESCRIPTION: 共通包 PostgreSQL 数据库驱动


import sys
import datetime
import psycopg2
import psycopg2.extras
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_requests
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
@description: r_pgsql_user 类
-------
@param:
-------
@return:
"""
class r_pgsql_user():

    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self, user=None, time=None, ip=None):
        # 用户名
        self.user = user
        self.user = self.get_user()
        # 更新时间
        self.time = None
        # IP
        self.ip = rab_requests.get_ip_info()["ip"] if not ip else ip
    
    """
    @description: 获取用户
    -------
    @param:
    -------
    @return:
    """
    def get_user(self):
        # 如果当前没有用户名
        if (not self.user):
            # 获得数据库用户
            try:
                if (rab_config.load_package_config(
                        "rab_config.ini", "common", "user")):
                    self.user = str(rab_config.load_package_config(
                        "rab_config.ini", "common", "user"))
                else:
                    self.user = "unknown_pgsql_user"
            except Exception as e:
                self.user = "unknown_pgsql_user"
        # 如果当前没有节点备注
        if ("(" not in self.user):
            # 节点名作为附加
            try:
                if (rab_config.load_package_config("rab_config.ini", \
                        "rab_distributed_system", "node_id")):
                    self.user += " ({})".format(str(
                        rab_config.load_package_config("rab_config.ini", \
                            "rab_distributed_system", "node_id")))
            except Exception as e:
                pass
        return self.user
    
    """
    @description: 获取当前时间
    -------
    @param:
    -------
    @return:
    """
    def get_time(self):
        return datetime.datetime.now(datetime.timezone.utc)
    
    """
    @description: 获取 IP
    -------
    @param:
    -------
    @return:
    """
    def get_ip(self):
        return self.ip


"""
@description: r_pgsql_driver 类
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
        # 批量插入数
        self.batch_size = int(rab_config.load_package_config(
            "rab_config.ini", "rab_postgresql", "batch_size"))
        # 指针
        self.cur = None
        # 与数据库之间的连接
        self.conn = None
        # 用户
        self.r_pgsql_user = r_pgsql_user(user=self.user)

    """
    @description: 建立数据库连接
    -------
    @param:
    -------
    @return:
    """
    def connect(self):
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
    def test(self):
        test_sql = "SELECT 1;"
        try:
            self.cur.execute(test_sql)
            result_list = self.cur.fetchall()
            if (result_list):
                return True
        except Exception:
            pass
        return False

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
    @description: 数据库重连
    -------
    @param:
    -------
    @return:
    """
    def reconnect(self):
        self.close()
        self.connect()
    
    """
    @description: 查询语句
    -------
    @param: sql<str>, data<list>
    -------
    @return: <list>
    """
    def select(self, sql, data=None):
        # 测试当前连接是否可用，不可用则重连
        if (not self.test()):
            self.reconnect()
        try:
            self.cur.execute(sql, data)
            select_result = self.cur.fetchall()
            r_logger.info("查询成功！")
            r_logger.info("SQL 文：{}".format(str(sql)))
            r_logger.info("参数：{}".format(str(data))) if data else False
            if (len(str(select_result)) > 120):
                r_logger.info("结果：{select_result}......行数{row_num}".format(
                    select_result=str(select_result)[0:100], row_num=str(
                        len(select_result))))
            else:
                r_logger.info("结果：{}".format(str(select_result)))
            return select_result
        except Exception as e:
            r_logger.error("查询失败！")
            r_logger.error(e)
            r_logger.error("SQL 文：{}".format(str(sql)))
            r_logger.error("参数：{}".format(str(data))) if data else False
            return []

    """
    @description: 执行单一 SQL 语句
    -------
    @param:
    -------
    @return:
    """
    def execute(self, sql, data=None):
        # 测试当前连接是否可用，不可用则重连
        if (not self.test()):
            self.reconnect()
        try:
            self.cur.execute(sql, data)
            self.conn.commit()
            r_logger.info("SQL 执行成功！")
            r_logger.info("SQL 文：{}".format(str(sql)))
            r_logger.info("参数：{}".format(str(data))) if data else False
            return True
        except Exception as e:
            r_logger.error("SQL 执行失败！")
            r_logger.error(e)
            r_logger.error("SQL 文：{}".format(str(sql)))
            r_logger.info("参数：{}".format(str(data))) if data else False
            return False

    """
    @description: 插入语句
    -------
    @param: sql<str>, data<list>
    -------
    @return: <list>
    """
    def insert(self, sql, data=None):
        return self.execute(sql, data)
    
    """
    @description: 更新语句
    -------
    @param: sql<str>, data<list>
    -------
    @return: <list>
    """
    def update(self, sql, data=None):
        return self.execute(sql, data)
    
    """
    @description: 删除语句
    -------
    @param: sql<str>, data<list>
    -------
    @return: <list>
    """
    def delete(self, sql, data=None):
        return self.execute(sql, data)
    
    """
    @description: 清空表
    -------
    @param: table_name<str>
    -------
    @return: <bool>
    """
    def delete_all(self, table):
        sql = "DELETE FROM {}".format(table)
        return self.execute(sql)

    """
    @description: 根据提供的 SQL 语句处理多条数据
    -------
    @param: sql<str>, data<list>
    -------
    @return: <bool>
    """
    def execute_many(self, sql, data):
        # 测试当前连接是否可用，不可用则重连
        if (not self.test()):
            self.reconnect()
        try:
            # executemany 因为效率问题放弃
            # cur.executemany(sql, data)
            # 改为 execute_batch
            psycopg2.extras.execute_batch(
                self.cur, sql, data, page_size=self.batch_size)
            self.conn.commit()
            r_logger.info("数据插入或更新成功！")
            r_logger.info("SQL 文：{}".format(str(sql)))
            r_logger.info("数据：{data}......行数：{row_num}".format(
                data=str(data)[0:40], row_num=str(len(data))))
            return True
        except Exception as e:
            r_logger.error("数据插入或更新失败！")
            r_logger.error(e)
            r_logger.error("SQL 文：{}".format(str(sql)))
            r_logger.error("数据：{data}......行数：{row_num}".format(
                data=str(data), row_num=str(len(data))))
            return False


"""
@description: 单体测试
-------
@param:
-------
@return:
"""
if __name__ == "__main__":
    r_pgsql_driver = r_pgsql_driver()
    print(r_pgsql_driver.select("SELECT 1;"))
    print(r_pgsql_driver.r_pgsql_user.get_user())
    print(r_pgsql_driver.r_pgsql_user.get_time())
    print(r_pgsql_driver.r_pgsql_user.get_ip())