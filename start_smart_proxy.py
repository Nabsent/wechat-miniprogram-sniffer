#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能抓包启动脚本
自动分析、下载文件
"""

import subprocess
import socket
import sys
import os

def get_local_ip():
    """获取本机IP地址"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def check_mitmproxy():
    """检查 mitmproxy 是否已安装"""
    try:
        result = subprocess.run(['mitmdump', '--version'],
                              capture_output=True,
                              text=True,
                              timeout=5)
        return result.returncode == 0
    except:
        return False

def main():
    print("=" * 70)
    print("智能文件抓取器 - 自动分析和下载")
    print("=" * 70)
    print()

    # 检查 mitmproxy
    if not check_mitmproxy():
        print("[!] 未检测到 mitmproxy，请先运行:")
        print("    install_https.bat")
        print()
        input("按回车键退出...")
        sys.exit(1)

    local_ip = get_local_ip()

    print(f"[*] 本机 IP: {local_ip}")
    print(f"[*] 代理端口: 8888")
    print()
    print("=" * 70)
    print("📱 手机配置:")
    print("=" * 70)
    print()
    print(f"1. 配置手机代理: {local_ip}:8888")
    print(f"2. 安装证书: http://mitm.it")
    print()
    print("=" * 70)
    print("🤖 智能功能:")
    print("=" * 70)
    print()
    print("✅ 自动识别文件下载")
    print("✅ 自动识别文件列表 API")
    print("✅ 自动解析并下载所有文件")
    print("✅ 保持会话（cookies/token）")
    print()
    print("📂 下载位置: ./auto_downloads/")
    print("📝 日志文件: ./captured_data.json")
    print()
    print("=" * 70)
    print("使用方法:")
    print("=" * 70)
    print()
    print("1. 在手机上打开微信小程序")
    print("2. 浏览文件列表页面（系统会自动识别API）")
    print("3. 点击单个文件（系统会自动下载）")
    print("4. 如果识别到列表API，会自动下载所有文件")
    print()
    print("提示:")
    print("  - 如果看到 '发现疑似文件列表API' → 自动解析中")
    print("  - 如果看到 '开始自动下载' → 批量下载中")
    print("  - 所有文件自动保存到 auto_downloads 目录")
    print()
    print("=" * 70)
    print()

    input("配置完成后，按回车键启动代理...")
    print()
    print("[*] 正在启动智能抓包代理...")
    print("[*] 按 Ctrl+C 停止")
    print()
    print("=" * 70)
    print()

    try:
        # 启动 mitmproxy with smart sniffer
        subprocess.run([
            'mitmdump',
            '-s', 'smart_sniffer.py',
            '--listen-host', '0.0.0.0',
            '--listen-port', '8888',
            '--set', 'block_global=false',
            '--set', 'stream_large_bodies=1m',
        ])
    except KeyboardInterrupt:
        print("\n[*] 代理已停止")
        print("\n查看下载的文件:")
        print(f"  cd {os.path.abspath('auto_downloads')}")
    except Exception as e:
        print(f"\n[!] 启动失败: {e}")
        input("\n按回车键退出...")

if __name__ == '__main__':
    main()
