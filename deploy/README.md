# 部署文档

## 服务器配置

本服务器由Ucloud上海提供的ECS实例构建，基于KVM虚拟化技术。操作系统采用Debian 11。系统的基本配置如下：

CPU：32核，内存：256GB，存储：256GB SSD，以下是服务器的具体配置和硬件性能详情：

```bash
---------------------基础信息查询--感谢所有开源项目---------------------
 CPU 型号          : Intel Xeon Processor (Cascadelake)
 CPU 核心数        : 32
 CPU 频率          : 2992.968 MHz
 CPU 缓存          : L1: 1.00 MB / L2: 64.00 MB / L3: 16.00 MB
 AES-NI指令集      : ✔ Enabled
 VM-x/AMD-V支持    : ❌ Disabled
 内存              : 13.33 GiB / 251.70 GiB
 Swap              : [ no swap partition or swap file detected ]
 硬盘空间          : 8.50 GiB / 251.82 GiB
 系统              : Debian GNU/Linux 11 (bullseye) (x86_64)
 架构              : x86_64 (64 Bit)
 内核              : 5.10.0-23-amd64
 TCP加速方式       : cubic
 虚拟化架构        : KVM
 IPV4 ASN          : AS4812 China Telecom (Group)
 IPV4 位置         : Shanghai / Shanghai / CN
----------------------CPU测试--通过sysbench测试-------------------------
 -> CPU 测试中 (Fast Mode, 1-Pass @ 5sec)
 1 线程测试(单核)得分:          1223 Scores
 32 线程测试(多核)得分:                 34994 Scores
---------------------内存测试--感谢lemonbench开源-----------------------
 -> 内存测试 Test (Fast Mode, 1-Pass @ 5sec)
 单线程读测试:          23312.69 MB/s
 单线程写测试:          16553.32 MB/s
------------------磁盘dd读写测试--感谢lemonbench开源--------------------
 -> 磁盘IO(4K Block/1M Block, Direct Mode)
 测试操作               写速度                                  读速度
 100MB-4K Block         60.7 MB/s (14.81 IOPS, 1.73s))          26.7 MB/s (6516 IOPS, 3.93s)
 1GB-1M Block           296 MB/s (282 IOPS, 3.54s)              296 MB/s (282 IOPS, 3.54s)
---------------------磁盘fio读写测试--感谢yabs开源----------------------
Block Size | 4k            (IOPS) | 64k           (IOPS)
  ------   | ---            ----  | ----           ---- 
Read       | 29.59 MB/s    (7.3k) | 130.23 MB/s   (2.0k)
Write      | 29.60 MB/s    (7.4k) | 130.92 MB/s   (2.0k)
Total      | 59.20 MB/s   (14.8k) | 261.16 MB/s   (4.0k)
           |                      |                     
Block Size | 512k          (IOPS) | 1m            (IOPS)
  ------   | ---            ----  | ----           ---- 
Read       | 125.83 MB/s    (245) | 125.50 MB/s    (122)
Write      | 132.51 MB/s    (258) | 133.86 MB/s    (130)
Total      | 258.34 MB/s    (503) | 259.37 MB/s    (252)
```

## 集群配置

本项目采用基于 Docker Compose 部署的 Spark 集群和 HDFS 集群。为了简化 Spark 镜像的使用，我们对其进行了二次封装，包括更换软件源、安装必要的软件包以及用户配置等。因此，需先在本地构建 Spark 镜像。

### 镜像构建

切换至 `spark-cluster` 目录，通过该目录下的 `Dockerfile` 构建 Spark 镜像。构建命令如下：

```bash
docker build -t linu/spark:v1 .
```

### 网络创建

因为Spark需要通过HDFS访问文件，因此先通过`docker network create`命令创建`mixed_cluster brige`，使两类集群可以互访，命令如下：

```bash
docker network create mixed_cluster
```

### 创建集群

