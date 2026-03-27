# HTTPS 抓包完整指南

## 🎯 概述

本指南帮助您使用 mitmproxy 解密 HTTPS 流量，捕获微信小程序中的文件下载链接。

---

## 📦 第一步：安装依赖

### Windows

```cmd
install_https.bat
```

### Linux/macOS

```bash
pip3 install mitmproxy requests
```

安装时间：约 2-5 分钟（mitmproxy 较大，约 40MB）

---

## 🚀 第二步：启动代理

```cmd
python start_https_proxy.py
```

会显示：
```
[*] 本机 IP: 192.168.1.100
[*] 代理端口: 8888
```

记下这个 IP 地址。

---

## 📱 第三步：配置手机代理

### Android / iOS 通用配置

1. **连接同一WiFi**（手机和电脑）
2. **打开WiFi设置** → 点击已连接的WiFi
3. **配置代理** → 手动
4. **填写配置：**
   ```
   服务器/主机名: 192.168.1.100  (电脑的IP)
   端口:         8888
   ```
5. **保存**

---

## 🔐 第四步：安装证书（重要！）

### ⚠️ 必须安装证书才能解密HTTPS

#### 1. 手机浏览器访问

```
http://mitm.it
```

**注意：是 http 不是 https**

#### 2. 选择对应系统

网页会自动识别，或手动选择：
- Android → 下载证书
- iOS → 下载描述文件

#### 3. 安装证书

##### 📱 Android 详细步骤

**方式一：直接安装（推荐）**

1. 下载证书后，点击通知栏的下载完成提示
2. 选择"安装证书"
3. 证书名称填写: `mitmproxy`
4. 凭据用途选择: `VPN 和应用`
5. 点击"确定"

**方式二：手动安装**

1. 设置 → 安全 → 加密与凭据
2. 从存储设备安装 / 安装证书
3. 选择下载的 `mitmproxy-ca-cert.pem` 或 `.cer` 文件
4. 输入锁屏密码（如果有）
5. 证书名称: `mitmproxy`

**方式三：信任用户证书（适用于 Android 7.0+）**

⚠️ **Android 7.0+ 默认不信任用户证书，小程序可能无法抓包！**

解决方案：
- **推荐**: 使用 Android 6.0 或模拟器
- **Root 方案**: 将证书移动到系统证书目录
- **开发模式**: 修改应用的网络安全配置

**验证是否安装成功：**
1. 设置 → 安全 → 信任的凭据
2. 切换到"用户"标签
3. 应该能看到 `mitmproxy` 证书

##### 📱 iOS 详细步骤

**第一步：安装描述文件**

1. Safari 浏览器访问 `http://mitm.it`
2. 点击 iOS 图标
3. 点击"允许"下载配置描述文件
4. 提示"已下载描述文件" → 点击"关闭"
5. 打开"设置" App
6. 顶部会显示"已下载描述文件"
7. 点击进入 → 点击右上角"安装"
8. 输入解锁密码
9. 点击右上角"安装" → 再次点击"安装"
10. 点击"完成"

**第二步：信任证书（关键！）**

⚠️ **iOS 10.3+ 必须额外信任证书！**

1. 设置 → 通用 → 关于本机
2. 滚动到底部 → **证书信任设置**
3. 找到 `mitmproxy` 证书
4. **打开右侧的开关**（变成绿色）
5. 弹出警告 → 点击"继续"

**验证是否安装成功：**
1. 设置 → 通用 → VPN 与设备管理 / 描述文件
2. 应该能看到 `mitmproxy` 配置

---

## ✅ 第五步：测试抓包

### 1. 测试浏览器（验证代理工作）

手机浏览器访问: `http://www.baidu.com`

**电脑终端应该显示：**
```
[1] HTTP GET www.baidu.com/
```

### 2. 测试HTTPS（验证证书安装）

手机浏览器访问: `https://www.baidu.com`

**电脑终端应该显示：**
```
[2] HTTPS GET www.baidu.com/
```

