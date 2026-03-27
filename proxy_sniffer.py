#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信小程序抓包代理工具
功能：拦截 HTTP/HTTPS 请求，提取文件下载链接
"""

import socket
import threading
import re
import json
from datetime import datetime
from urllib.parse import urlparse
import ssl
import select

class ProxySniffer:
    def __init__(self, host='0.0.0.0', port=8888, log_file='captured_urls.json'):
        self.host = host
        self.port = port
        self.log_file = log_file
        self.captured_urls = []
        self.running = False

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

        print(f"[*] 代理服务器启动成功")
        print(f"[*] 监听地址: {self.host}:{self.port}")
        print(f"[*] 日志文件: {self.log_file}")
        print(f"[*] 请配置手机代理为: {self.get_local_ip()}:{self.port}")
        print(f"[*] 按 Ctrl+C 停止服务\n")

        try:
            while self.running:
                client_socket, client_address = server_socket.accept()
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
                return

            request_str = request.decode('utf-8', errors='ignore')

            # 解析请求
            first_line = request_str.split('\n')[0]
            method = first_line.split()[0] if first_line.split() else ''

            # 处理 CONNECT 方法（HTTPS）
            if method == 'CONNECT':
                self.handle_https_connect(client_socket, request_str)
            else:
                self.handle_http_request(client_socket, request, request_str)

        except Exception as e:
            print(f"[!] 处理请求出错: {e}")
        finally:
            client_socket.close()

    def handle_https_connect(self, client_socket, request_str):
        """处理 HTTPS CONNECT 请求"""
        try:
            # 提取目标主机和端口
            first_line = request_str.split('\n')[0]
            url = first_line.split()[1]
            host, port = url.split(':') if ':' in url else (url, 443)
            port = int(port)

            # 连接到目标服务器
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((host, port))

            # 发送连接成功响应
            client_socket.send(b'HTTP/1.1 200 Connection Established\r\n\r\n')

            # 转发数据（不解密，仅用于建立连接）
            self.forward_data(client_socket, remote_socket)

        except Exception as e:
            print(f"[!] HTTPS连接错误: {e}")

    def handle_http_request(self, client_socket, request, request_str):
        """处理 HTTP 请求"""
        try:
            # 解析请求信息
            lines = request_str.split('\n')
            first_line = lines[0]
            method, url, protocol = first_line.split()

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

            # 连接到目标服务器
            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((host, port))

            # 重构请求
            new_request = f"{method} {path} {protocol}\r\n"
            for line in lines[1:]:
                if line.strip() and not line.lower().startswith('proxy-'):
                    new_request += line + '\r\n'

            remote_socket.send(new_request.encode())

            # 接收响应
            response = b''
            while True:
                try:
                    remote_socket.settimeout(2)
                    chunk = remote_socket.recv(8192)
                    if not chunk:
                        break
                    response += chunk
                    client_socket.send(chunk)
                except socket.timeout:
                    break

            # 分析响应，提取文件链接
            self.analyze_response(url, request_str, response)

            remote_socket.close()

        except Exception as e:
            print(f"[!] HTTP请求错误: {e}")

    def extract_host(self, lines):
        """从请求头中提取 Host"""
        for line in lines:
            if line.lower().startswith('host:'):
                return line.split(':', 1)[1].strip()
        return 'unknown'

    def forward_data(self, client_socket, remote_socket):
        """双向转发数据"""
        sockets = [client_socket, remote_socket]
        try:
            while True:
                readable, _, _ = select.select(sockets, [], [], 5)
                if not readable:
                    break
                for sock in readable:
                    data = sock.recv(8192)
                    if not data:
                        return
                    if sock is client_socket:
                        remote_socket.send(data)
                    else:
                        client_socket.send(data)
        except:
            pass

    def analyze_response(self, url, request_str, response):
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
                    'headers': headers
                }

                self.captured_urls.append(captured)

                print(f"[+] 捕获文件: {filename}")
                print(f"    URL: {url}")
                print(f"    类型: {content_type}")
                print()

        except Exception as e:
            pass

    def extract_filename(self, url, response_str):
        """提取文件名"""
        # 从 Content-Disposition 提取
        match = re.search(r'filename[*]?=["\']?([^"\';\r\n]+)', response_str, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # 从 URL 提取
        path = urlparse(url).path
        if '/' in path:
            return path.split('/')[-1]

        return 'unknown'

    def save_logs(self):
        """保存捕获的 URL 到文件"""
        if self.captured_urls:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(self.captured_urls, f, ensure_ascii=False, indent=2)
            print(f"[*] 已保存 {len(self.captured_urls)} 个捕获记录到 {self.log_file}")
        else:
            print("[*] 没有捕获到文件")

if __name__ == '__main__':
    proxy = ProxySniffer()
    proxy.start()
