# 微信小程序文件抓包下载工具

一个完整的微信小程序文件抓包与下载解决方案，**支持 HTTPS 解密**，可以捕获加密的文件请求。

## ✨ 特性

- 🤖 **智能自动化** - 自动识别文件列表API，一键下载所有文件
- ✅ **支持 HTTPS 解密** - 可以抓取微信小程序的加密请求
- ✅ 自动捕获文件下载链接（PDF、图片、视频、Office 文档等）
- ✅ 会话保持（自动处理 cookies/token）
- ✅ 支持批量下载和选择性下载
- ✅ 提供两种模式：智能自动 + 手动控制
- ✅ 跨平台支持（Windows/Linux/macOS）

## 🚀 快速开始

### ⭐ 推荐：智能自动模式

一次操作，自动下载所有文件！

```cmd
# 方法一：图形菜单
quick_start.bat
# 选择 1 - Start Smart Proxy (Auto Download)

# 方法二：命令行
python start_smart_proxy.py
```

**工作流程：**
1. 手机配置代理并安装证书
2. 打开微信小程序，浏览文件列表
3. 系统自动识别文件列表API
4. 自动解析并下载所有文件到 `auto_downloads/`

### 手动模式

```cmd
python start_https_proxy.py
```

手动选择要下载的文件。

#### 步骤 3: 配置手机并安装证书

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

### 核心脚本

| 文件 | 说明 |
|------|------|
| `start_smart_proxy.py` | ⭐ 智能代理（自动下载所有文件）|
| `smart_sniffer.py` | 智能分析器（API识别+自动下载）|
| `start_https_proxy.py` | HTTPS代理（手动模式）|
| `mitm_sniffer.py` | 基础抓包脚本 |
| `file_downloader.py` | 手动下载工具 |

### 辅助工具

| 文件 | 说明 |
|------|------|
| `quick_start.bat` | 图形化启动菜单 |
| `install_https.bat` | 依赖安装脚本 |
| `get_ip.py` | 查看本机IP |
| `setup_windows_proxy.py` | Windows系统代理配置 |

## 🎯 工作原理

本工具使用 **mitmproxy** 作为中间人代理，通过以下步骤解密HTTPS流量：

1. 拦截手机的网络请求
2. 使用自签名证书解密HTTPS内容
3. 分析请求和响应，识别文件下载
4. 记录文件URL和请求头
5. 提供下载工具获取文件

> ⚠️ **重要**: 必须在手机上安装并信任证书才能解密HTTPS！

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

### 查看本机IP
```cmd
python get_ip.py
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

### Q4: 能上网但捕获不到文件？

**检查**:
1. 证书是否正确安装并信任
2. 手机浏览器访问 `https://www.baidu.com` 测试
3. 如果浏览器正常但小程序不行 → 见Q1

更多问题请查看: [HTTPS抓包指南.md](HTTPS抓包指南.md)

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
1. 启动 HTTPS 解密代理
2. 下载捕获的文件
3. 查看捕获列表
4. 查看本机IP
5. 安装依赖 ⭐ (首次必选)
6. 查看帮助

---

**祝您抓包顺利！** 🎊

有问题？查看 [HTTPS抓包指南.md](HTTPS抓包指南.md) 或提交 Issue。
