@echo off
chcp 65001 >nul
echo ========================================
echo HTTPS 解密抓包工具 - 依赖安装
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.7+
    pause
    exit /b 1
)

echo [*] 检测到 Python 版本:
python --version
echo.

echo [*] 正在安装 mitmproxy（可能需要几分钟）...
echo.

REM 使用国内镜像加速
pip install mitmproxy requests -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo.
    echo [!] 安装失败，尝试使用官方源...
    pip install mitmproxy requests
)

echo.
echo ========================================
echo 安装完成！
echo ========================================
echo.
echo 下一步：安装手机证书
echo   1. 启动代理: python start_https_proxy.py
echo   2. 手机配置代理为: 电脑IP:8888
echo   3. 手机浏览器访问: http://mitm.it
echo   4. 根据手机系统下载并安装证书
echo   5. Android需要到"设置-安全-信任的凭据-用户"中启用
echo   6. iOS需要到"设置-通用-关于本机-证书信任设置"中启用
echo.
echo 详细说明请查看: HTTPS抓包指南.md
echo.
pause
