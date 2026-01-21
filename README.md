# FLZT 自动签到脚本

这是一个专为青龙面板设计的 FLZT 自动签到脚本，支持签到、流量转换和Bark推送通知。

## 功能特点

- ✅ 自动登录和签到
- ✅ 支持流量转换功能
- ✅ Bark 推送通知
- ✅ 青龙面板集成
- ✅ 多账号支持（通过环境变量）

## 文件结构

```
├── main.py          # 主入口文件
├── flzt.py          # 主要业务逻辑
├── config.py        # 配置文件（环境变量读取）
├── notification.py  # 通知推送模块
└── README.md        # 说明文档
```

## 安装与配置

### 1. 青龙面板配置

1. 登录青龙面板
2. 进入「脚本管理」页面
3. 创建一个新目录，例如 `flzt_sign`
4. 将以下文件上传到该目录：
  - `main.py`
  - `flzt.py`
  - `config.py`
  - `notification.py`

### 2. 环境变量设置

在青龙面板中，进入「环境变量」页面，添加以下变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `FLZT_BASE_URL` | FLZT 站点基础 URL | `https://your-flzt-site.com` |
| `FLZT_EMAIL` | 登录邮箱 | `user@example.com` |
| `FLZT_PASSWORD` | 登录密码 | `your_password` |
| `BARK_PUSH` | Bark 推送密钥（可选） | `your_bark_key` |

### 3. 配置参数说明

在 `config.py` 中还可以调整以下参数：

```python
# 流量转换配置
CONVERT_TRAFFIC = True  # 是否转换流量，True/False
CONVERT_AMOUNT = 1000   # 转换多少流量，0表示全部转换，>0表示转换指定MB数
```

### 4. 安装依赖

在青龙面板的「依赖管理」中，添加 Python 依赖：
- `requests`

## 使用方法

### 1. 创建定时任务

在青龙面板中创建定时任务：
- 命令：`task /ql/scripts/xxx/main.py`
- 定时规则（示例）：`0 9 * * *`（每天上午9点执行）
- 名称：`FLZT自动签到`

### 2. 手动执行

也可以在青龙面板中手动执行脚本：
1. 进入「脚本管理」页面
2. 找到 `xxx` 目录
3. 点击 `main.py` 右侧的「运行」按钮

### 3. 查看日志

执行后可以在青龙面板的「日志」中查看执行结果：
- 登录是否成功
- 签到状态
- 流量转换结果
- 推送通知状态

## 推送通知配置

### Bark 推送（推荐）

1. 在手机上下载安装 Bark App
2. 获取推送密钥
3. 在青龙环境变量中设置 `BARK_PUSH` 变量

### 青龙内置推送

脚本也支持青龙面板的内置推送机制，如果配置了青龙的推送渠道（如企业微信、Telegram等），会自动使用。

## 多账号支持

如果需要支持多账号签到，可以通过以下方式之一：

### 方式一：青龙面板多账号环境变量

可以为每个账号设置不同的环境变量前缀：

```bash
FLZT_BASE_URL_1=https://site1.com
FLZT_EMAIL_1=user1@example.com
FLZT_PASSWORD_1=pass1

FLZT_BASE_URL_2=https://site2.com
FLZT_EMAIL_2=user2@example.com
FLZT_PASSWORD_2=pass2
```

然后修改 `main.py` 来读取多个账号。

### 方式二：修改脚本支持列表

在 `main.py` 中修改为遍历多个账号：

```python
accounts = [
    {"email": "user1@example.com", "password": "pass1"},
    {"email": "user2@example.com", "password": "pass2"},
]

for acc in accounts:
    flzt = FLZT(email=acc["email"], password=acc["password"])
    flzt.run()
```

## 免责声明

1. 本脚本仅供学习和交流使用
2. 请遵守相关网站的服务条款
3. 过度使用可能导致账号被封禁
4. 作者不对使用本脚本造成的任何问题负责