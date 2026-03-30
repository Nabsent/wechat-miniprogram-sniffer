# Windows 微信客户端抓包指南

## 快速配置

### 方法一：使用自动配置脚本（推荐）

```cmd
python setup_windows_proxy.py
```

按提示操作：
1. 选择 3 - 检查证书（确认证书存在）
2. 选择 4 - 打开证书管理器，手动导入证书
3. 选择 1 - 启用系统代理
4. 启动微信客户端
5. 使用完毕后选择 2 - 禁用系统代理

### 方法二：手动配置

#### 1. 安装证书

**位置**：`C:\Users\你的用户名\.mitmproxy\mitmproxy-ca-cert.cer`

**步骤**：
1. 按 `Win + R`，输入 `certmgr.msc`
2. 右键"受信任的根证书颁发机构" → 证书
3. 右键 → 所有任务 → 导入
4. 选择上述证书文件
5. 完成导入

#### 2. 配置系统代理

**Windows 10/11:**
- 设置 → 网络和 Internet → 代理
- 手动设置代理 → 开启
- 地址：`127.0.0.1`，端口：`8888`

**或使用命令行：**
```cmd
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 1 /f
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyServer /d "127.0.0.1:8888" /f
```

#### 3. 启动微信

正常启动微信客户端即可。

---

## 常见问题

### Q1: 微信无法连接网络

**原因**：微信使用证书绑定，不信任自签名证书。

**解决方案 A: 使用 Proxifier（推荐）**

Proxifier 可以强制微信走代理并绕过部分证书检查：

1. 下载 Proxifier: https://www.proxifier.com/
2. 配置代理服务器：127.0.0.1:8888
3. 添加规则：WeChat.exe → 走代理
4. 启动微信

**解决方案 B: 降级微信版本**

较老的微信版本可能没有严格的证书校验。

**解决方案 C: 使用 Frida Hook（高级）**

绕过微信的 SSL Pinning，需要技术背景。

### Q2: 能看到流量但无法解密

部分请求可能使用了双重加密或自定义协议。

### Q3: 浏览器正常但微信不行

说明证书或代理配置有问题：
1. 确认证书安装到"受信任的根证书颁发机构"
2. 检查微信是否读取了系统代理设置
3. 尝试使用 Proxifier 强制走代理

### Q4: 使用完忘记关闭代理

所有程序都无法上网，运行：
```cmd
python setup_windows_proxy.py
# 选择 2 - 禁用系统代理
```

或手动：
```cmd
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings" /v ProxyEnable /t REG_DWORD /d 0 /f
```

---

## 推荐方案对比

| 方案 | 难度 | 成功率 | 说明 |
|------|------|--------|------|
| **手机抓包** | ⭐ 简单 | 95% | 最推荐 |
| **系统代理** | ⭐⭐ 中等 | 50% | 可能被证书绑定阻止 |
| **Proxifier** | ⭐⭐ 中等 | 70% | 付费软件，效果较好 |
| **Frida Hook** | ⭐⭐⭐ 困难 | 90% | 需要技术背景 |

---

## 推荐：使用手机抓包

**电脑微信比手机微信更难抓包**，建议：

1. **用手机小程序**（如果可以）
   - 按原教程配置手机代理即可
   - 成功率最高

2. **用网页版微信**
   - 部分功能支持网页版
   - 浏览器代理配置更简单

3. **用模拟器**
   - 安装 Android 模拟器（如夜神、雷电）
   - 在模拟器中安装微信
   - 模拟器配置代理和证书

---

## 使用后恢复

**务必禁用代理，否则无法上网：**

```cmd
python setup_windows_proxy.py
# 选择 2 - 禁用系统代理
```

---

## 总结

- ✅ **理论上可行**：Windows 微信会读取系统代理
- ⚠️ **实际困难**：证书绑定可能阻止连接
- 🎯 **推荐方案**：优先使用手机小程序或模拟器
- 🔧 **高级方案**：使用 Proxifier 或 Frida Hook
