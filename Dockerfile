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
WORKDIR /root/GitHub
RUN git clone https://github.com/senjianlu/rab_python_packages.git

# 配置环境
WORKDIR /root/GitHub/rab_python_packages
RUN python3 rab_env.py
RUN python3 rab_env.py rab_chrome

# 删除无用文件
RUN rm -r chromedriver_linux64.zip
RUN rm -r google-chrome-stable_current_x86_64.rpm