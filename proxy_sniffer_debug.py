#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信小程序抓包代理工具 - 调试增强版
增加详细日志输出，帮助排查问题
"""

import socket
import threading
import re
import json
from datetime import datetime
from urllib.parse import urlparse
import ssl
import select

class ProxySnifferDebug:
    def __init__(self, host='0.0.0.0', port=8888, log_file='captured_urls.json'):
        self.host = host
        self.port = port
        self.log_file = log_file
        self.captured_urls = []
        self.running = False
        self.request_count = 0

        # 需要关注的文件类型
        self.file_extensions = [
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.7z', '.png', '.jpg', '.jpeg', '.gif',
            '.mp4', '.mp3', '.avi', '.mov', '.txt', '.json', '.xml'
        ]

        # 需要关注的 Content-Type
        self.file_content_types = [
            'application/pdf', 'application/msword',
            'application/vnd.ms-excel', 'application/vnd.ms-powerpoint',
            'application/zip', 'application/x-rar', 'application/octet-stream',
            'image/', 'video/', 'audio/'
        ]

    def start(self):
        """启动代理服务器"""
        self.running = True
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(100)

        print(f"[*] 代理服务器启动成功 (调试模式)")
        print(f"[*] 监听地址: {self.host}:{self.port}")
        print(f"[*] 日志文件: {self.log_file}")
        print(f"[*] 请配置手机代理为: {self.get_local_ip()}:{self.port}")
        print(f"[*] 按 Ctrl+C 停止服务")
        print(f"[*] 调试模式：会显示所有经过的请求\n")
        print("=" * 70)

        try:
            while self.running:
                client_socket, client_address = server_socket.accept()
                print(f"[DEBUG] 新连接: {client_address[0]}:{client_address[1]}")
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, client_address)
                )
                client_thread.daemon = True
                client_thread.start()
        except KeyboardInterrupt:
            print("\n[*] 正在停止服务器...")
            self.running = False
            self.save_logs()
        finally:
            server_socket.close()

    def get_local_ip(self):
        """获取本机IP地址"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'

    def handle_client(self, client_socket, client_address):
        """处理客户端请求"""
        try:
            request = client_socket.recv(8192)
            if not request:
                print(f"[DEBUG] 空请求: {client_address}")
                return

            request_str = request.decode('utf-8', errors='ignore')

            # 解析请求
            lines = request_str.split('\n')
            if not lines:
                return

            first_line = lines[0].strip()
            if not first_line:
                return

            parts = first_line.split()
            if len(parts) < 2:
                return

            method = parts[0]
            url = parts[1]

            self.request_count += 1

            # 处理 CONNECT 方法（HTTPS）
            if method == 'CONNECT':
                print(f"[{self.request_count}] HTTPS: {url}")
                self.handle_https_connect(client_socket, request_str, url)
            else:
                print(f"[{self.request_count}] HTTP:  {method} {url}")
                self.handle_http_request(client_socket, request, request_str)

        except Exception as e:
            print(f"[!] 处理请求出错: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass

    def handle_https_connect(self, client_socket, request_str, url):
        """处理 HTTPS CONNECT 请求"""
        try:
            # 记录 HTTPS 请求（虽然无法看到内容，但至少知道访问了哪个域名）
            host, port = url.split(':') if ':' in url else (url, 443)
            port = int(port)

            # 如果是微信或小程序相关域名，特别标注
            wechat_domains = ['weixin', 'wechat', 'qq.com', 'servicewechat']
            is_wechat = any(domain in host.lower() for domain in wechat_domains)

            if is_wechat:
                print(f"    ⚡ 微信相关: {host}")

            # 连接到目标服务器
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.settimeout(10)
            remote_socket.connect((host, port))

            # 发送连接成功响应
            client_socket.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')

            # 转发数据（不解密，仅用于建立连接）
            self.forward_data(client_socket, remote_socket, host)

        except Exception as e:
            print(f"    [!] HTTPS连接失败: {e}")

    def handle_http_request(self, client_socket, request, request_str):
        """处理 HTTP 请求"""
        try:
            # 解析请求信息
            lines = request_str.split('\n')
            first_line = lines[0]
            parts = first_line.split()

            if len(parts) < 3:
                return

            method, url, protocol = parts[0], parts[1], parts[2]

            # 解析 URL
            parsed_url = urlparse(url)
            host = parsed_url.netloc or self.extract_host(lines)
            path = parsed_url.path or '/'
            if parsed_url.query:
                path += '?' + parsed_url.query

            port = 80
            if ':' in host:
                host, port = host.split(':')
                port = int(port)

            # 检查是否是文件请求
            is_file = any(ext in url.lower() for ext in self.file_extensions)
            if is_file:
                print(f"    📄 可能是文件: {path}")

            # 连接到目标服务器
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.settimeout(10)
            remote_socket.connect((host, port))

            # 重构请求
            new_request = f"{method} {path} {protocol}\r\n"
            for line in lines[1:]:
                if line.strip() and not line.lower().startswith('proxy-'):
                    new_request += line + '\r\n'

            remote_socket.send(new_request.encode())

            # 接收响应
            response = b''
            response_header = b''
            header_complete = False

            while True:
                try:
                    remote_socket.settimeout(3)
                    chunk = remote_socket.recv(8192)
                    if not chunk:
                        break
                    response += chunk
                    client_socket.send(chunk)

                    # 只解析响应头
                    if not header_complete:
                        response_header += chunk
                        if b'\r\n\r\n' in response_header:
                            header_complete = True

                except socket.timeout:
                    break

            # 分析响应
            if response:
                self.analyze_response(url, request_str, response_header if header_complete else response, host)

            remote_socket.close()

        except Exception as e:
            print(f"    [!] HTTP请求失败: {e}")

    def extract_host(self, lines):
        """从请求头中提取 Host"""
        for line in lines:
            if line.lower().startswith('host:'):
                return line.split(':', 1)[1].strip()
        return 'unknown'

    def forward_data(self, client_socket, remote_socket, host):
        """双向转发数据，并尝试记录部分信息"""
        sockets = [client_socket, remote_socket]
        data_count = 0
        try:
            while True:
                readable, _, _ = select.select(sockets, [], [], 5)
                if not readable:
                    break
                for sock in readable:
                    data = sock.recv(8192)
                    if not data:
                        return

                    data_count += len(data)

                    # 尝试在数据流中查找文件特征（可能会看到部分未加密的信息）
                    if sock is remote_socket and data_count < 50000:  # 只检查前50KB
                        data_str = data.decode('utf-8', errors='ignore')
                        # 查找可能的文件扩展名
                        for ext in self.file_extensions:
                            if ext in data_str.lower():
                                print(f"    📎 在 {host} 的流量中发现 {ext} 特征")
                                break

                    if sock is client_socket:
                        remote_socket.send(data)
                    else:
                        client_socket.send(data)
        except:
            pass

    def analyze_response(self, url, request_str, response, host):
        """分析响应，判断是否为文件下载"""
        try:
            response_str = response.decode('utf-8', errors='ignore')

            # 检查 URL 是否包含文件扩展名
            is_file = any(ext in url.lower() for ext in self.file_extensions)

            # 检查 Content-Type
            content_type_match = re.search(r'Content-Type:\s*([^\r\n]+)', response_str, re.IGNORECASE)
            content_type = content_type_match.group(1).strip() if content_type_match else ''

            is_file_type = any(ct in content_type for ct in self.file_content_types)

            # 检查 Content-Disposition
            has_attachment = 'attachment' in response_str.lower()

            # 检查响应状态
            status_match = re.search(r'HTTP/\d\.\d\s+(\d+)', response_str)
            status_code = status_match.group(1) if status_match else 'unknown'

            # 显示响应信息
            if content_type:
                print(f"    Content-Type: {content_type}")
            print(f"    Status: {status_code}")

            # 如果是文件，记录下来
            if is_file or is_file_type or has_attachment:
                # 提取请求头
                headers = {}
                for line in request_str.split('\n')[1:]:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        headers[key.strip()] = value.strip()

                # 提取文件名
                filename = self.extract_filename(url, response_str)

                captured = {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'url': url,
                    'filename': filename,
                    'content_type': content_type,
                    'status_code': status_code,
                    'headers': headers,
                    'host': host
                }

                self.captured_urls.append(captured)

                print(f"    ✅ 捕获到文件!")
                print(f"    📁 文件名: {filename}")
                print(f"    🔗 URL: {url}")
                print("    " + "=" * 66)

        except Exception as e:
            print(f"    [!] 分析响应失败: {e}")

    def extract_filename(self, url, response_str):
        """提取文件名"""
        # 从 Content-Disposition 提取
        match = re.search(r'filename[*]?=["\']?([^"\';\r\n]+)', response_str, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # 从 URL 提取
        path = urlparse(url).path
        if '/' in path:
            filename = path.split('/')[-1]
            if filename:
                return filename

        return 'unknown'

    def save_logs(self):
        """保存捕获的 URL 到文件"""
        print(f"\n[*] 共处理 {self.request_count} 个请求")

        if self.captured_urls:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.captured_urls, f, ensure_ascii=False, indent=2)
            print(f"[*] 已保存 {len(self.captured_urls)} 个文件记录到 {self.log_file}")
        else:
            print("[*] 没有捕获到文件")

if __name__ == '__main__':
    print("""
╔════════════════════════════════════════════════════════════════════╗
║         微信小程序抓包工具 - 调试增强版                           ║
╚════════════════════════════════════════════════════════════════════╝

本版本会显示所有经过代理的请求，帮助排查问题。

常见问题排查：
1. 如果没有任何日志输出 → 手机代理配置可能有误
2. 如果有HTTP请求但没有文件 → 小程序可能使用HTTPS加密
3. 如果看到微信相关域名 → 说明流量已通过代理

提示：
- [数字] 表示请求序号
- HTTP 表示明文请求（可以完整分析）
- HTTPS 表示加密请求（只能看到域名）
- ⚡ 表示微信相关域名
- 📄 表示可能的文件请求
- ✅ 表示成功捕获文件

""")

    proxy = ProxySnifferDebug()
    proxy.start()
