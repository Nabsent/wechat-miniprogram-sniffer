"""
Windows 微信客户端抓包配置脚本
自动配置系统代理
"""

import subprocess
import os
import sys
from pathlib import Path

def enable_system_proxy():
    """启用系统代理"""
    print("[*] 启用系统代理...")

    # 设置代理
    subprocess.run([
        'reg', 'add',
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings',
        '/v', 'ProxyEnable', '/t', 'REG_DWORD', '/d', '1', '/f'
    ], capture_output=True)

    subprocess.run([
        'reg', 'add',
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings',
        '/v', 'ProxyServer', '/d', '127.0.0.1:8888', '/f'
    ], capture_output=True)

    print("[+] 系统代理已启用: 127.0.0.1:8888")

def disable_system_proxy():
    """禁用系统代理"""
    print("[*] 禁用系统代理...")

    subprocess.run([
        'reg', 'add',
        r'HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings',
        '/v', 'ProxyEnable', '/t', 'REG_DWORD', '/d', '0', '/f'
    ], capture_output=True)

    print("[+] 系统代理已禁用")

def check_certificate():
    """检查证书是否安装"""
    cert_path = Path.home() / '.mitmproxy' / 'mitmproxy-ca-cert.cer'

    if not cert_path.exists():
        print("[!] 证书文件不存在，请先启动代理生成证书")
        return False

    print(f"[*] 证书位置: {cert_path}")
    print("[*] 请手动安装证书到 '受信任的根证书颁发机构'")

    choice = input("\n证书是否已安装? (y/n): ").strip().lower()
    return choice == 'y'

def main():
    print("=" * 60)
    print("Windows 微信客户端抓包配置工具")
    print("=" * 60)
    print()
    print("选项:")
    print("  1. 启用系统代理 (127.0.0.1:8888)")
    print("  2. 禁用系统代理")
    print("  3. 检查证书")
    print("  4. 打开证书管理器")
    print("  0. 退出")
    print()

    choice = input("请选择 (0-4): ").strip()

    if choice == '1':
        if not check_certificate():
            print("\n[!] 请先安装证书后再启用代理")
            return
        enable_system_proxy()
        print("\n[*] 配置完成！现在可以启动微信客户端了")
        print("[*] 使用完毕后记得选择选项 2 禁用代理")

    elif choice == '2':
        disable_system_proxy()
        print("\n[*] 已恢复正常网络")

    elif choice == '3':
        check_certificate()

    elif choice == '4':
        print("[*] 打开证书管理器...")
        subprocess.Popen(['certmgr.msc'])
        print("\n操作步骤:")
        print("1. 展开 '受信任的根证书颁发机构' → '证书'")
        print("2. 查找 'mitmproxy' 证书")
        print("3. 如果没有，右键 → 所有任务 → 导入")
        print(f"4. 选择: {Path.home() / '.mitmproxy' / 'mitmproxy-ca-cert.cer'}")

    elif choice == '0':
        print("退出")
    else:
        print("无效选项")

if __name__ == '__main__':
    # 检查管理员权限
    try:
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("[!] 警告: 建议以管理员身份运行")
            print()
    except:
        pass

    main()
