#!/usr/bin/env python
# -*- coding:UTF-8 -*-
#
# @AUTHOR: Rabbir
# @FILE: /root/GitHub/rab_python_packages/rab_rabbitmq.py
# @DATE: 2021/07/12 Mon
# @TIME: 14:39:42
#
# @DESCRIPTION: 共通包 RabbitMQ 消息队列方法模块


import sys
import json
import uuid
import pika
import time
import requests
sys.path.append("..") if (".." not in sys.path) else True
from rab_python_packages import rab_config
from rab_python_packages import rab_logging


# 日志记录
r_logger = rab_logging.r_logger()


"""
@description: RabbitMQ 对象
-------
@param:
-------
@return:
"""
class r_rabbitmq():
    
    """
    @description: 初始化
    -------
    @param:
    -------
    @return:
    """
    def __init__(self,
                 username=rab_config.load_package_config(
                     "rab_config.ini", "rab_rabbitmq", "username"),
                 password=rab_config.load_package_config(
                     "rab_config.ini", "rab_rabbitmq", "password"),
                 host=rab_config.load_package_config(
                     "rab_config.ini", "rab_rabbitmq", "host"),
                 port=rab_config.load_package_config(
                     "rab_config.ini", "rab_rabbitmq", "port"),
                 api_host=rab_config.load_package_config(
                     "rab_config.ini", "rab_rabbitmq", "api_host")):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.api_host = api_host
        self.connection = {}
        self.channel = {}
    
    """
    @description: 建立连接
    -------
    @param:
    -------
    @return:
    """
    def connect(self, connection_name):
        auth = pika.PlainCredentials(self.username, self.password)
        try:
            self.connection[connection_name] = pika.BlockingConnection(
                pika.ConnectionParameters(self.host, int(self.port), "/", auth))
            return True
        except Exception as e:
            r_logger.error(
                "RabbitMQ 建立连接 {} 时出错！".format(connection_name))
            r_logger.error(e)
            return False
    
    """
    @description: 建立频道
    -------
    @param:
    -------
    @return:
    """
    def build_channel(self, connection_name, channel_name):
        if (channel_name not in self.channel.keys()):
            self.channel[channel_name] = self.connection[
                connection_name].channel()
        else:
            r_logger.warn("RabbitMQ 已经存在频道：{}".format(channel_name))
    
    """
    @description: 关闭连接
    -------
    @param:
    -------
    @return:
    """
    def disconnect(self):
        # 关闭所有频道
        if (self.channel):
            for channel_name in self.channel.keys():
                if (self.channel[channel_name]
                        and self.channel[channel_name].is_open):
                    try:
                        self.channel[channel_name].close()
                    except Exception as e:
                        r_logger.error(
                            "RabbitMQ 频道 {} 关闭出错！".format(channel_name))
                        r_logger.error(e)
                self.channel[channel_name] = None
            self.channel = {}
        # 关闭所有连接
        if (self.connection):
            for connection_name in self.connection.keys():
                if (self.connection[connection_name]
                        and self.connection[connection_name].is_open):
                    try:
                        self.connection[connection_name].close()
                    except Exception as e:
                        r_logger.error(
                            "RabbitMQ 连接 {} 关闭出错!".format(connection_name))
                        r_logger.error(e)
                self.connection[connection_name] = None
            self.connection = {}
    
    """
    @description: 发布
    -------
    @param:
    -------
    @return:
    """
    def publish(self, channel_name, queue, body):
        try:
            if (type(body) == str):
                body = json.loads(body)
            # 任务是否有 UUID，没有的话一定要赋予
            if ("uuid" not in body.keys()):
                uuid = str(uuid.uuid1())
                body["uuid"] = uuid
            else:
                uuid = body["uuid"]
            # 发布
            self.channel[channel_name].basic_publish(exchange="", \
                routing_key=queue, body=json.dumps(body), \
                # 消息持久化
                properties=pika.BasicProperties(delivery_mode=2))
            return True, uuid
        except Exception as e:
            r_logger.error(
                "RabbitMQ 发布信息时出错，队列：{queue}，消息:{body}".format(
                    queue=queue, body=str(body)))
            r_logger.error(e)
        return False, None

    """
    @description: 获取（以 UUID 作为主键）
    -------
    @param:
    -------
    @return:
    """
    def get(self, channel_name, queue, uuid):
        # 遍历所有消息
        for method, properties, body \
                in self.channel[channel_name].consume(queue):
            # 如果 UUID 匹配
            if ("uuid" in json.loads(body.decode("UTF-8")).keys()
                    and uuid == json.loads(body.decode("UTF-8"))["uuid"]):
                # 删除这个消息
                result = json.loads(body.decode("UTF-8"))
                self.channel[channel_name].basic_ack(method.delivery_tag)
                return result
            # 如果 UUID 不匹配
            else:
                # 将消息放回队列
                self.channel[channel_name].basic_nack(method.delivery_tag)
        # 没有结果的情况下返回空
        return None
    
    """
    @description: 获取队列长度
    -------
    @param:
    -------
    @return:
    """
    def get_message_count(self, queue, vhost="%2F"):
        try:
            url = "{api_host}/api/queues/{vhost}/{queue}".format(
                api_host=self.api_host, vhost=vhost, queue=queue)
            r = requests.get(url, auth=(self.username, self.password))
            result = json.loads(r.text)
            ready = result['messages_ready']
            unacknowledged = result['messages_unacknowledged']
            total = result['messages']
            return ready, unacknowledged, total
        except Exception as e:
            r_logger.error("RabbitMQ 获取队列长度时出错！")
            r_logger.error(e)
        return None, None, None
    
    """
    @description: 判断队列是否为空
    -------
    @param:
    -------
    @return:
    """
    def is_queue_empty(self, queue):
        # 获取非缓存的准确队列长度
        _ready = None
        for _ in range(0, 10):
            ready, unacknowledged, total = self.get_message_count(
                "reptile_results")
            if (ready >= 100):
                break
            elif(ready == 0):
                break
            else:
                time.sleep(0.5)
                r_logger.info("RabbitMQ 开始等待获取准确的队列长度......")
            if (_ready == None):
                _ready = ready
                continue
            elif(_ready == ready):
                continue
            else:
                break
        # 判断准备队列是否为空
        if (ready == 0):
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

    r_rabbitmq = r_rabbitmq()
    r_rabbitmq.connect("test_connection")
    r_rabbitmq.build_channel("test_connection", "test_channel")

    # 测试是否能正常推送消息和根据 UUID 获取结果
    # try:
    #     for uuid in range(123450, 123460):
    #         body = json.dumps({"uuid": str(uuid)})
    #         r_rabbitmq.publish("test_channel", "test_quere", body)
    #     print("获得结果:{}".format(
    #         r_rabbitmq.get("test_channel", "test_quere", "123456")))
    # except Exception as e:
    #     print("测试出错：{}".format(str(e)))
    # finally:
    #     r_rabbitmq.disconnect()

    # 测试队列长度是否获取正确
    print(r_rabbitmq.get_message_count("test_quere"))