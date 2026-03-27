@echo off
cls

:menu
cls
echo ========================================
echo   WeChat Mini Program File Sniffer
echo ========================================
echo.
echo  1. Start HTTPS Proxy
echo  2. Download Files
echo  3. List Captured Files
echo  4. Show Local IP
echo  5. Install Dependencies (First Time)
echo  6. Help
echo  0. Exit
echo.
echo ========================================

set /p choice="Select (0-6): "

if "%choice%"=="1" goto start_https_proxy
if "%choice%"=="2" goto download_files
if "%choice%"=="3" goto list_files
if "%choice%"=="4" goto get_ip
if "%choice%"=="5" goto install_deps
if "%choice%"=="6" goto show_help
if "%choice%"=="0" goto end

echo Invalid choice, try again...
timeout /t 2 >nul
goto menu

:start_https_proxy
cls
echo [*] Starting HTTPS proxy...
echo [*] First time? Install dependencies (Option 5) and certificate first
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
echo Steps:
echo 1. Install dependencies (Option 5)
echo 2. Start HTTPS proxy (Option 1)
echo 3. Configure phone proxy: PC_IP:8888
echo 4. Install certificate: http://mitm.it
echo    - Android: Enable in Settings - Security - Trusted Credentials - User
echo    - iOS: Enable in Settings - General - About - Certificate Trust
echo 5. Use WeChat Mini Program and download files
echo 6. Stop proxy and download files (Option 2)
echo.
echo For details: See README.md
echo ========================================
echo.
pause
goto menu

:end
echo Thanks for using!
exit
