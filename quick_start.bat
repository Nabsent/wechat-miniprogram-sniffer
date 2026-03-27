@echo off
chcp 65001 >nul
cls

:menu
cls
echo ========================================
echo    微信小程序抓包工具 - 快速启动
echo ========================================
echo.
echo  1. 启动 HTTPS 解密代理
echo  2. 下载捕获的文件
echo  3. 查看捕获的文件列表
echo  4. 查看本机 IP 地址
echo  5. 安装依赖（首次使用必选）
echo  6. 查看使用说明
echo  0. 退出
echo.
echo ========================================

set /p choice="请选择操作 (0-6): "

if "%choice%"=="1" goto start_https_proxy
if "%choice%"=="2" goto download_files
if "%choice%"=="3" goto list_files
if "%choice%"=="4" goto get_ip
if "%choice%"=="5" goto install_deps
if "%choice%"=="6" goto show_help
if "%choice%"=="0" goto end

echo 无效的选择，请重试
timeout /t 2 >nul
goto menu

:start_https_proxy
cls
echo [*] 启动 HTTPS 解密代理...
echo [*] 首次使用请先安装依赖（选项5）并在手机安装证书
echo.
python start_https_proxy.py
echo.
echo 代理服务器已停止
pause
goto menu

:download_files
cls
echo [*] 启动文件下载工具...
echo.
python file_downloader.py
echo.
pause
goto menu

:list_files
cls
echo [*] 查看捕获的文件列表...
echo.
python file_downloader.py --list
echo.
pause
goto menu

:get_ip
cls
echo [*] 获取本机 IP 地址...
echo.
python get_ip.py
goto menu

:install_deps
cls
echo [*] 安装依赖（mitmproxy）...
echo.
call install_https.bat
goto menu

:show_help
cls
echo ========================================
echo            使用说明
echo ========================================
echo.
echo 使用步骤:
echo ================================
echo 1. 选择菜单项 5 - 安装依赖
echo 2. 选择菜单项 1 - 启动 HTTPS 解密代理
echo 3. 配置手机代理（服务器=电脑IP, 端口=8888）
echo 4. 手机浏览器访问 http://mitm.it 安装证书
echo    - Android: 还需在"信任的凭据-用户"中启用
echo    - iOS: 还需在"证书信任设置"中启用
echo 5. 使用微信小程序，触发文件下载
echo 6. 电脑终端会显示捕获的文件
echo 7. 停止代理后，选择菜单项 2 下载文件
echo.
echo 详细步骤请查看: HTTPS抓包指南.md
echo.
echo 详细说明请查看 README.md
echo ========================================
echo.
pause
goto menu

:end
echo 感谢使用！
exit
