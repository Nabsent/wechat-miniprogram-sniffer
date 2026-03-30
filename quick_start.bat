@echo off
cls

:menu
cls
echo ========================================
echo   WeChat Mini Program File Sniffer
echo ========================================
echo.
echo  1. Auto Crawler (Fully Automatic) - Recommended
echo  2. Smart Proxy (Auto Download)
echo  3. HTTPS Proxy (Manual)
echo  4. Download Files
echo  5. List Captured Files
echo  6. Show Local IP
echo  7. Install Dependencies (First Time)
echo  8. Help
echo  0. Exit
echo.
echo ========================================

set /p choice="Select (0-8): "

if "%choice%"=="1" goto start_auto_crawler
if "%choice%"=="2" goto start_smart_proxy
if "%choice%"=="3" goto start_https_proxy
if "%choice%"=="4" goto download_files
if "%choice%"=="5" goto list_files
if "%choice%"=="6" goto get_ip
if "%choice%"=="7" goto install_deps
if "%choice%"=="8" goto show_help
if "%choice%"=="0" goto end

echo Invalid choice, try again...
timeout /t 2 >nul
goto menu

:start_auto_crawler
cls
echo [*] Starting Auto Crawler (Fully Automatic)...
echo [*] You just open the mini program, system does the rest!
echo.
python start_auto_crawler.py
echo.
echo Crawler stopped
pause
goto menu

:start_smart_proxy
cls
echo [*] Starting Smart Proxy (Auto Download)...
echo [*] Files will be automatically downloaded to: auto_downloads/
echo.
python start_smart_proxy.py
echo.
echo Proxy stopped
pause
goto menu

:start_https_proxy
cls
echo [*] Starting HTTPS proxy (Manual Mode)...
echo [*] First time? Install dependencies (Option 6) and certificate first
echo.
python start_https_proxy.py
echo.
echo Proxy stopped
pause
goto menu

:download_files
cls
echo [*] Starting file downloader...
echo.
python file_downloader.py
echo.
pause
goto menu

:list_files
cls
echo [*] Listing captured files...
echo.
python file_downloader.py --list
echo.
pause
goto menu

:get_ip
cls
echo [*] Getting local IP address...
echo.
python get_ip.py
goto menu

:install_deps
cls
echo [*] Installing dependencies (mitmproxy)...
echo.
call install_https.bat
goto menu

:show_help
cls
echo ========================================
echo            Quick Guide
echo ========================================
echo.
echo Best: Auto Crawler (Fully Automatic)
echo 1. Install dependencies (Option 7)
echo 2. Start Auto Crawler (Option 1)
echo 3. Configure phone proxy: PC_IP:8888
echo 4. Install certificate: http://mitm.it
echo 5. Open WeChat mini program and click into file list
echo 6. System automatically crawls ALL pages and downloads ALL files!
echo.
echo You only need to: Open mini program, Click once
echo System will: Learn API, Auto paginate, Download everything
echo.
echo.
echo Manual Mode:
echo 1. Start HTTPS Proxy (Option 2)
echo 2. Manually download files (Option 3)
echo.
echo For details: See README.md
echo ========================================
echo.
pause
goto menu

:end
echo Thanks for using!
exit
