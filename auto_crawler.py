#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全自动文件爬虫 - 学习模式
用户只需打开小程序，系统自动分析、遍历、下载所有文件
"""

from mitmproxy import http, ctx
import json
import os
import re
import requests
import time
from datetime import datetime
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from pathlib import Path
from copy import deepcopy
from concurrent.futures import ThreadPoolExecutor
import threading

class AutoCrawler:
    def __init__(self):
        # 学习阶段：记录用户的操作模式
        self.learned_apis = {}  # 学习到的API模式
        self.file_list_apis = []  # 文件列表API
        self.pagination_patterns = []  # 分页模式

        # 会话信息
        self.session_data = {}  # {host: {cookies, headers, tokens}}

        # 文件信息
        self.all_files = []  # 所有发现的文件
        self.downloaded_files = set()  # 已下载的文件URL

        # 配置
        self.download_dir = 'auto_downloads'
        self.log_file = 'crawler_log.json'
        self.auto_crawl_enabled = True  # 是否自动爬取

        # 线程池用于异步下载和翻页，避免阻塞代理
        self.executor = ThreadPoolExecutor(max_workers=5)
        self.crawl_tasks = []
        self.download_lock = threading.Lock()

        Path(self.download_dir).mkdir(exist_ok=True)

        # API识别模式
        self.file_extensions = ['.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
                               '.zip', '.rar', '.7z', '.png', '.jpg', '.jpeg', '.gif',
                               '.mp4', '.mp3', '.avi', '.mov']

        self.list_keywords = ['list', 'files', 'documents', 'items', 'data',
                             'query', 'search', 'getList', 'page', 'records']

        ctx.log.info("\n" + "="*70)
        ctx.log.info("🤖 全自动文件爬虫已启动")
        ctx.log.info("="*70)
        ctx.log.info("请在手机上打开小程序，点进文件列表")
        ctx.log.info("系统会自动学习API结构，然后自动爬取所有文件")
        ctx.log.info("="*70 + "\n")

    def request(self, flow: http.HTTPFlow):
        """记录请求，学习会话信息"""
        request = flow.request
        host = request.host

        # 保存会话信息
        if host not in self.session_data:
            self.session_data[host] = {
                'cookies': {},
                'headers': {},
                'user_agent': None
            }

        # 提取cookies
        if 'cookie' in request.headers:
            self.session_data[host]['cookies'] = self.parse_cookies(request.headers['cookie'])

        # 提取认证信息
        auth_headers = ['authorization', 'token', 'x-token', 'x-auth-token', 'x-access-token']
        for header in auth_headers:
            if header in request.headers:
                self.session_data[host]['headers'][header] = request.headers[header]

        # 保存User-Agent
        if 'user-agent' in request.headers:
            self.session_data[host]['user_agent'] = request.headers['user-agent']

    def response(self, flow: http.HTTPFlow):
        """分析响应，学习API模式"""
        request = flow.request
        response = flow.response

        if not response:
            return

        url = request.pretty_url
        content_type = response.headers.get('content-type', '').lower()

        # 处理JSON API响应
        if 'application/json' in content_type:
            try:
                json_data = json.loads(response.content.decode('utf-8'))

                # 调试：显示所有JSON API
                ctx.log.info(f"\n[DEBUG] JSON API: {url[:100]}")

                # 分析是否是文件列表API
                if self.is_file_list_api(url, json_data):
                    ctx.log.warn(f"\n[AUTO CRAWLER] 发现文件列表API")
                    self.learn_api_pattern(url, request, json_data)
                else:
                    ctx.log.info(f"[DEBUG] 不匹配 - URL无关键词或无文件数据")

            except Exception as e:
                ctx.log.error(f"[DEBUG] JSON解析错误: {e}")

        # 处理直接的文件下载
        elif self.is_file_download(url, content_type, response):
            self.handle_file_download(flow)

    def is_file_list_api(self, url, json_data):
        """判断是否是文件列表API"""
        # 先尝试提取文件，如果能提取到就认为是文件列表
        files = self.extract_file_list(json_data)
        if len(files) > 0:
            ctx.log.info(f"[DEBUG] 从JSON提取到 {len(files)} 个文件")
            return True

        url_lower = url.lower()

        # 检查URL关键词（作为辅助判断）
        has_keyword = any(kw in url_lower for kw in self.list_keywords)
        if not has_keyword:
            ctx.log.info(f"[DEBUG] URL无关键词且无文件数据")
            return False

        # 有关键词但没提取到文件，可能是空列表，也返回True
        ctx.log.info(f"[DEBUG] URL有关键词，但提取不到文件")
        return False

    def learn_api_pattern(self, url, request, json_data):
        """学习API模式"""
        ctx.log.warn(f"\n🎓 学习到新的API模式:")
        ctx.log.warn(f"   URL: {url}")

        # 提取文件列表
        files = self.extract_file_list(json_data)
        ctx.log.warn(f"   📋 发现 {len(files)} 个文件")

        # 分析分页信息
        pagination = self.detect_pagination(url, json_data)

        # 保存API模式
        api_pattern = {
            'url': url,
            'method': request.method,
            'timestamp': datetime.now().isoformat(),
            'files': files,
            'pagination': pagination,
            'total_count': self.extract_total_count(json_data),
            'params': dict(parse_qs(urlparse(url).query)),
            'host': request.host
        }

        self.file_list_apis.append(api_pattern)

        # 显示分析结果
        if pagination:
            ctx.log.info(f"   📄 分页信息: {pagination}")
            ctx.log.info(f"   📊 总数: {api_pattern['total_count']}")

        # 异步自动爬取（不阻塞代理）
        if self.auto_crawl_enabled:
            ctx.log.warn(f"\n🚀 已提交爬取任务到后台执行...")
            task = self.executor.submit(self.auto_crawl_all_pages, api_pattern)
            self.crawl_tasks.append(task)

    def detect_pagination(self, url, json_data):
        """检测分页模式"""
        pagination = {}

        # 从URL参数检测
        parsed = urlparse(url)
        params = parse_qs(parsed.query)

        # 常见的分页参数
        page_keys = ['page', 'pageNum', 'pageNo', 'p', 'current']
        size_keys = ['pageSize', 'size', 'limit', 'perPage', 'count']

        for key in page_keys:
            if key in params:
                pagination['page_param'] = key
                pagination['current_page'] = int(params[key][0])
                break

        for key in size_keys:
            if key in params:
                pagination['size_param'] = key
                pagination['page_size'] = int(params[key][0])
                break

        # 从响应体检测
        def search_pagination(obj, depth=0):
            if depth > 3 or not isinstance(obj, dict):
                return

            # 总页数
            for key in ['totalPages', 'total_pages', 'pageCount', 'pages']:
                if key in obj and isinstance(obj[key], int):
                    pagination['total_pages'] = obj[key]

            # 总记录数
            for key in ['total', 'totalCount', 'total_count', 'count']:
                if key in obj and isinstance(obj[key], int):
                    pagination['total_count'] = obj[key]

            # 当前页
            for key in ['currentPage', 'current_page', 'page', 'pageNum']:
                if key in obj and isinstance(obj[key], int):
                    pagination['current_page'] = obj[key]

            # 每页大小
            for key in ['pageSize', 'page_size', 'size', 'limit']:
                if key in obj and isinstance(obj[key], int):
                    pagination['page_size'] = obj[key]

            for value in obj.values():
                if isinstance(value, dict):
                    search_pagination(value, depth + 1)

        search_pagination(json_data)

        return pagination if pagination else None

    def extract_total_count(self, json_data):
        """提取总数"""
        def search_total(obj, depth=0):
            if depth > 3:
                return None

            if isinstance(obj, dict):
                for key in ['total', 'totalCount', 'total_count', 'count']:
                    if key in obj and isinstance(obj[key], int):
                        return obj[key]

                for value in obj.values():
                    result = search_total(value, depth + 1)
                    if result:
                        return result

            return None

        return search_total(json_data)

    def extract_file_list(self, json_data):
        """从JSON中提取文件列表"""
        files = []

        def find_files(obj, depth=0):
            if depth > 5:
                return

            if isinstance(obj, dict):
                # 检查是否是文件对象
                file_info = {}

                # URL字段
                for key in ['url', 'fileUrl', 'file_url', 'downloadUrl', 'download_url',
                           'link', 'path', 'href', 'src', 'address']:
                    if key in obj and isinstance(obj[key], str):
                        file_info['url'] = obj[key]
                        break

                # 文件名
                for key in ['name', 'fileName', 'file_name', 'title', 'filename']:
                    if key in obj and isinstance(obj[key], str):
                        file_info['name'] = obj[key]
                        break

                # 大小
                for key in ['size', 'fileSize', 'file_size', 'length']:
                    if key in obj:
                        file_info['size'] = obj[key]
                        break

                # ID（用于构造URL）
                for key in ['id', 'fileId', 'file_id']:
                    if key in obj:
                        file_info['id'] = obj[key]
                        break

                if 'url' in file_info or 'id' in file_info:
                    files.append(file_info)

                # 递归查找
                for value in obj.values():
                    find_files(value, depth + 1)

            elif isinstance(obj, list):
                for item in obj:
                    find_files(item, depth + 1)

        find_files(json_data)
        return files

    def auto_crawl_all_pages(self, api_pattern):
        """自动爬取所有分页（在线程池中执行，不阻塞代理）"""
        pagination = api_pattern.get('pagination')

        if not pagination:
            ctx.log.info("   ℹ️  未检测到分页，直接下载当前页文件")
            self.download_file_list(api_pattern['files'], api_pattern['host'])
            return

        # 计算总页数
        total_pages = pagination.get('total_pages')
        total_count = pagination.get('total_count')
        page_size = pagination.get('page_size', 10)
        current_page = pagination.get('current_page', 1)

        if not total_pages and total_count:
            total_pages = (total_count + page_size - 1) // page_size

        if not total_pages:
            ctx.log.warn("   ⚠️  无法确定总页数")
            self.download_file_list(api_pattern['files'], api_pattern['host'])
            return

        ctx.log.info(f"   📖 共 {total_pages} 页，当前第 {current_page} 页")
        ctx.log.info(f"   🔄 后台爬取中，代理继续正常工作...")

        # 下载第一页
        all_files = list(api_pattern['files'])

        # 爬取其他页
        page_param = pagination.get('page_param', 'page')
        base_url = api_pattern['url']

        for page in range(current_page + 1, total_pages + 1):
            ctx.log.info(f"   [{page}/{total_pages}] 正在获取第 {page} 页...")

            # 构造新URL
            new_url = self.build_page_url(base_url, page_param, page)

            # 发送请求
            files = self.fetch_page(new_url, api_pattern['host'], api_pattern['method'])

            if files:
                all_files.extend(files)
                ctx.log.info(f"       ✅ 获取到 {len(files)} 个文件")
            else:
                ctx.log.warn(f"       ⚠️  获取失败")

            time.sleep(0.5)  # 避免请求过快

        ctx.log.warn(f"\n📊 爬取完成！共 {len(all_files)} 个文件")

        # 批量下载（异步）
        self.download_file_list(all_files, api_pattern['host'])

    def build_page_url(self, base_url, page_param, page):
        """构造分页URL"""
        parsed = urlparse(base_url)
        params = parse_qs(parsed.query)
        params[page_param] = [str(page)]

        new_query = urlencode(params, doseq=True)
        new_parsed = parsed._replace(query=new_query)

        return urlunparse(new_parsed)

    def fetch_page(self, url, host, method='GET'):
        """获取指定页的数据"""
        try:
            session_data = self.session_data.get(host, {})

            headers = {
                'User-Agent': session_data.get('user_agent',
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) MicroMessenger/8.0.40')
            }

            # 添加认证头
            headers.update(session_data.get('headers', {}))

            # 添加cookies
            cookies = session_data.get('cookies', {})

            response = requests.request(method, url, headers=headers, cookies=cookies, timeout=10)
            response.raise_for_status()

            json_data = response.json()
            return self.extract_file_list(json_data)

        except Exception as e:
            ctx.log.error(f"请求失败: {e}")
            return []

    def download_file_list(self, files, host):
        """批量下载文件（异步执行）"""
        ctx.log.warn(f"\n💾 已提交 {len(files)} 个文件到下载队列...")

        for idx, file_info in enumerate(files, 1):
            url = file_info.get('url')
            if not url:
                # 尝试从ID构造URL
                file_id = file_info.get('id')
                if file_id:
                    ctx.log.warn(f"   [{idx}/{len(files)}] 文件ID: {file_id}（需要构造下载URL）")
                continue

            # 处理相对路径
            if not url.startswith('http'):
                if url.startswith('/'):
                    url = f"https://{host}{url}"
                else:
                    url = f"https://{host}/{url}"

            # 跳过已下载
            if url in self.downloaded_files:
                continue

            filename = file_info.get('name', f'file_{idx}')
            size = file_info.get('size', 'unknown')

            # 提交到线程池异步下载
            task = self.executor.submit(self.download_file, url, filename, host, idx, len(files), size)
            self.crawl_tasks.append(task)

    def download_file(self, url, filename, host, index=None, total=None, size='unknown'):
        """下载单个文件（在线程池中执行）"""
        # 跳过已下载
        with self.download_lock:
            if url in self.downloaded_files:
                return True
            self.downloaded_files.add(url)

        try:
            if index and total:
                ctx.log.info(f"   [{index}/{total}] {filename} ({self.format_size(size)})")

            session_data = self.session_data.get(host, {})

            headers = {
                'User-Agent': session_data.get('user_agent',
                    'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) MicroMessenger/8.0.40')
            }
            headers.update(session_data.get('headers', {}))

            response = requests.get(url, headers=headers,
                                   cookies=session_data.get('cookies', {}),
                                   timeout=30, stream=True)
            response.raise_for_status()

            # 清理文件名
            filename = self.sanitize_filename(filename)
            filepath = Path(self.download_dir) / filename

            # 避免重名
            counter = 1
            while filepath.exists():
                name, ext = os.path.splitext(filename)
                filename = f"{name}_{counter}{ext}"
                filepath = Path(self.download_dir) / filename
                counter += 1

            # 下载
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            ctx.log.info(f"       ✅ 已保存")
            return True

        except Exception as e:
            ctx.log.error(f"       ❌ 下载失败: {e}")
            return False

    def is_file_download(self, url, content_type, response):
        """判断是否是文件下载"""
        is_file_url = any(ext in url.lower() for ext in self.file_extensions)
        is_file_type = any(ct in content_type for ct in
                          ['pdf', 'msword', 'excel', 'powerpoint', 'zip', 'rar',
                           'image/', 'video/', 'audio/', 'octet-stream'])
        has_attachment = 'attachment' in response.headers.get('content-disposition', '').lower()

        return is_file_url or is_file_type or has_attachment

    def handle_file_download(self, flow):
        """处理单个文件下载"""
        request = flow.request
        response = flow.response
        url = request.pretty_url

        if url in self.downloaded_files:
            return

        filename = self.extract_filename(url, response)

        # 自动保存
        filepath = Path(self.download_dir) / self.sanitize_filename(filename)

        counter = 1
        while filepath.exists():
            name, ext = os.path.splitext(self.sanitize_filename(filename))
            filepath = Path(self.download_dir) / f"{name}_{counter}{ext}"
            counter += 1

        with open(filepath, 'wb') as f:
            f.write(response.content)

        self.downloaded_files.add(url)

        size = len(response.content)
        ctx.log.warn(f"\n✅ 下载文件: {filename} ({self.format_size(size)})")
        ctx.log.info(f"   💾 {filepath}")

    def extract_filename(self, url, response):
        """提取文件名"""
        # 从Content-Disposition提取
        cd = response.headers.get('content-disposition', '')
        match = re.search(r'filename[*]?=["\']?([^"\';\r\n]+)', cd, re.IGNORECASE)
        if match:
            from urllib.parse import unquote
            return unquote(match.group(1).strip())

        # 从URL提取
        path = urlparse(url).path
        if '/' in path:
            filename = path.split('/')[-1]
            if filename:
                from urllib.parse import unquote
                return unquote(filename)

        return f'file_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

    def sanitize_filename(self, filename):
        """清理文件名"""
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        return filename or 'unnamed_file'

    def format_size(self, size):
        """格式化文件大小"""
        try:
            size = int(size)
            if size < 1024:
                return f"{size}B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f}KB"
            else:
                return f"{size / 1024 / 1024:.2f}MB"
        except:
            return str(size)

    def parse_cookies(self, cookie_string):
        """解析cookie字符串"""
        cookies = {}
        for item in cookie_string.split(';'):
            if '=' in item:
                key, value = item.strip().split('=', 1)
                cookies[key] = value
        return cookies

    def done(self):
        """保存日志"""
        # 等待所有爬取和下载任务完成
        if self.crawl_tasks:
            ctx.log.info(f"\n⏳ 等待 {len(self.crawl_tasks)} 个后台任务完成...")

            # 等待所有任务完成
            success = 0
            failed = 0
            for task in self.crawl_tasks:
                try:
                    result = task.result(timeout=120)  # 每个任务最多等待120秒
                    if result:
                        success += 1
                    else:
                        failed += 1
                except Exception as e:
                    ctx.log.error(f"任务执行失败: {e}")
                    failed += 1

            ctx.log.info(f"✅ 所有任务已完成: {success} 成功, {failed} 失败")

        # 关闭线程池
        self.executor.shutdown(wait=True)

        summary = {
            'learned_apis': self.file_list_apis,
            'downloaded_count': len(self.downloaded_files),
            'downloaded_files': list(self.downloaded_files),
            'timestamp': datetime.now().isoformat()
        }

        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        ctx.log.info(f"\n{'='*70}")
        ctx.log.info(f"📊 爬取汇总:")
        ctx.log.info(f"   🎓 学习到 {len(self.file_list_apis)} 个API")
        ctx.log.info(f"   📥 下载了 {len(self.downloaded_files)} 个文件")
        ctx.log.info(f"   📂 保存位置: {os.path.abspath(self.download_dir)}")
        ctx.log.info(f"   📝 日志: {self.log_file}")
        ctx.log.info(f"{'='*70}")

addons = [AutoCrawler()]
