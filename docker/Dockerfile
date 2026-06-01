# ============================================================
# DDNS-Python 容器镜像
# ============================================================

FROM python:3.11-alpine

LABEL maintainer="ddns-python"
LABEL description="DNSPod DDNS auto-update container"

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip && \
    pip config set global.index-url https://mirrors4.tuna.tsinghua.edu.cn/pypi/web/simple

RUN pip install --no-cache-dir requests

COPY src/ddns.py          /app/ddns.py
COPY docker/entrypoint.sh /app/entrypoint.sh
COPY config/config.ini    /app/config.ini

# 创建日志目录
RUN mkdir -p /app/logs
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
