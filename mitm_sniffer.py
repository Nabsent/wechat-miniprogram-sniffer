#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于 mitmproxy 的 HTTPS 解密抓包工具
自动捕获微信小程序的文件下载
"""

from mitmproxy import http, ctx
import json
import os
from datetime import datetime
from urllib.parse import urlparse, unquote
import re

class WeChatFileSniffer:
    def __init__(self):
        self.captured_urls = []
        self.log_file = 'captured_urls.json'
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
            'application/vnd.openxmlformats',
            'application/zip', 'application/x-rar', 'application/octet-stream',
            'image/', 'video/', 'audio/'
        ]

        # 初始化提示已在启动脚本中显示，这里不重复

    def request(self, flow: http.HTTPFlow) -> None:
        """处理请求"""
        self.request_count += 1
        # 只在捕获到文件时显示详细信息，减少日志

    def response(self, flow: http.HTTPFlow) -> None:
        """处理响应"""
        request = flow.request
        response = flow.response

        if not response:
            return

        url = request.pretty_url
        content_type = response.headers.get('content-type', '').lower()
        content_disposition = response.headers.get('content-disposition', '').lower()

        # 检查是否是文件
        is_file_url = any(ext in url.lower() for ext in self.file_extensions)
        is_file_type = any(ct in content_type for ct in self.file_content_types)
        has_attachment = 'attachment' in content_disposition

        if is_file_url or is_file_type or has_attachment:
            # 提取文件名
            filename = self.extract_filename(url, response)

            # 获取文件大小
            content_length = response.headers.get('content-length', 'unknown')

            # 收集请求头
            headers = {}
            for key, value in request.headers.items():
                headers[key] = value

            captured = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'url': url,
                'filename': filename,
                'content_type': content_type,
                'content_length': content_length,
                'status_code': response.status_code,
                'method': request.method,
                'headers': headers,
                'host': request.host
            }

            self.captured_urls.append(captured)

            # 显示捕获信息（精简版）
            size_mb = f"{int(content_length) / 1024 / 1024:.2f}MB" if content_length.isdigit() else content_length
            ctx.log.warn(f"\n✅ 捕获文件: {filename} ({size_mb})")
            ctx.log.warn(f"   {url}\n")

            # 实时保存
            self.save_logs()

    def extract_filename(self, url, response):
        """提取文件名"""
        # 从 Content-Disposition 提取
        content_disposition = response.headers.get('content-disposition', '')
        match = re.search(r'filename[*]?=["\']?([^"\';\r\n]+)', content_disposition, re.IGNORECASE)
        if match:
            filename = match.group(1).strip()
            # URL解码
            filename = unquote(filename)
            return filename

        # 从 URL 提取
        path = urlparse(url).path
        if '/' in path:
            filename = path.split('/')[-1]
            if filename:
                filename = unquote(filename)
                return filename

        # 根据Content-Type生成默认文件名
        content_type = response.headers.get('content-type', '').lower()
        ext_map = {
            'application/pdf': '.pdf',
            'application/msword': '.doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
            'application/vnd.ms-excel': '.xls',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
            'image/png': '.png',
            'image/jpeg': '.jpg',
            'image/gif': '.gif',
            'video/mp4': '.mp4',
        }

        for ct, ext in ext_map.items():
            if ct in content_type:
                return f'download_{datetime.now().strftime("%Y%m%d_%H%M%S")}{ext}'

        return 'unknown_file'

    def save_logs(self):
        """保存捕获的 URL 到文件"""
        if self.captured_urls:
            try:
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    json.dump(self.captured_urls, f, ensure_ascii=False, indent=2)
            except Exception as e:
                ctx.log.error(f"保存日志失败: {e}")

    def done(self):
        """代理停止时调用"""
        if self.captured_urls:
            ctx.log.info(f"\n✅ 共捕获 {len(self.captured_urls)} 个文件，已保存到: {self.log_file}")
        else:
            ctx.log.info(f"\n未捕获到文件（共处理 {self.request_count} 个请求）")

# mitmproxy 入口
addons = [
    WeChatFileSniffer()
]
