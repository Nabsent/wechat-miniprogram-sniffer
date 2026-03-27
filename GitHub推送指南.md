# GitHub 项目创建和推送指南

## 方法一：使用 GitHub 网页创建（推荐）

### 1. 在 GitHub 创建新仓库

访问：https://github.com/new

填写信息：
- **Repository name**: `WeCrawler` 或 `wechat-miniprogram-sniffer`
- **Description**: 微信小程序文件抓包下载工具 - 支持HTTPS解密
- **Public/Private**: 选择 Public（公开）或 Private（私有）
- **⚠️ 不要勾选**:
  - ❌ Add a README file
  - ❌ Add .gitignore
  - ❌ Choose a license

点击 **Create repository**

### 2. 推送本地代码到 GitHub

复制 GitHub 显示的命令，或使用以下命令：

#### 如果使用 HTTPS（推荐，更简单）

```bash
cd "D:\gitspace\WeCrawler"
git branch -M main
git remote add origin https://github.com/你的用户名/WeCrawler.git
git push -u origin main
```

#### 如果使用 SSH（需要先配置 SSH 密钥）

```bash
cd "D:\gitspace\WeCrawler"
git branch -M main
git remote add origin git@github.com:你的用户名/WeCrawler.git
git push -u origin main
```

### 3. 输入 GitHub 凭据

- **用户名**: 你的 GitHub 用户名
- **密码**: 使用 Personal Access Token（不是账号密码）

**如何获取 Token：**
1. GitHub 右上角头像 → Settings
2. 左侧最底部 → Developer settings
3. Personal access tokens → Tokens (classic)
4. Generate new token (classic)
5. 勾选 `repo` 权限
6. 生成并复制 Token（只显示一次！）

---

## 方法二：使用 GitHub CLI（最简单）

### 1. 安装 GitHub CLI

Windows (使用 winget):
```cmd
winget install --id GitHub.cli
```

或下载安装：https://cli.github.com/

### 2. 登录 GitHub

```bash
gh auth login
```

按提示选择：
- GitHub.com
- HTTPS
- Login with a web browser（在浏览器中登录）

### 3. 创建仓库并推送

```bash
cd "D:\gitspace\WeCrawler"
gh repo create WeCrawler --public --source=. --remote=origin --push
```

选项说明：
- `--public`: 公开仓库（改为 `--private` 则为私有）
- `--source=.`: 使用当前目录
- `--remote=origin`: 设置远程名称
- `--push`: 立即推送

---

## 方法三：手动命令（适合已有 GitHub 账号配置）

### 快速推送脚本

```bash
# 1. 切换到项目目录
cd "D:\gitspace\WeCrawler"

# 2. 重命名分支为 main（GitHub 默认）
git branch -M main

# 3. 添加远程仓库（替换你的用户名）
git remote add origin https://github.com/你的用户名/WeCrawler.git

# 4. 推送代码
git push -u origin main
```

---

## 验证推送成功

访问你的仓库页面：
```
https://github.com/你的用户名/WeCrawler
```

应该能看到：
- ✅ README.md 显示在首页
- ✅ 所有 Python 脚本和文档
- ✅ 提交历史中有 "Initial commit"

---

## 常见问题

### Q1: git push 提示 "fatal: unable to access"

**原因**: 网络问题或代理设置

**解决**:
```bash
# 取消 git 代理
git config --global --unset http.proxy
git config --global --unset https.proxy

# 或设置代理（如果需要）
git config --global http.proxy http://127.0.0.1:7890
```

### Q2: 提示 "Support for password authentication was removed"

**原因**: GitHub 不再支持密码登录

**解决**: 使用 Personal Access Token 代替密码（见上文获取方法）

### Q3: git push 提示 "remote: Repository not found"

**原因**: 仓库不存在或 URL 错误

**解决**:
```bash
# 检查远程仓库
git remote -v

# 移除错误的远程仓库
git remote remove origin

# 重新添加正确的 URL
git remote add origin https://github.com/你的用户名/WeCrawler.git
```

### Q4: git push 被拒绝 (rejected)

**原因**: 远程仓库有本地没有的提交（例如在网页创建了 README）

**解决**:
```bash
# 先拉取远程更改
git pull origin main --allow-unrelated-histories

# 再推送
git push -u origin main
```

---

## 推送后的操作

### 1. 添加项目描述和标签

在 GitHub 仓库页面：
- 点击右上角的 ⚙️ (Settings)
- 添加 Description: `微信小程序文件抓包下载工具 - 支持HTTPS解密`
- 添加 Topics: `wechat`, `miniprogram`, `https`, `proxy`, `mitmproxy`, `sniffer`

### 2. 启用 GitHub Pages（可选）

如果想要一个在线文档页面：
- Settings → Pages
- Source: Deploy from a branch
- Branch: main / (root)
- 访问: `https://你的用户名.github.io/WeCrawler/`

### 3. 添加 License（可选）

```bash
# 在项目根目录创建 LICENSE 文件
echo "MIT License" > LICENSE
git add LICENSE
git commit -m "Add MIT license"
git push
```

### 4. 添加项目徽章（可选）

在 README.md 顶部添加：

```markdown
![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)
```

---

## 完整的推送命令（复制即用）

```bash
# 假设你的 GitHub 用户名是 yourname
cd "D:\gitspace\WeCrawler"
git branch -M main
git remote add origin https://github.com/yourname/WeCrawler.git
git push -u origin main
```

执行后输入你的 GitHub 用户名和 Personal Access Token 即可。

---

## 后续更新代码

当你修改了代码后：

```bash
cd "D:\gitspace\WeCrawler"
git add .
git commit -m "描述你的修改"
git push
```

---

祝你推送成功！🎉
