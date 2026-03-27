#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取本机 IP 地址工具
"""

import socket
import platform

def get_all_ips():
    """获取所有网络接口的 IP 地址"""
    hostname = socket.gethostname()

    print("=" * 60)
    print("本机网络信息")
    print("=" * 60)
    print(f"主机名: {hostname}")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print()

    try:
        # 获取所有 IP 地址
        ip_list = socket.getaddrinfo(hostname, None)

        ipv4_addresses = []
        for item in ip_list:
            if item[0] == socket.AF_INET:  # IPv4
                ip = item[4][0]
                if ip not in ipv4_addresses and not ip.startswith('127.'):
                    ipv4_addresses.append(ip)

        if ipv4_addresses:
            print("检测到以下 IP 地址:")
            print()
            for idx, ip in enumerate(ipv4_addresses, 1):
                print(f"  [{idx}] {ip}")
            print()
            print("=" * 60)
            print("手机代理配置:")
            print("=" * 60)

            # 推荐使用第一个非本地回环的地址
            recommended_ip = ipv4_addresses[0]
            print(f"服务器/主机名:  {recommended_ip}")
            print(f"端口:          8888")
            print(f"网关:          (保持默认或留空)")
            print()
            print("如果手机有多个网卡，请尝试上面列出的其他 IP 地址")

        else:
            print("[!] 未检测到可用的 IPv4 地址")
            print("[!] 请检查网络连接")

    except Exception as e:
        print(f"[!] 获取 IP 地址失败: {e}")

    print("=" * 60)

def check_network():
    """检查网络连接"""
    print("\n检查网络连接...")
    try:
        # 尝试连接到公共 DNS
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(2)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"[✓] 网络连接正常")
        print(f"[✓] 推荐使用 IP: {local_ip}")
        return local_ip
    except Exception as e:
        print(f"[!] 网络连接异常: {e}")
        return None

if __name__ == '__main__':
    get_all_ips()
    check_network()

    print("\n" + "=" * 60)
    print("提示:")
    print("  1. 确保手机和电脑连接到同一个 WiFi")
    print("  2. 使用上面显示的 IP 地址配置手机代理")
    print("  3. 如果有多个 IP，优先使用 192.168.x.x 的地址")
    print("=" * 60)

    input("\n按回车键退出...")
