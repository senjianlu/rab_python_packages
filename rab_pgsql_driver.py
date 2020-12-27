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
        # 如果现在有连接就直接用
        if (not (self.cur and self.conn)):
            self.create()
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
        finally:
            self.close()
        return result_bool

    """
    @description: 根据提供的 SQL 语句处理多条数据
    -------
    @param: sql<str>, data<list>
    -------
    @return: <bool>
    """
    def execute_many(self, sql, data):
        # 如果现在有连接就直接用
        if (not (self.cur and self.conn)):
            self.create()
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
        finally:
            self.close()
        return result_bool

    """
    @description: 查询语句
    -------
    @param: sql<str>, args<list>
    -------
    @return: <list>
    """
    def select(self, sql, args=None):
        # 如果现在有连接就直接用
        if (not (self.cur and self.conn)):
            self.create()
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
        finally:
            self.close()
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