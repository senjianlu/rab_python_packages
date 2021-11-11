# rab_python_packages

## 项目介绍  
简单可用的 Python3 模块包。  
在大量简单方法整合起来的模块加持下，即使是初学者也能迅速开展对数据的爬取、整理和存储等工作。  

## 环境
环境需求：  
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
| PyYAML | 6.0 |  
| redis | 3.5.3 |  
| requests[socks] | 2.10.0 |  
| rsa | 4.7.2 |  
| selenium | 3.141.0 |  
| singleton_decorator | 1.0.0 |  
| six | 1.16.0 |  
| urllib3 | 1.25.11 |  
| websocket | 0.2.1 |  

| 浏览器 | 版本 |  
| ----- | ----- |  
| Google Chrome | 92.0.4515.107 |  

| 浏览器驱动 | 版本 |  
| ----- | ----- |  
| ChromeDriver | 92.0.4515.107 |  

**你有以下两种方式来配置环境：**
1. 使用命令配置本机环境：
```bash
cd rab_python_packages
# 配置运行环境
python3 rab_env.py
# 针对 rab_chrome 配置 Selenium 驱动 Chrome 所需的环境
python3 rab_env.py rab_chrome
```
2. 如果你习惯在 Docker 镜像内进行开发作业，那么也可以从 Docker Hub 上拉取已经配置好环境的  [rabbir/rab_python_packages](https://hub.docker.com/r/rabbir/rab_python_packages) 镜像并连接：
```bash
docker pull rabbir/rab_python_packages:latest
# 后台运行容器
docker run -dit rabbir/rab_python_packages:latest
# 连接镜像为 rabbir/rab_python_packages:latest 的第一个容器
docker attach `docker ps -aq -l --filter ancestor=rabbir/rab_python_packages:latest`
```
> 你也可以选择在本地构建 Docker 镜像，使用本项目中的 Dockerfile 以保证在构建过程中环境会一并被配置好：
> ```bash
> cd rab_python_packages
> # rabbir/rab_python_packages:latest 替换为你想要的标签
> docker build -t rabbir/rab_python_packages:latest .
> ```

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
Dockerfile 构建镜像：
```yaml
# 基础镜像系统版本为 rabbir/rab_python_packages:latest
FROM rabbir/rab_python_packages:latest
...
...
```

## 整体结构
![rab_python_packages](https://raw.githubusercontent.com/senjianlu/imgs/master/20211111083715.png)  

## 特别鸣谢
- 感谢 [JetBrains](https://www.jetbrains.com/) 为本项目提供的 [PyCharm](https://www.jetbrains.com/pycharm/) 开源许可证
- 感谢 [DigitalOcean](https://www.digitalocean.com/) 为本项目提供测试用服务器
- 感谢 [Amazon Web Services](https://aws.amazon.com/) 为本项目提供免费的静态资源存储服务