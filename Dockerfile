# 基础镜像系统版本为 CentOS:7
FROM centos:7

# 维护者信息
LABEL maintainer="Rabbir admin@cs.cheap"

# Docker 内用户切换到 root
USER root

# 安装 Git 和 Python3
WORKDIR /root
RUN yum -y install git
RUN curl -s https://gitee.com/senjianlu/one-click-scripts/raw/main/CentOS7%20%E4%B8%8B%E4%B8%80%E9%94%AE%E5%AE%89%E8%A3%85%20Python3%20%E7%8E%AF%E5%A2%83/install.sh | bash

# 在 /root/GitHub 目录下克隆 rab_python_packages 项目
RUN mkdir /root/GitHub
RUN mkdir /root/GitHub/rab_python_packages
WORKDIR /root/GitHub/rab_python_packages
# 将宿主机当前目录下的所有文件拷贝至镜像内的 /root/GitHub/rab_python_packages 文件夹中
COPY . .

# 配置环境
RUN python3 rab_env.py
RUN python3 rab_env.py rab_chrome

# 删除无用文件
RUN rm -r chromedriver_linux64.zip
RUN rm -r google-chrome-stable_current_x86_64.rpm

# 安装 GOST 并将启动和停止脚本下载至 /usr/local/bin 路径下
WORKDIR /root
RUN curl -s https://gitee.com/senjianlu/one-click-scripts/raw/main/CentOS7%20%E4%B8%8B%E4%B8%80%E9%94%AE%E5%AE%89%E8%A3%85%20GOST%20%E5%B9%B6%E5%90%AF%E5%8A%A8%20HTTP%20%E5%92%8C%20SOCKS5%20%E4%BB%A3%E7%90%86%E6%9C%8D%E5%8A%A1/install.sh | bash
RUN wget https://gitee.com/senjianlu/one-click-scripts/raw/main/CentOS7%20%E4%B8%8B%E4%B8%80%E9%94%AE%E5%AE%89%E8%A3%85%20GOST%20%E5%B9%B6%E5%90%AF%E5%8A%A8%20HTTP%20%E5%92%8C%20SOCKS5%20%E4%BB%A3%E7%90%86%E6%9C%8D%E5%8A%A1/%E5%90%AF%E5%8A%A8%E6%9C%8D%E5%8A%A1%EF%BC%88%E5%85%B6%E4%BB%96%EF%BC%89/start.sh -P /usr/local/bin/
RUN wget https://gitee.com/senjianlu/one-click-scripts/raw/main/CentOS7%20%E4%B8%8B%E4%B8%80%E9%94%AE%E5%AE%89%E8%A3%85%20GOST%20%E5%B9%B6%E5%90%AF%E5%8A%A8%20HTTP%20%E5%92%8C%20SOCKS5%20%E4%BB%A3%E7%90%86%E6%9C%8D%E5%8A%A1/%E5%90%AF%E5%8A%A8%E6%9C%8D%E5%8A%A1/stop.sh -P /usr/local/bin/