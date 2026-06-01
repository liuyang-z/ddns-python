# ============================================================
# DDNS-Python 容器镜像
# ============================================================
FROM python:3.11-alpine

LABEL maintainer="ddns-python"
LABEL description="DNSPod DDNS auto-update container"

# 设置工作目录
WORKDIR /app

# 升级 pip 并配置清华镜像源（加速国内下载）
RUN pip install --no-cache-dir --upgrade pip && \
    pip config set global.index-url https://mirrors4.tuna.tsinghua.edu.cn/pypi/web/simple

# 安装 Python 依赖
RUN pip install --no-cache-dir requests

# 复制应用代码与入口脚本
COPY ddns.py       /app/ddns.py
COPY entrypoint.sh /app/entrypoint.sh

# 复制默认配置文件（运行时可通过 volume 覆盖）
COPY config.ini    /app/config.ini

# 创建日志目录
RUN mkdir -p /app/logs

# 赋予入口脚本执行权限
RUN chmod +x /app/entrypoint.sh

# 容器启动后自动运行 DDNS 检测循环
ENTRYPOINT ["/app/entrypoint.sh"]
