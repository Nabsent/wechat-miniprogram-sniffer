#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全自动爬虫启动脚本
"""

import subprocess
import socket
import sys
import os

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return '127.0.0.1'

def check_mitmproxy():
    try:
        result = subprocess.run(['mitmdump', '--version'],
                              capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

def main():
    print("=" * 70)
    print("🤖 全自动文件爬虫 - 真正的自动化")
    print("=" * 70)
    print()

    if not check_mitmproxy():
        print("[!] 未检测到 mitmproxy，请先运行: install_https.bat")
        input("按回车键退出...")
        sys.exit(1)

    local_ip = get_local_ip()

    print(f"[*] 本机 IP: {local_ip}")
    print(f"[*] 代理端口: 8888")
    print()
    print("=" * 70)
    print("📱 一次性设置:")
    print("=" * 70)
    print()
    print(f"1. 手机配置代理: {local_ip}:8888")
    print(f"2. 安装证书: http://mitm.it")
    print()
    print("=" * 70)
    print("🚀 使用方法:")
    print("=" * 70)
    print()
    print("您只需要：")
    print("  1. 在手机上打开微信小程序")
    print("  2. 点进文件列表页面")
    print()
    print("系统会自动：")
    print("  ✅ 学习API结构")
    print("  ✅ 识别分页模式")
    print("  ✅ 自动翻页获取所有文件")
    print("  ✅ 批量下载到本地")
    print()
    print("示例流程：")
    print("  您: 打开小程序 → 点击'文件管理'")
    print("  系统: 🎓 学习到API模式")
    print("  系统: 📋 发现 50 个文件，共 5 页")
    print("  系统: 🚀 自动爬取所有页面...")
    print("  系统: 💾 批量下载所有文件...")
    print("  系统: ✅ 完成！")
    print()
    print("💡 提示:")
    print("  - 您只需操作一次，系统会自动完成剩余工作")
    print("  - 支持自动识别分页（page, pageNum, pageSize等）")
    print("  - 自动保持会话（cookies, token等）")
    print("  - 所有文件保存到: auto_downloads/")
    print()
    print("=" * 70)
    print()

    input("配置完成后，按回车启动全自动爬虫...")
    print()
    print("[*] 正在启动...")
    print("[*] 按 Ctrl+C 停止")
    print()
    print("=" * 70)
    print()

    try:
        subprocess.run([
            'mitmdump',
            '-s', 'auto_crawler.py',
            '--listen-host', '0.0.0.0',
            '--listen-port', '8888',
            '--set', 'block_global=false',
            '--set', 'stream_large_bodies=1m',
        ])
    except KeyboardInterrupt:
        print("\n[*] 爬虫已停止")
        print("\n查看结果:")
        print(f"  下载文件: {os.path.abspath('auto_downloads')}")
        print(f"  日志文件: crawler_log.json")
    except Exception as e:
        print(f"\n[!] 启动失败: {e}")
        input("\n按回车键退出...")

if __name__ == '__main__':
    main()
