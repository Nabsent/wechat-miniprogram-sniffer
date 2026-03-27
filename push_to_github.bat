@echo off
chcp 65001 >nul
cls
echo ========================================
echo      GitHub 快速推送工具
echo ========================================
echo.

REM 检查是否已配置远程仓库
git remote -v >nul 2>&1
if %errorlevel% equ 0 (
    git remote -v | findstr "origin" >nul
    if %errorlevel% equ 0 (
        echo [*] 检测到已配置的远程仓库:
        git remote -v
        echo.
        set /p continue="是否继续推送？(y/n): "
        if /i not "%continue%"=="y" (
            echo 已取消
            pause
            exit /b 0
        )
        goto push_code
    )
)

echo [1] 配置远程仓库
echo.
echo 请先在 GitHub 创建新仓库（不要初始化 README）
echo 访问: https://github.com/new
echo.

set /p username="输入你的 GitHub 用户名: "
set /p reponame="输入仓库名称 (默认: WeCrawler): "

if "%reponame%"=="" set reponame=WeCrawler

echo.
echo [*] 配置远程仓库...
git branch -M main
git remote add origin https://github.com/%username%/%reponame%.git

echo.
echo [2] 推送代码到 GitHub
echo.
echo 即将推送到: https://github.com/%username%/%reponame%
echo.
echo 提示: 密码请使用 GitHub Personal Access Token
echo 获取 Token: https://github.com/settings/tokens
echo.
pause

:push_code
echo.
echo [*] 正在推送代码...
git push -u origin main

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo        推送成功！
    echo ========================================
    echo.
    echo 访问你的仓库:
    git remote get-url origin
    echo.
) else (
    echo.
    echo ========================================
    echo        推送失败
    echo ========================================
    echo.
    echo 可能的原因:
    echo 1. 仓库不存在（先在 GitHub 创建）
    echo 2. 凭据错误（需要使用 Personal Access Token）
    echo 3. 网络问题
    echo.
    echo 详细说明请查看: GitHub推送指南.md
    echo.
)

pause
