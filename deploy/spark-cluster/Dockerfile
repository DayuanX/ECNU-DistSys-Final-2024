# 构建命令: docker build -t linu/spark:v1 .
FROM docker.io/bitnami/spark:3.5.3
LABEL maintainer="Yangliu <linu@linu.me>"
LABEL description="Docker image with Spark (3.5.3) and some basic commands, based on bitnami/spark:3.5.3"

# 切换账户并更换密码
USER root
RUN echo 'root:1234' | chpasswd

# Debian更换科大镜像源
RUN sed -i "s/archive.ubuntu./mirrors.ustc.edu.cn/g" /etc/apt/sources.list 
RUN sed -i "s/deb.debian.org/mirrors.ustc.edu.cn/g" /etc/apt/sources.list 
RUN sed -i "s/security.debian.org/mirrors.ustc.edu.cn\/debian-security/g" /etc/apt/sources.list
RUN apt-get update && apt-get install -y openssh-server

# 安装Curl命令
RUN apt install -y curl && apt install sudo -y
# IP命令、Ping命令
RUN apt install -y iproute2 && apt install -y iputils-ping

# Python依赖
# Using ustc pipy mirror
RUN pip3 install -i https://mirrors.ustc.edu.cn/pypi/simple/ -U pip 
RUN pip3 config set global.index-url https://mirrors.ustc.edu.cn/pypi/simple/
# Install Python packages
RUN pip3 install  numpy \
                  pandas

# 设置入口脚本
ENTRYPOINT [ "/opt/bitnami/scripts/spark/entrypoint.sh" ]
CMD [ "/opt/bitnami/scripts/spark/run.sh" ]



