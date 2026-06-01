#!/bin/sh
# DDNS 容器入口脚本 — 周期性执行 ddns.py
# 可通过环境变量 INTERVAL 设置检测间隔（秒），默认 300 秒（5分钟）

INTERVAL=${INTERVAL:-300}

echo "DDNS container started. Checking every ${INTERVAL}s."

while true; do
    python /app/ddns.py
    echo "Next check in ${INTERVAL}s..."
    sleep "$INTERVAL"
done
