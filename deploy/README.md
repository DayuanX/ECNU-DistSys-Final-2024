# 部署

## 虚拟机配置
考虑使用 VMWare Workstation 配置 Ubuntu 24.04 LTS 作为实验平台。

不同物理机上的虚拟机需要能够互相访问，因此需要调整 VMWare 设置，把虚拟机的网络改为桥接模式，使虚拟机暴露在宿舍的局域网中。

下载地址: [清华源](https://mirrors.tuna.tsinghua.edu.cn/ubuntu-releases/24.04.1/)

只需要安装 live server 即可。假定用户名是 `ubuntu` 。hostname 按顺序为 `ubuntu-1`, 
`ubuntu-2`, `ubuntu-3`, `ubuntu-4`。

```bash
ip addr
```
可以查看虚拟机的 ip。后续物理机访问虚拟机也需要使用这个 ip。

之后默认 `ubuntu-1` 为主节点, hdfs namenode 和 spark-master 都会在其上部署；
其余节点均为 hdfs datanode & spark slave。

hostname可以这样修改:
```bash
sudo hostnamectl set-hostname ubuntu-1
```

在**所有**服务器上都创建几个文件夹用于存放后续的 hdfs 文件:
```bash
mkdir -p /home/ubuntu/bigdata/volumes-nn
mkdir -p /home/ubuntu/bigdata/volumes-dn01
mkdir -p /home/ubuntu/bigdata/volumes-dn02
mkdir -p /home/ubuntu/bigdata/volumes-dn03
mkdir -p /home/ubuntu/bigdata/volumes-dn04
```
这几个文件夹用于 hdfs 存放持久化的数据，如果不创建，后续的 hdfs 部署会失败。

## 安装 Docker

[官方文档](https://docs.docker.com/engine/install/ubuntu/)

可能需要挂代理。
```bash
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
验证:
```bash
sudo docker run hello-world
```

## 配置 Docker Swarm
在 `ubuntu-1` 上执行:
```bash
sudo docker swarm init
```

得到类似下面的结果:
```
Swarm initialized: current node (8pbeemanze4hic086lg9vatgq) is now a manager.
 
To add a worker to this swarm, run the following command:
 
    docker swarm join --token SWMTKN-1-5u7vluy344umgyreimctpoeuvabz4yp5dz4xney55cypvsv15n-9r5e5at6z1ri63b2azy0ob81p 192.168.137.6:2377
 
To add a manager to this swarm, run 'docker swarm join-token manager' and follow the instructions.
```

在其余节点上各自执行上面给的 `sudo docker swarm join .......` 命令，加入集群。


## 部署集群

1. 创建网络
```bash
sudo docker network create --driver overlay hdfs-network
```

2. 配置 HDFS。进入 `hdfs-cluster` 目录：
```bash
sudo docker stack deploy -c docker-compose.yml hdfs-cluster
```

3. 配置 Spark。进入 `spark-cluster` 目录：
```bash
sudo docker stack deploy -c docker-compose.yml spark-cluster
```

4. 验证效果: 在配置文件中，hdfs暴露了9870端口，spark暴露了8080端口，用浏览器访问 `ubuntu-1` 的对应端口可以打开管理界面，应该都能看到4个节点在线。