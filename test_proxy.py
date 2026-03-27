#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试工具 - 检查代理是否正常工作
"""

import socket

def test_proxy_connection(proxy_host='127.0.0.1', proxy_port=8888):
    """测试代理服务器是否可以连接"""
    print(f"正在测试连接到代理服务器: {proxy_host}:{proxy_port}")

    try:
        # 尝试连接到代理服务器
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.connect((proxy_host, proxy_port))

        # 发送一个简单的HTTP请求
        request = b"GET http://www.baidu.com/ HTTP/1.1\r\nHost: www.baidu.com\r\n\r\n"
        sock.send(request)

        # 接收响应
        response = sock.recv(1024)
        sock.close()

        if b"HTTP" in response:
            print("✅ 代理服务器工作正常！")
            print(f"收到响应: {response[:100].decode('utf-8', errors='ignore')}")
            return True
        else:
            print("⚠️  代理服务器有响应，但不是标准HTTP响应")
            return False

    except ConnectionRefusedError:
        print("❌ 连接被拒绝：代理服务器可能没有运行")
        return False
    except socket.timeout:
        print("❌ 连接超时：代理服务器没有响应")
        return False
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def test_from_phone_perspective(proxy_host):
    """从手机角度测试（检查防火墙）"""
    print(f"\n正在检测防火墙规则...")
    print(f"尝试从外部连接到: {proxy_host}:8888")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        sock.bind(('', 0))  # 使用随机端口
        local_port = sock.getsockname()[1]
        sock.close()

        print(f"✅ 可以使用网络端口: {local_port}")
        print(f"💡 提示: 让手机尝试访问 http://{proxy_host}:8888")

    except Exception as e:
        print(f"❌ 网络配置可能有问题: {e}")

if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("代理服务器连接测试")
    print("=" * 60)
    print()

    # 获取本机IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip = s.getsockname()[0]
        s.close()
        print(f"本机IP: {local_ip}")
    except:
        local_ip = '127.0.0.1'
        print(f"本机IP: 无法获取，使用 {local_ip}")

    print()

    # 测试本地连接
    print("1. 测试本地连接...")
    test_proxy_connection('127.0.0.1', 8888)

    print()

    # 测试外部连接
    if local_ip != '127.0.0.1':
        print("2. 测试外部IP连接（模拟手机连接）...")
        test_proxy_connection(local_ip, 8888)
        test_from_phone_perspective(local_ip)

    print()
    print("=" * 60)
    print("测试完成")
    print()
    print("如果本地连接成功但外部连接失败，请检查：")
    print("1. 防火墙设置（允许端口 8888）")
    print("2. 手机和电脑是否在同一WiFi")
    print("3. 路由器是否有AP隔离")
    print("=" * 60)
