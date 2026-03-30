#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能文件抓取器 - 自动分析和下载
功能：
1. 自动识别文件列表 API
2. 解析列表，提取所有文件链接
3. 自动下载所有文件
"""

from mitmproxy import http, ctx
import json
import os
import re
import requests
from datetime import datetime
from urllib.parse import urlparse, unquote, parse_qs
from pathlib import Path

class SmartFileSniffer:
    def __init__(self):
        self.captured_urls = []
        self.api_patterns = []  # 识别到的文件列表API
        self.file_list_responses = []  # 文件列表响应
        self.download_dir = 'auto_downloads'
        self.log_file = 'captured_data.json'
        self.session_cookies = {}
        self.session_headers = {}

        # 创建下载目录
        Path(self.download_dir).mkdir(exist_ok=True)

        # 文件类型识别
        self.file_extensions = [
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.zip', '.rar', '.7z', '.png', '.jpg', '.jpeg', '.gif',
            '.mp4', '.mp3', '.avi', '.mov', '.txt', '.json', '.xml'
        ]

        self.file_content_types = [
            'application/pdf', 'application/msword',
            'application/vnd.ms-excel', 'application/vnd.ms-powerpoint',
            'application/vnd.openxmlformats',
            'application/zip', 'application/x-rar', 'application/octet-stream',
            'image/', 'video/', 'audio/'
        ]

        # API 模式识别关键词
        self.api_keywords = [
            'list', 'files', 'documents', 'getList', 'query',
            'search', 'items', 'data', 'content', 'attachment'
        ]

    def request(self, flow: http.HTTPFlow) -> None:
        """处理请求，记录会话信息"""
        request = flow.request

        # 保存 cookies 和认证信息
        if request.host not in self.session_cookies:
            self.session_cookies[request.host] = {}

        if 'cookie' in request.headers:
            self.session_cookies[request.host]['cookie'] = request.headers['cookie']

        # 保存重要的请求头
        important_headers = ['authorization', 'token', 'x-token', 'x-auth-token']
        for header in important_headers:
            if header in request.headers:
                if request.host not in self.session_headers:
                    self.session_headers[request.host] = {}
                self.session_headers[request.host][header] = request.headers[header]

    def response(self, flow: http.HTTPFlow) -> None:
        """处理响应，智能识别和处理"""
        request = flow.request
        response = flow.response

        if not response:
            return

        url = request.pretty_url
        content_type = response.headers.get('content-type', '').lower()

        # 情况1: 直接的文件下载
        if self.is_file_response(url, content_type, response):
            self.handle_file_download(flow)

        # 情况2: JSON API 响应（可能包含文件列表）
        elif 'application/json' in content_type:
            self.handle_json_response(flow)

        # 情况3: HTML 页面（可能包含文件链接）
        elif 'text/html' in content_type:
            self.handle_html_response(flow)

    def is_file_response(self, url, content_type, response):
        """判断是否是文件响应"""
        # 检查 URL 扩展名
        is_file_url = any(ext in url.lower() for ext in self.file_extensions)

        # 检查 Content-Type
        is_file_type = any(ct in content_type for ct in self.file_content_types)

        # 检查 Content-Disposition
        has_attachment = 'attachment' in response.headers.get('content-disposition', '').lower()

        return is_file_url or is_file_type or has_attachment

    def handle_file_download(self, flow):
        """处理文件下载"""
        request = flow.request
        response = flow.response
        url = request.pretty_url

        filename = self.extract_filename(url, response)
        content_length = response.headers.get('content-length', 'unknown')

        # 收集请求信息
        headers = dict(request.headers)

        captured = {
            'type': 'file',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'url': url,
            'filename': filename,
            'content_type': response.headers.get('content-type', ''),
            'content_length': content_length,
            'method': request.method,
            'headers': headers,
            'host': request.host
        }

        self.captured_urls.append(captured)

        # 自动下载
        self.auto_download_file(captured, response.content)

        # 显示
        size_mb = self.format_size(content_length)
        ctx.log.warn(f"\n✅ 捕获文件: {filename} ({size_mb})")
        ctx.log.warn(f"   📥 已自动下载")

    def handle_json_response(self, flow):
        """处理 JSON 响应，查找文件列表"""
        request = flow.request
        response = flow.response
        url = request.pretty_url

        try:
            # 解析 JSON
            json_data = json.loads(response.content.decode('utf-8'))

            # 检查是否是文件列表 API
            if self.looks_like_file_list_api(url, json_data):
                ctx.log.info(f"\n🔍 发现疑似文件列表API: {url}")

                # 提取文件信息
                file_items = self.extract_file_items(json_data)

                if file_items:
                    ctx.log.warn(f"   📋 发现 {len(file_items)} 个文件")

                    # 保存列表信息
                    list_data = {
                        'type': 'file_list',
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'api_url': url,
                        'method': request.method,
                        'headers': dict(request.headers),
                        'files': file_items,
                        'host': request.host
                    }

                    self.file_list_responses.append(list_data)

                    # 自动下载列表中的所有文件
                    self.auto_download_file_list(list_data)

        except Exception as e:
            pass

    def handle_html_response(self, flow):
        """处理 HTML 响应，提取文件链接"""
        # 简单实现：查找 href 中的文件链接
        try:
            html_content = flow.response.content.decode('utf-8', errors='ignore')

            # 提取所有链接
            file_urls = []
            for ext in self.file_extensions:
                pattern = rf'href=["\']([^"\']*{ext}[^"\']*)["\']'
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                file_urls.extend(matches)

            if file_urls:
                ctx.log.info(f"\n📄 页面中发现 {len(file_urls)} 个文件链接")

        except:
            pass

    def looks_like_file_list_api(self, url, json_data):
        """判断是否是文件列表 API"""
        # 检查 URL 中的关键词
        url_lower = url.lower()
        has_keyword = any(keyword in url_lower for keyword in self.api_keywords)

        if not has_keyword:
            return False

        # 检查 JSON 结构
        # 通常文件列表 API 返回数组或包含数组的对象
        if isinstance(json_data, list) and len(json_data) > 0:
            return True

        if isinstance(json_data, dict):
            # 检查常见的数据字段
            data_fields = ['data', 'list', 'items', 'files', 'documents', 'content', 'result']
            for field in data_fields:
                if field in json_data:
                    value = json_data[field]
                    if isinstance(value, list) and len(value) > 0:
                        return True

        return False

    def extract_file_items(self, json_data):
        """从 JSON 中提取文件项"""
        file_items = []

        # 递归查找文件信息
        def find_files(obj, depth=0):
            if depth > 5:  # 限制递归深度
                return

            if isinstance(obj, dict):
                # 查找文件相关字段
                file_info = {}

                # URL 字段
                url_fields = ['url', 'fileUrl', 'file_url', 'downloadUrl', 'download_url', 'link', 'path', 'src']
                for field in url_fields:
                    if field in obj:
                        file_info['url'] = obj[field]
                        break

                # 文件名字段
                name_fields = ['name', 'fileName', 'file_name', 'title', 'filename']
                for field in name_fields:
                    if field in obj:
                        file_info['name'] = obj[field]
                        break

                # 大小字段
                size_fields = ['size', 'fileSize', 'file_size', 'length']
                for field in size_fields:
                    if field in obj:
                        file_info['size'] = obj[field]
                        break

                # 如果找到了 URL，认为是一个文件项
                if 'url' in file_info:
                    file_items.append(file_info)

                # 继续递归
                for value in obj.values():
                    find_files(value, depth + 1)

            elif isinstance(obj, list):
                for item in obj:
                    find_files(item, depth + 1)

        find_files(json_data)
        return file_items

    def auto_download_file(self, file_info, content=None):
        """自动下载文件"""
        filename = file_info['filename']

        # 清理文件名
        filename = self.sanitize_filename(filename)

        # 如果已经有内容（从响应中获取），直接保存
        if content:
            file_path = Path(self.download_dir) / filename

            # 避免重复
            counter = 1
            while file_path.exists():
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{counter}{ext}"
                file_path = Path(self.download_dir) / filename
                counter += 1

            with open(file_path, 'wb') as f:
                f.write(content)

            ctx.log.info(f"   💾 保存到: {file_path}")
        else:
            # 需要发起新的下载请求
            self.download_from_url(file_info)

    def auto_download_file_list(self, list_data):
        """自动下载文件列表中的所有文件"""
        files = list_data['files']
        host = list_data['host']
        headers = list_data['headers']

        ctx.log.warn(f"\n🚀 开始自动下载 {len(files)} 个文件...")

        for idx, file_item in enumerate(files, 1):
            try:
                url = file_item['url']
                filename = file_item.get('name', f'file_{idx}')

                # 处理相对路径
                if not url.startswith('http'):
                    url = f"https://{host}{url}" if url.startswith('/') else f"https://{host}/{url}"

                ctx.log.info(f"[{idx}/{len(files)}] {filename}")

                # 下载
                self.download_from_url({
                    'url': url,
                    'filename': filename,
                    'headers': headers,
                    'host': host
                })

            except Exception as e:
                ctx.log.error(f"   ❌ 下载失败: {e}")

    def download_from_url(self, file_info):
        """从 URL 下载文件"""
        url = file_info['url']
        filename = file_info.get('filename', 'download')
        headers = file_info.get('headers', {})

        try:
            # 构建请求头
            download_headers = {}

            # 添加基本头
            download_headers['User-Agent'] = headers.get('user-agent',
                'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) MicroMessenger/8.0.40')

            # 添加认证相关头
            for key, value in headers.items():
                if key.lower() in ['cookie', 'authorization', 'token', 'referer']:
                    download_headers[key] = value

            # 发送请求
            response = requests.get(url, headers=download_headers, timeout=30, stream=True)
            response.raise_for_status()

            # 保存文件
            filename = self.sanitize_filename(filename)
            file_path = Path(self.download_dir) / filename

            # 避免重复
            counter = 1
            while file_path.exists():
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{counter}{ext}"
                file_path = Path(self.download_dir) / filename
                counter += 1

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            ctx.log.info(f"   ✅ 已下载: {file_path}")

        except Exception as e:
            ctx.log.error(f"   ❌ 下载失败: {e}")

    def extract_filename(self, url, response):
        """提取文件名"""
        # 从 Content-Disposition 提取
        content_disposition = response.headers.get('content-disposition', '')
        match = re.search(r'filename[*]?=["\']?([^"\';\r\n]+)', content_disposition, re.IGNORECASE)
        if match:
            filename = match.group(1).strip()
            return unquote(filename)

        # 从 URL 提取
        path = urlparse(url).path
        if '/' in path:
            filename = path.split('/')[-1]
            if filename:
                return unquote(filename)

        # 从 Content-Type 生成默认名
        content_type = response.headers.get('content-type', '').lower()
        ext_map = {
            'application/pdf': '.pdf',
            'application/msword': '.doc',
            'image/png': '.png',
            'image/jpeg': '.jpg',
        }

        for ct, ext in ext_map.items():
            if ct in content_type:
                return f'download_{datetime.now().strftime("%Y%m%d_%H%M%S")}{ext}'

        return 'unknown_file'

    def sanitize_filename(self, filename):
        """清理文件名"""
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '_')

        filename = unquote(filename)

        if not filename or filename.startswith('.'):
            filename = 'downloaded_file' + filename

        return filename

    def format_size(self, size_str):
        """格式化文件大小"""
        try:
            size = int(size_str)
            if size < 1024:
                return f"{size}B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f}KB"
            else:
                return f"{size / 1024 / 1024:.2f}MB"
        except:
            return size_str

    def save_logs(self):
        """保存日志"""
        data = {
            'captured_files': self.captured_urls,
            'file_lists': self.file_list_responses,
        }

        try:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            ctx.log.error(f"保存日志失败: {e}")

    def done(self):
        """代理停止时调用"""
        self.save_logs()

        total_files = len(self.captured_urls)
        total_lists = len(self.file_list_responses)

        if total_files > 0 or total_lists > 0:
            ctx.log.info(f"\n{'='*60}")
            ctx.log.info(f"✅ 捕获汇总:")
            ctx.log.info(f"   📄 直接文件: {total_files} 个")
            ctx.log.info(f"   📋 文件列表: {total_lists} 个")
            ctx.log.info(f"   💾 保存位置: {os.path.abspath(self.download_dir)}")
            ctx.log.info(f"   📝 日志文件: {self.log_file}")
            ctx.log.info(f"{'='*60}")
        else:
            ctx.log.info("\n未捕获到文件")

# mitmproxy 入口
addons = [
    SmartFileSniffer()
]
