# 微信小程序文件抓包下载工具

一个完整的微信小程序文件抓包与下载解决方案，**支持 HTTPS 解密**，可以捕获加密的文件请求。

## ✨ 特性

- ✅ **支持 HTTPS 解密** - 可以抓取微信小程序的加密请求
- ✅ 自动捕获文件下载链接（PDF、图片、视频、Office 文档等）
- ✅ 保留完整请求头信息用于下载
- ✅ 支持批量下载和选择性下载
- ✅ 提供调试工具帮助排查问题
- ✅ 跨平台支持（Windows/Linux/macOS）

## 🚀 快速开始（3步解决HTTPS问题）

### 步骤 1: 安装依赖

```cmd
install_https.bat
```

或使用快速启动菜单，选择"8. 安装 HTTPS 代理依赖"

### 步骤 2: 启动 HTTPS 解密代理

```cmd
python start_https_proxy.py
```

记下显示的 IP 地址（如 192.168.1.100）

### 步骤 3: 配置手机并安装证书

**配置代理：**
- 服务器/主机名: `192.168.1.100` (电脑IP)
- 端口: `8888`

**安装证书（关键步骤）：**
1. 手机浏览器访问: `http://mitm.it`
2. 下载对应系统的证书
3. **Android**: 安装后在"设置→安全→信任的凭据→用户"中启用
4. **iOS**: 安装描述文件后，在"设置→通用→关于本机→证书信任设置"中启用

详细步骤: [HTTPS抓包指南.md](HTTPS抓包指南.md)

### 步骤 4: 使用并下载

1. 打开微信小程序，点击文件
2. 电脑终端显示捕获信息
3. 停止代理（Ctrl+C）
4. 运行 `python file_downloader.py` 下载文件

## 📂 文件说明

### 🔥 主要文件（HTTPS解密）

| 文件 | 说明 |
|------|------|
| `start_https_proxy.py` | ⭐ HTTPS解密代理启动脚本 |
| `mitm_sniffer.py` | mitmproxy 抓包脚本 |
| `install_https.bat` | HTTPS 依赖安装脚本 |
| `file_downloader.py` | 文件下载工具 |

### 🛠️ 辅助工具

| 文件 | 说明 |
|------|------|
| `proxy_sniffer_debug.py` | HTTP调试代理（不能抓HTTPS内容）|
| `get_ip.py` | 查看本机IP地址 |
| `test_proxy.py` | 测试代理连接 |
| `quick_start.bat` | Windows 图形化菜单 |

### 📖 文档

| 文件 | 说明 |
|------|------|
| `HTTPS抓包指南.md` | ⭐ 详细的证书安装和使用教程 |
| `手机配置指南.md` | 各品牌手机代理配置 |
| `问题排查.md` | 常见问题解决方案 |

## 🎯 两种方案对比

| 方案 | 适用场景 | HTTPS支持 | 需要证书 |
|------|---------|-----------|---------|
| **HTTPS 解密代理** | 微信小程序（推荐） | ✅ 完全支持 | ✅ 必须安装 |
| **HTTP 调试代理** | HTTP网站、网络调试 | ❌ 仅域名 | ❌ 不需要 |

> ⚠️ **重要**: 微信小程序必须使用 HTTPS 解密代理！

## 📱 证书安装重点

### Android

1. 访问 `http://mitm.it` 下载证书
2. 点击安装
3. **关键**：设置 → 安全 → **信任的凭据** → **用户** → 启用 mitmproxy

⚠️ **Android 7.0+** 默认不信任用户证书，建议：
- 使用 Android 6.0 手机或模拟器
- 或 Root 后安装为系统证书

### iOS

1. 访问 `http://mitm.it` 下载描述文件
2. 设置 → 已下载描述文件 → 安装
3. **关键**：设置 → 通用 → 关于本机 → **证书信任设置** → 启用 mitmproxy

⚠️ **第3步容易遗漏**，这是最常见的失败原因！

详细图文教程: [HTTPS抓包指南.md](HTTPS抓包指南.md)

## 💻 命令行使用

### 启动 HTTPS 代理
```cmd
python start_https_proxy.py
```

### 下载文件
```cmd
# 交互模式（推荐）
python file_downloader.py

# 下载所有捕获的文件
python file_downloader.py --all

# 下载指定URL
python file_downloader.py --url "https://example.com/file.pdf"

# 仅查看列表
python file_downloader.py --list
```

