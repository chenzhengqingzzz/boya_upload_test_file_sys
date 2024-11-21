# 使用python:3.11-slim作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 复制当前目录下的所有文件到容器的/app目录下
COPY . /app

# COPY ./perl/* /usr/local/share/perl/
RUN export DOCKER_BUILDKIT=1

# 更新软件包列表
RUN apt-get update

# 安装sudo、vim、samba挂载工具、tk
RUN apt-get install -y sudo vim cifs-utils tk python3-tk gcc python3-dev


# 安装perl生成表格模块
RUN apt-get install -y cpanminus && cpanm Excel::Writer::XLSX

# 安装Python依赖
RUN pip install  --no-cache-dir -r requirements.txt

# 创建win中的Z路径
RUN mkdir /Z

# 创建凭证文件夹 info为txt文件
RUN mkdir credentials


# 设置时区为北京时间
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo "Asia/Shanghai" > /etc/timezone

# 设置环境变量以使用GUI应用
ENV DISPLAY=:0 \
    LANG="C.UTF-8"

# 暴露5000端口
EXPOSE 5000

# 设置容器启动时运行的命令
CMD ["python", "app.py"]

# cd /boya_upload_test_file_sys
# docker build --no-cache -t boya_upload_test_file_sys .
# 根据存放凭证的文件夹修改路径
# docker run --privileged -d --name boya_upload_test_file_sys -p 80:80 -v /credentials:/credentials --restart always 192.168.2.143:5000/boya_upload_test_file_sys
# sudo mount -t cifs //192.168.2.108/fileserver /Z -o credentials=/credentials/info.txt,vers=3.0,sec=ntlmssp,iocharset=utf8

# docker tag boya_upload_test_file_sys 192.168.2.143:5000/boya_upload_test_file_sys
# docker push 192.168.2.143:5000/boya_upload_test_file_sys

# 查询仓库镜像 http://192.168.2.143:5000/v2/_catalog

# 5000 registry
# 9000 管理docker
# 81 nginx反代管理