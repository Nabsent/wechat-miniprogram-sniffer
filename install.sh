#!/bin/bash
# 微信小程序抓包工具 - 依赖安装脚本 (Linux/macOS)

echo "========================================"
echo "微信小程序抓包工具 - 依赖安装"
echo "========================================"
echo

# 检查 Python 是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到 Python3，请先安装 Python 3.7+"
    exit 1
fi

echo "[*] 检测到 Python 版本:"
python3 --version
echo

# 检查 pip 是否可用
if ! command -v pip3 &> /dev/null; then
    echo "[错误] pip3 未安装，正在尝试安装..."
    python3 -m ensurepip --default-pip
fi

echo "[*] 正在安装依赖包..."
echo

# 安装 requests
echo "[1/1] 安装 requests..."
pip3 install requests

echo
echo "========================================"
echo "安装完成！"
echo "========================================"
echo
echo "使用方法:"
echo "  1. 启动抓包代理: python3 proxy_sniffer.py"
echo "  2. 下载文件:     python3 file_downloader.py"
echo
echo "详细说明请查看 README.md"
echo

# 添加执行权限
chmod +x proxy_sniffer.py
chmod +x file_downloader.py

echo "[*] 已添加执行权限"
