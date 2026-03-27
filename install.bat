@echo off
chcp 65001 >nul
echo ========================================
echo 微信小程序抓包工具 - 依赖安装
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.7+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [*] 检测到 Python 版本:
python --version
echo.

REM 检查 pip 是否可用
pip --version >nul 2>&1
if errorlevel 1 (
    echo [错误] pip 未安装，正在尝试安装...
    python -m ensurepip --default-pip
)

echo [*] 正在安装依赖包...
echo.

REM 安装 requests（用于文件下载）
echo [1/1] 安装 requests...
pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 使用方法:
echo   1. 启动抓包代理: python proxy_sniffer.py
echo   2. 下载文件:     python file_downloader.py
echo.
echo 详细说明请查看 README.md
echo.
pause
