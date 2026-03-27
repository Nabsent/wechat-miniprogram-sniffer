#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件下载工具
从捕获的 URL 日志中下载文件
"""

import json
import os
import sys
import requests
from urllib.parse import urlparse, unquote

class FileDownloader:
    def __init__(self, log_file='captured_urls.json', output_dir='downloaded_files'):
        self.log_file = log_file
        self.output_dir = output_dir
        self.session = requests.Session()

        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

    def load_captured_urls(self):
        """加载捕获的 URL 日志"""
        if not os.path.exists(self.log_file):
            print(f"[!] 日志文件不存在: {self.log_file}")
            return []

        with open(self.log_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_captures(self):
        """列出所有捕获的文件"""
        captures = self.load_captured_urls()

        if not captures:
            print("[!] 没有捕获到任何文件")
            return []

        print(f"\n共捕获 {len(captures)} 个文件:\n")
        for idx, capture in enumerate(captures, 1):
            print(f"[{idx}] {capture['filename']}")
            print(f"    时间: {capture['timestamp']}")
            print(f"    类型: {capture['content_type']}")
            print(f"    URL: {capture['url'][:80]}...")
            print()

        return captures

    def download_file(self, capture, custom_filename=None):
        """下载单个文件"""
        url = capture['url']
        filename = custom_filename or capture['filename']
        headers = capture.get('headers', {})

        # 确保文件名安全
        filename = self.sanitize_filename(filename)
        output_path = os.path.join(self.output_dir, filename)

        # 如果文件已存在，添加序号
        if os.path.exists(output_path):
            base, ext = os.path.splitext(filename)
            counter = 1
            while os.path.exists(output_path):
                filename = f"{base}_{counter}{ext}"
                output_path = os.path.join(self.output_dir, filename)
                counter += 1

        print(f"[*] 正在下载: {filename}")
        print(f"[*] 来源: {url}")

        try:
            # 发送请求
            response = self.session.get(url, headers=headers, stream=True, timeout=30)
            response.raise_for_status()

            # 获取文件大小
            total_size = int(response.headers.get('content-length', 0))

            # 下载文件
            downloaded = 0
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r[*] 进度: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='')

            print(f"\n[+] 下载成功: {output_path}\n")
            return True

        except Exception as e:
            print(f"\n[!] 下载失败: {e}\n")
            # 删除不完整的文件
            if os.path.exists(output_path):
                os.remove(output_path)
            return False

    def sanitize_filename(self, filename):
        """清理文件名，移除非法字符"""
        # 移除或替换非法字符
        illegal_chars = '<>:"/\\|?*'
        for char in illegal_chars:
            filename = filename.replace(char, '_')

        # URL 解码
        filename = unquote(filename)

        # 如果文件名为空或只是扩展名，使用默认名称
        if not filename or filename.startswith('.'):
            filename = 'downloaded_file' + filename

        return filename

    def download_all(self):
        """下载所有捕获的文件"""
        captures = self.load_captured_urls()

        if not captures:
            print("[!] 没有可下载的文件")
            return

        print(f"\n[*] 准备下载 {len(captures)} 个文件...\n")

        success = 0
        failed = 0

        for idx, capture in enumerate(captures, 1):
            print(f"[{idx}/{len(captures)}]")
            if self.download_file(capture):
                success += 1
            else:
                failed += 1

        print(f"\n下载完成:")
        print(f"  成功: {success}")
        print(f"  失败: {failed}")
        print(f"  保存位置: {os.path.abspath(self.output_dir)}")

    def download_by_index(self, indices):
        """根据索引下载指定文件"""
        captures = self.load_captured_urls()

        if not captures:
            print("[!] 没有可下载的文件")
            return

        for idx in indices:
            if 1 <= idx <= len(captures):
                self.download_file(captures[idx - 1])
            else:
                print(f"[!] 无效的索引: {idx}")

    def download_by_url(self, url, headers=None):
        """直接下载指定 URL"""
        capture = {
            'url': url,
            'filename': os.path.basename(urlparse(url).path) or 'download',
            'content_type': 'unknown',
            'headers': headers or {}
        }
        self.download_file(capture)

def main():
    downloader = FileDownloader()

    if len(sys.argv) == 1:
        # 交互模式
        print("=" * 60)
        print("微信小程序文件下载工具")
        print("=" * 60)

        captures = downloader.list_captures()

        if not captures:
            sys.exit(1)

        print("选择操作:")
        print("  1. 下载所有文件")
        print("  2. 下载指定序号的文件 (例如: 1,3,5)")
        print("  3. 下载指定 URL")
        print("  0. 退出")

        choice = input("\n请输入选项: ").strip()

        if choice == '1':
            downloader.download_all()
        elif choice == '2':
            indices_str = input("请输入文件序号 (用逗号分隔): ").strip()
            try:
                indices = [int(i.strip()) for i in indices_str.split(',')]
                downloader.download_by_index(indices)
            except ValueError:
                print("[!] 输入格式错误")
        elif choice == '3':
            url = input("请输入 URL: ").strip()
            if url:
                downloader.download_by_url(url)

    elif sys.argv[1] == '--all':
        # 下载所有
        downloader.download_all()

    elif sys.argv[1] == '--url':
        # 下载指定 URL
        if len(sys.argv) < 3:
            print("用法: python file_downloader.py --url <URL>")
            sys.exit(1)
        downloader.download_by_url(sys.argv[2])

    elif sys.argv[1] == '--list':
        # 仅列出
        downloader.list_captures()

    else:
        print("用法:")
        print("  python file_downloader.py           # 交互模式")
        print("  python file_downloader.py --all     # 下载所有")
        print("  python file_downloader.py --list    # 列出捕获的文件")
        print("  python file_downloader.py --url <URL>  # 下载指定URL")

if __name__ == '__main__':
    main()
