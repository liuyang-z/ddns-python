# ============================================================
# DDNS-Python Makefile
# ============================================================
IMAGE_NAME   ?= ddns-python

# 从 VERSION 文件读取版本号，读取失败则回退为 latest
VERSION      := $(shell cat VERSION 2>/dev/null)
ifeq ($(VERSION),)
VERSION      := latest
endif

IMAGE_TAG    ?= $(VERSION)
EXPORT_FILE  ?= $(IMAGE_NAME)-$(VERSION).tar

.DEFAULT_GOAL := help

## 查看帮助
.PHONY: help
help:
	@echo "可用命令:"
	@echo "  make build     — 构建 Docker 镜像 (tag: $(VERSION))"
	@echo "  make run       — 以后台方式运行容器"
	@echo "  make compose-up   — 使用 docker compose 启动"
	@echo "  make compose-down — 使用 docker compose 停止"
	@echo "  make export    — 导出镜像为 $(EXPORT_FILE)"
	@echo "  make clean     — 删除镜像与导出文件"
	@echo ""
	@echo "当前版本: $(VERSION)"
	@echo ""
	@echo "可配置变量:"
	@echo "  IMAGE_NAME    镜像名称（默认: $(IMAGE_NAME)）"
	@echo "  IMAGE_TAG     镜像标签（默认: $(IMAGE_TAG)）"
	@echo "  EXPORT_FILE   导出文件名（默认: $(EXPORT_FILE)）"

## 构建 Docker 镜像
.PHONY: build
build:
	docker build -f docker/Dockerfile -t $(IMAGE_NAME):$(IMAGE_TAG) .

## 运行容器（挂载本地 config.ini，按需修改）
.PHONY: run
run:
	docker run -ti --rm \
		--name ddns-python \
		-v "$(CURDIR)/config/config.ini:/app/config.ini:ro" \
		-e INTERVAL=10 \
		$(IMAGE_NAME):$(IMAGE_TAG)

## 使用 docker compose 启动
.PHONY: compose-up
compose-up:
	docker compose -f docker/docker-compose.yml up -d

## 使用 docker compose 停止并清理
.PHONY: compose-down
compose-down:
	docker compose -f docker/docker-compose.yml down

## 导出镜像为 tar 文件
.PHONY: export
export:
	docker save -o $(EXPORT_FILE) $(IMAGE_NAME):$(IMAGE_TAG)
	@echo "镜像已导出为: $(EXPORT_FILE)"

## 清理本地镜像与导出文件
.PHONY: clean
clean:
	-docker rmi $(IMAGE_NAME):$(IMAGE_TAG)
	-rm -f $(EXPORT_FILE)