如果显示证书错误 → 证书未正确安装或未信任

### 3. 测试微信小程序

1. 打开微信
2. 进入目标小程序
3. 触发文件下载或预览

**电脑终端应该显示：**
```
======================================================================
✅ 捕获到文件!
📁 文件名: document.pdf
📦 大小: 1234567 bytes
🔗 URL: https://example.com/files/document.pdf
📋 类型: application/pdf
======================================================================
```

---

## 📥 第六步：下载文件

停止代理（Ctrl+C），运行下载工具：

```cmd
python file_downloader.py
```

选择要下载的文件即可。

---

## ❓ 常见问题

### Q1: 手机浏览器能抓包，微信小程序不能

**原因：**
- Android 7.0+ 不信任用户证书
- 小程序使用了证书绑定（Certificate Pinning）

**解决方案：**

**方案A: 使用旧版Android（推荐）**
- Android 6.0 或更低版本
- Android 模拟器（如夜神、雷电）

**方案B: Root + 系统证书**
```bash
# 需要 Root 权限
adb root
adb remount
adb push mitmproxy-ca-cert.cer /system/etc/security/cacerts/
adb reboot
```

**方案C: 使用 Magisk 模块**
- 安装 Magisk
- 安装"Move Certificates"模块
- 自动将用户证书转为系统证书

**方案D: Xposed + JustTrustMe**
- 安装 Xposed 框架
- 安装 JustTrustMe 模块
- 绕过证书校验

### Q2: 访问 mitm.it 显示无法连接

**检查：**
1. 代理是否在运行
2. 手机代理配置是否正确
3. 访问的是 `http://mitm.it` 不是 `https://mitm.it`
4. 防火墙是否允许连接

**临时解决：**
证书文件在这里：
- Windows: `C:\Users\用户名\.mitmproxy\mitmproxy-ca-cert.cer`
- macOS/Linux: `~/.mitmproxy/mitmproxy-ca-cert.pem`

用电脑将证书发送到手机（QQ、微信、邮件等），然后手动安装。

### Q3: iOS 安装后仍然报证书错误

**必须完成两步：**
1. 安装描述文件（设置 → 已下载描述文件）
2. **信任证书**（设置 → 通用 → 关于本机 → 证书信任设置）

第二步很容易遗漏！

### Q4: Android 找不到"信任的凭据"

不同品牌位置不同：
- 小米: 设置 → 密码与安全 → 系统安全 → 加密与凭据 → 信任的凭据
- 华为: 设置 → 安全 → 更多安全设置 → 加密和凭据 → 信任的凭据
- OPPO: 设置 → 其他设置 → 设备与隐私 → 信任的凭据
- vivo: 设置 → 安全 → 更多安全设置 → 加密与凭据 → 信任的凭据

### Q5: 端口 8888 被占用

修改 `start_https_proxy.py` 中的端口：

```python
'--listen-port', '9999',  # 改为其他端口
```

手机代理端口也要相应修改。

### Q6: mitmproxy 安装失败