通过`docker-compose -d up`，启动两集群即可。

对于Spark，需要注意的是，基于实验，要为每个worker配置好需要的内存，以及可见的CPU, 例如`cpuset: "28-31" `。

### 访问和使用集群

两个集群创建好后，容器内部通过其hostname即可访问，例如`spark://master-spark:7077`。

我们将宿主机的`/root/workspace`与Spark-master和Hadoop-namenode容器内的`/root`目录绑定，可直接在此处操作文件，而无需使用`docker cp`命令同步。Spark提交任务、向HDFS上传文件时，依然需要通过`docker exec -it 容器名 /bin/bash`的方式，在容器中提交

## 容器监控配置

为了对集群的性能进行评估，我们通过cAdvisor、Prometheus和Grafana对集群性能进行监控，下面是部署过程。

### cAdvisor

cAdvisor(Container Advisor) 是 Google 开源的一个容器监控工具，可用于对容器资源的使用情况和性能进行监控。用于收集、聚合、处理和导出正在运行容器的有关信息。具体来说，该组件对每个容器都会记录其资源隔离参数、历史资源使用情况、完整历史资源使用情况的直方图和网络统计信息。cAdvisor 本身就对 Docker 容器支持，并且还对其它类型的容器尽可能的提供支持，力求兼容与适配所有类型的容器。

#### 启动命令

```bash
VERSION=v0.49.2 # use the latest release version from https://github.com/google/cadvisor/releases
sudo docker run \
  --volume=/:/rootfs:ro \
  --volume=/var/run:/var/run:ro \
  --volume=/sys:/sys:ro \
  --volume=/var/lib/docker/:/var/lib/docker:ro \
  --volume=/dev/disk/:/dev/disk:ro \
  --publish=8080:8080 \
  --detach=true \
  --name=cadvisor \
  --privileged \
  --device=/dev/kmsg \
  gcr.io/cadvisor/cadvisor:$VERSION
```

#### 参考

[google/cadvisor: Analyzes resource usage and performance characteristics of running containers.](https://github.com/google/cadvisor#quick-start-running-cadvisor-in-a-docker-container)

### Prometheus

Prometheus 是由前 Google 工程师从 2012 年开始在 Soundcloud 以开源软件的形式进行研发的系统监控和告警工具包，自此以后，许多公司和组织都采用了 Prometheus 作为监控告警工具。

#### 数据目录创建

```bash
mkdir -p /disk/docker-monitor/prometheus/data
chmod 777 /disk/docker-monitor/prometheus/data
```

创建配置文件，用于收集cAdvisor的日志

```bash
/disk/docker-monitor/prometheus/conf/prometheus.yml
```

```bash
global:
  scrape_interval: 15s
  evaluation_interval: 15s 

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          # - alertmanager:9093

rule_files:
  - rule/record/*.yml

scrape_configs:
  - job_name: "prometheus"
    static_configs:
      - targets: ["localhost:9090"]
  - job_name: "cadvisor"
    static_configs:
      - targets: ["172.17.0.1:8081"]
```

#### 启动命令

```bash
docker run -d -p 9090:9090 --name prometheus \
    -v /disk/docker-monitor/prometheus/conf:/opt/bitnami/prometheus/conf \
    -v /disk/docker-monitor/prometheus/data:/opt/bitnami/prometheus/data \
    bitnami/prometheus:2.42.0 \
    --web.enable-lifecycle --web.enable-admin-api\
    --config.file=/opt/bitnami/prometheus/conf/prometheus.yml\
    --storage.tsdb.path=/opt/bitnami/prometheus/data
```

### Grafana

Grafana是一个跨平台、开源的数据可视化网络应用程序平台。用户配置连接的数据源之后，Grafana可以在网络浏览器里显示数据图表和警告。

#### 启动命令

```bash
docker run -d --name=grafana -p 3000:3000 -v grafana:/var/lib/grafana grafana/grafana
```

