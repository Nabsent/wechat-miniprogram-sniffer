#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTPS 抓包代理启动脚本
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
    except FileNotFoundError:
        return False
    except:
        return False

def main():
    print("=" * 70)
    print("微信小程序 HTTPS 抓包工具")
    print("=" * 70)
    print()

    # 检查 mitmproxy
    if not check_mitmproxy():
        print("[!] 未检测到 mitmproxy，请先运行安装脚本:")
        print("    install_https.bat")
        print()
        input("按回车键退出...")
        sys.exit(1)

    local_ip = get_local_ip()

    print(f"[*] 本机 IP: {local_ip}")
    print(f"[*] 代理端口: 8888")
    print()
    print("=" * 70)
    print("📱 手机配置步骤:")
    print("=" * 70)
    print()
    print("1️⃣  配置手机代理")
    print(f"    服务器: {local_ip}")
    print(f"    端口:   8888")
    print()
    print("2️⃣  安装证书（首次使用必须安装！）")
    print("    手机浏览器访问: http://mitm.it")
    print("    选择对应系统下载证书")
    print()
    print("    📱 Android:")
    print("       - 下载证书后安装")
    print("       - 设置 → 安全 → 信任的凭据 → 用户 → 启用 mitmproxy")
    print()
    print("    📱 iOS:")
    print("       - 下载描述文件并安装")
    print("       - 设置 → 通用 → 关于本机 → 证书信任设置")
    print("       - 启用对 mitmproxy 的完全信任")
    print()
    print("3️⃣  使用微信小程序")
    print("    打开小程序，触发文件下载")
    print("    终端会显示捕获的文件信息")
    print()
    print("=" * 70)
    print()

    # 检查脚本文件
    script_file = 'mitm_sniffer.py'
    if not os.path.exists(script_file):
        print(f"[!] 未找到脚本文件: {script_file}")
        input("按回车键退出...")
        sys.exit(1)

    input("配置完成后，按回车键启动代理...")
    print()
    print("[*] 正在启动 HTTPS 解密代理...")
    print("[*] 按 Ctrl+C 停止")
    print()
    print("=" * 70)
    print()

    try:
        # 启动 mitmproxy
        subprocess.run([
            'mitmdump',
            '-s', script_file,
            '--listen-host', '0.0.0.0',
            '--listen-port', '8888',
            '--set', 'block_global=false',
            '--set', 'stream_large_bodies=1m',  # 大文件流式处理
        ])
    except KeyboardInterrupt:
        print("\n[*] 代理已停止")
    except Exception as e:
        print(f"\n[!] 启动失败: {e}")
        print()
        print("可能的原因:")
        print("1. 端口 8888 已被占用")
        print("2. mitmproxy 安装不完整")
        print("3. 权限不足")
        input("\n按回车键退出...")

if __name__ == '__main__':
    main()
