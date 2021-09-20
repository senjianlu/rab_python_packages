# rab_python_packages

## 项目介绍  
简单可用的 Python3 模块包。  
在大量简单方法整合起来的模块加持下，即使是初学者也能迅速开展对数据的爬取、整理和存储等工作。  

## 环境
| 系统 | 版本 |  
| -----| ---- |  
| Linux | CentOS7 |  

| 数据库 | 版本 |  
| -----| ---- |  
| PostgreSQL | 12 |  

| 语言 | 版本 |
| -----| ---- |  
| Python | 3.8.2 |  

| 模块 | 版本 |
| -----| ---- |  
| cfscrape | 2.1.1 |  
| configparser | 5.0.2 |  
| charset-normalizer | 2.0.3 |  
| docker | 5.0.0 |  
| minio | 7.1.0 |  
| pika | 1.2.0 |  
| psycopg2 | 2.8.6 |  
| rsa | 4.7.2 |  
| requests[socks] | 2.10.0 |  
| selenium | 3.141.0 |  
| singleton_decorator | 1.0.0 |  
| six | 1.16.0 |  
| urllib3 | 1.25.11 |  
| websocket | 0.2.1 |  

## 使用方法 
仅使用当前版本（维持爬虫的稳定可用）:
```bash
git clone https://github.com/senjianlu/rab_python_packages.git
```
依赖此仓库（获取更多的封装方法）:
```bash
git submodule add https://github.com/senjianlu/rab_python_packages.git
```
*注：既存方法的方法名和参数不进行修改，实在需要添加参数会赋予初始值，任何改动以不影响现在的代码作为第一前提。*  

## 整体结构
![rab_python_packages](https://raw.githubusercontent.com/senjianlu/imgs/master/20210920190810.png)

## 特别鸣谢
- 感谢 [JetBrains](https://www.jetbrains.com/) 为本项目提供的 [PyCharm](https://www.jetbrains.com/pycharm/) 开源许可证
- 感谢 [DigitalOcean](https://www.digitalocean.com/) 为本项目提供测试用服务器
- 感谢 [Amazon Web Services](https://aws.amazon.com/) 为本项目提供免费的静态资源存储服务