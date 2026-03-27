@echo off
cls
echo ========================================
echo      GitHub Push Tool
echo ========================================
echo.

REM Check remote
git remote -v >nul 2>&1
if %errorlevel% equ 0 (
    git remote -v | findstr "origin" >nul
    if %errorlevel% equ 0 (
        echo [*] Remote repository found:
        git remote -v
        echo.
        set /p continue="Continue pushing? (y/n): "
        if /i not "%continue%"=="y" (
            echo Cancelled
            pause
            exit /b 0
        )
        goto push_code
    )
)

echo [1] Configure Remote Repository
echo.
echo Create a new repo on GitHub (without README)
echo Visit: https://github.com/new
echo.

set /p username="GitHub username: "
set /p reponame="Repository name (default: WeCrawler): "

if "%reponame%"=="" set reponame=WeCrawler

echo.
echo [*] Configuring remote...
git branch -M main
git remote add origin https://github.com/%username%/%reponame%.git

echo.
echo [2] Push to GitHub
echo.
echo Pushing to: https://github.com/%username%/%reponame%
echo.
echo NOTE: Use Personal Access Token as password
echo Get Token: https://github.com/settings/tokens
echo.
pause

:push_code
echo.
echo [*] Pushing...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo        Push Successful!
    echo ========================================
    echo.
    echo Visit your repository:
    git remote get-url origin
    echo.
) else (
    echo.
    echo ========================================
    echo        Push Failed
    echo ========================================
    echo.
    echo Possible reasons:
    echo 1. Repository not exists (create on GitHub first)
    echo 2. Wrong credentials (use Personal Access Token)
    echo 3. Network issues
    echo.
    echo See README.md for details
    echo.
)

pause
