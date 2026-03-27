@echo off
echo ========================================
echo   HTTPS Proxy - Install Dependencies
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.7+
    pause
    exit /b 1
)

echo [*] Python version:
python --version
echo.

echo [*] Installing mitmproxy (may take a few minutes)...
echo.

REM Use mirror for faster download (China users)
pip install mitmproxy requests -i https://pypi.tuna.tsinghua.edu.cn/simple

if errorlevel 1 (
    echo.
    echo [!] Failed, trying official source...
    pip install mitmproxy requests
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next Steps:
echo   1. Start proxy: python start_https_proxy.py
echo   2. Configure phone proxy: PC_IP:8888
echo   3. Visit on phone: http://mitm.it
echo   4. Download and install certificate
echo   5. Android: Enable in Settings - Security - Trusted Credentials - User
echo   6. iOS: Enable in Settings - General - About - Certificate Trust
echo.
echo For details: See README.md
echo.
pause