### 其他工具
```cmd
# 查看本机IP
python get_ip.py

# 测试代理连接
python test_proxy.py

# HTTP调试代理（显示所有请求）
python proxy_sniffer_debug.py
```

## 📋 完整检查清单

使用前请确认：

- [ ] 安装了 mitmproxy (`install_https.bat`)
- [ ] 启动了 HTTPS 代理 (`start_https_proxy.py`)
- [ ] 手机与电脑在同一WiFi
- [ ] 手机代理配置正确（IP:8888）
- [ ] 访问 `http://mitm.it` 下载了证书
- [ ] **Android**: 在"信任的凭据-用户"中启用了 mitmproxy
- [ ] **iOS**: 在"证书信任设置"中启用了 mitmproxy
- [ ] 测试：手机访问 `https://www.baidu.com`，电脑显示HTTPS请求
- [ ] 打开微信小程序
- [ ] 电脑显示捕获到文件
- [ ] 停止代理，运行下载工具

## ❓ 常见问题

### Q1: 浏览器能抓，微信小程序不能？

**原因**: Android 7.0+ 不信任用户证书

**解决**:
- 使用 Android 6.0 或模拟器（推荐）
- Root 后安装为系统证书
- 使用 Xposed + JustTrustMe 模块

### Q2: iOS 安装证书后仍显示不安全？

**原因**: 忘记在"证书信任设置"中启用

**解决**: 设置 → 通用 → 关于本机 → **证书信任设置** → 启用

### Q3: 访问 mitm.it 无法连接？

**检查**:
1. 代理是否在运行
2. 手机代理配置是否正确
3. 是 `http://mitm.it` 不是 `https://`

**替代方案**: 从电脑复制证书文件
- Windows: `C:\Users\用户名\.mitmproxy\mitmproxy-ca-cert.cer`
- 发送到手机手动安装

### Q4: 能上网但没有日志输出？

运行调试版查看：
```cmd
python proxy_sniffer_debug.py
```

如果浏览器有日志但小程序没有 → 证书未正确安装

更多问题: [问题排查.md](问题排查.md) | [HTTPS抓包指南.md](HTTPS抓包指南.md)

## 🔒 安全提示

1. **使用后删除证书** - mitmproxy 证书可解密流量
2. **关闭代理** - 抓包完成后恢复正常上网
3. **仅在可信网络** - 不要在公共WiFi使用
4. **不分享证书私钥** - `~/.mitmproxy/` 目录

## 🆚 工具对比

| 工具 | HTTPS | 证书 | 捕获小程序 | 难度 | 价格 |
|------|-------|------|-----------|------|------|
| **本工具(mitmproxy)** | ✅ | 需要 | ✅ | ⭐⭐ 中 | 免费 |
| Fiddler | ✅ | 需要 | ✅ | ⭐⭐ 中 | 免费 |
| Charles | ✅ | 需要 | ✅ | ⭐⭐ 中 | 付费 |
| Wireshark | ✅ | 不需要 | ❌ | ⭐⭐⭐ 难 | 免费 |

## 📚 依赖版本

- Python 3.7+
- mitmproxy >= 9.0.0
- requests >= 2.28.0

## 🎉 更新日志

### v2.0.0 (当前版本)
- ✨ 新增 HTTPS 解密支持
- ✨ 完整捕获微信小程序文件
- ✨ 自动化证书安装流程
- 📝 详细的图文教程
- 🔧 增强调试工具

### v1.0.0
- 基础 HTTP 代理
- 文件识别和下载
- 交互式界面

## 💡 使用建议

1. **首次使用**: 推荐运行 `quick_start.bat` 使用图形菜单
2. **遇到问题**: 先查看 [HTTPS抓包指南.md](HTTPS抓包指南.md)
3. **证书安装**: 这是成功的关键，务必完整操作
4. **Android 7.0+**: 建议使用模拟器或旧手机

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

## 🚀 快速启动菜单

**推荐新手使用**:

```cmd
quick_start.bat
```

菜单选项：
1. 启动 HTTPS 解密代理 ⭐
2. 启动 HTTP 调试代理
3. 下载捕获的文件
4. 查看捕获列表
5. 查看本机IP
6. 测试代理连接
7. 安装 HTTP 依赖
8. 安装 HTTPS 依赖 ⭐ (首次必选)
9. 查看帮助

---

**祝您抓包顺利！** 🎊

有问题？查看 [HTTPS抓包指南.md](HTTPS抓包指南.md) 或提交 Issue。