**Windows 常见问题：**
```cmd
# 错误：Microsoft Visual C++ 14.0 is required
# 解决：安装 Visual C++ Build Tools
# 下载：https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

或使用预编译版本：
```cmd
pip install --only-binary :all: mitmproxy
```

### Q7: 捕获到的文件下载失败

某些文件URL有时效性或需要特定Cookie。

在 `file_downloader.py` 中，会使用捕获的请求头进行下载。

如果仍然失败，可能需要：
1. 立即下载（不要等太久）
2. 在代理运行时直接保存文件内容（见高级用法）

---

## 🔧 高级用法

### 自动保存文件内容

修改 `mitm_sniffer.py`，在捕获文件时直接保存：

```python
def response(self, flow: http.HTTPFlow):
    # ... 现有代码 ...

    if is_file_url or is_file_type or has_attachment:
        # 保存文件内容
        save_dir = 'captured_files'
        os.makedirs(save_dir, exist_ok=True)

        file_path = os.path.join(save_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(response.content)

        ctx.log.warn(f"💾 已保存到: {file_path}")
```

### 过滤特定域名

只捕获特定网站的文件：

```python
def response(self, flow: http.HTTPFlow):
    # 只处理特定域名
    if 'example.com' not in flow.request.host:
        return

    # ... 其他代码 ...
```

### 使用 Web 界面

```cmd
# 使用 mitmweb 而不是 mitmdump
mitmweb -s mitm_sniffer.py --listen-port 8888
```

然后浏览器访问 `http://127.0.0.1:8081` 查看图形界面。

---

## 🔒 安全提示

1. **使用完毕删除证书**
   - Android: 设置 → 信任的凭据 → 用户 → 选择 mitmproxy → 删除
   - iOS: 设置 → 通用 → VPN与设备管理 → mitmproxy → 删除描述文件

2. **关闭代理**
   - 抓包完成后，记得关闭手机代理设置

3. **不要在公共WiFi使用**
   - 中间人代理本身是安全风险，只在可信网络使用

4. **证书私钥保管**
   - `~/.mitmproxy/` 目录包含私钥，不要分享给他人

---

## 🆚 对比：简单代理 vs HTTPS代理

| 特性 | proxy_sniffer.py | start_https_proxy.py |
|------|------------------|---------------------|
| HTTP 抓包 | ✅ | ✅ |
| HTTPS 解密 | ❌ | ✅ |
| 需要安装证书 | ❌ | ✅ 必须 |
| 捕获小程序文件 | ❌ 无法 | ✅ 完全支持 |
| 安装依赖 | requests | mitmproxy (较大) |
| 难度 | ⭐ 简单 | ⭐⭐ 中等 |

---

## 📋 完整流程检查清单

- [ ] 运行 `install_https.bat` 安装 mitmproxy
- [ ] 运行 `python start_https_proxy.py` 启动代理
- [ ] 记录显示的 IP 地址（如 192.168.1.100）
- [ ] 手机连接到与电脑相同的 WiFi
- [ ] 手机配置代理：服务器=电脑IP，端口=8888
- [ ] 手机浏览器访问 `http://mitm.it`
- [ ] 下载并安装对应系统的证书
- [ ] Android: 检查"信任的凭据-用户"中有 mitmproxy
- [ ] iOS: 在"证书信任设置"中启用 mitmproxy
- [ ] 手机浏览器访问 `https://www.baidu.com` 测试
- [ ] 电脑终端显示 HTTPS 请求（证明解密成功）
- [ ] 打开微信小程序，触发文件下载
- [ ] 电脑终端显示捕获到文件
- [ ] 停止代理，运行 `python file_downloader.py` 下载

---

## 🎓 原理说明

### 中间人代理（MITM）工作原理

1. **拦截连接**: 手机连接到代理服务器，而不是直接连接目标网站
2. **伪造证书**: 代理用自己的证书与手机通信
3. **解密内容**: 因为手机信任代理的证书，可以解密 HTTPS
4. **记录数据**: 代理记录请求和响应
5. **转发请求**: 代理用真实证书连接到目标网站
6. **返回响应**: 将响应加密后返回给手机

### 为什么需要安装证书

HTTPS 的安全性依赖于证书验证。如果不安装 mitmproxy 的证书：
- 手机会检测到证书不匹配
- 浏览器显示"连接不安全"
- 小程序拒绝连接

安装证书后，手机信任 mitmproxy，允许它解密流量。

---

## 📚 参考资料

- mitmproxy 官方文档: https://docs.mitmproxy.org/
- Android 证书配置: https://developer.android.com/training/articles/security-config
- iOS 证书信任: https://support.apple.com/zh-cn/HT204477

---

## 💬 需要帮助？

如果遇到问题，请提供：
1. 操作系统版本（Windows/macOS/Linux）
2. 手机型号和系统版本
3. 错误信息截图
4. `python start_https_proxy.py` 的完整输出

祝您抓包顺利！🎉
