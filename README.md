<div align="center">

# Sentry DingTalk Notify

A Sentry extension to post notifications to DingTalk (钉钉) robot.

![DingTalk](https://img.shields.io/badge/DingTalk-007FFF?style=flat-square&logo=dingtalk&logoColor=white)
![Sentry](https://img.shields.io/badge/Sentry-362D59?style=flat-square&logo=sentry&logoColor=white)
[![PyPI Version](https://img.shields.io/pypi/v/sentry-dingtalk-notify.svg?style=flat-square)](https://pypi.org/project/sentry-dingtalk-notify)
[![PyPI Downloads](https://img.shields.io/pypi/dm/sentry-dingtalk-notify.svg?style=flat-square)](https://pypi.org/project/sentry-dingtalk-notify)
[![Python Versions](https://img.shields.io/pypi/pyversions/sentry-dingtalk-notify.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/sentry-dingtalk-notify)
[![License](https://img.shields.io/github/license/lanxuexing/sentry-dingtalk-notify.svg?style=flat-square)](https://github.com/lanxuexing/sentry-dingtalk-notify/blob/main/LICENSE)

<p align="center">
  <a href="https://github.com/lanxuexing/sentry-dingtalk-notify/blob/main/README_en.md">English</a> | <strong>简体中文</strong>
</p>

</div>

<br/>

> ### ValueError: Division by zero
>
> *   **📦 Project**: sentry-demo (Sentry)
> *   **🌍 Env**: prod
> *   **🚦 Level**: error
> *   **📍 Location**: `app/utils/math.js`
>
> [👉 View Issue on Sentry](#)

## ✨ 核心功能

- **📝 精美排版**: 发送包含项目、环境、报错级别、代码位置的 Markdown 消息，一目了然。
- **🤖 多机器人**: 支持同时配置多个机器人，推送到不同的群组。
- **🔒 安全验证**: 完美支持钉钉的 **加签 (SEC)** 和 **自定义关键词** 安全设置。
- **📱 强提醒**: 支持通过手机号 **@群成员**，确保重要报警不被遗漏。
- **⚡️ 简单易用**: 配置灵活，支持占位符跳过特定配置。

## 🚀 安装指南 (Installation)

针对不同的使用场景，提供两种安装方式：

### 方式一：生产环境安装 (推荐 - 永久生效)
如果您使用的是 Sentry Self-Hosted (Docker)，这是官方推荐的标准方式。插件会打包进 Docker 镜像，重启不会丢失。

1.  在 Sentry 部署目录 (`self-hosted/`) 下，找到或创建 `sentry/enhance-image.sh` 文件。
2.  添加以下内容：
    ```bash
    #!/bin/bash
    pip install sentry-dingtalk-notify
    ```
    *(注意：文件需具有可执行权限 `chmod +x sentry/enhance-image.sh`)*
3.  执行安装脚本重构镜像：
    ```bash
    ./install.sh
    docker-compose up -d
    ```

### 方式二：快速测试安装 (临时生效)
如果只想快速试用，可以使用此方式。**注意：重建容器后插件会消失。**

1.  进入容器安装：
    ```bash
    docker-compose exec web pip install sentry-dingtalk-notify
    docker-compose exec worker pip install sentry-dingtalk-notify
    ```
2.  重启服务：
    ```bash
    docker-compose restart web worker
    ```

## ⚙️ 配置手册

进入 **Sentry > Project Settings > Legacy Integrations > DingTalk**。

### 1. Access Token (必填)
钉钉机器人 Webhook URL 中的 `access_token` 参数。
*   **格式**: 每行一个 Token。
    ```text
    80dc91e4d2...
    1284401411...
    ```

### 2. Secret / 加签 (推荐)
钉钉机器人安全设置中的“加签”密钥（以 `SEC` 开头）。
*   **重要规则**: 每一行 Secret 必须与上面的 Access Token **严格对应**（第一行对第一行）。
*   **占位符**: 如果某个机器人**没有**设置加签，请务必在该行填入减号 `-` 作为占位符。

    **示例配置**:
    ```text
    SEC3390d51...    <-- 对应第 1 个 Token
    -                <-- 对应第 2 个 Token (无 Secret)
    SEC8888888...    <-- 对应第 3 个 Token
    ```

### 3. Custom Keyword / 自定义关键词 (可选)
如果您的机器人设置了“自定义关键词”过滤。
*   **原理**: 插件会自动将此关键词拼接到消息标题中（例如 `【Sentry】 错误标题`）。
*   **设置**: 填写你在钉钉后台设置的关键词即可（例如 `Sentry`）。

### 4. At Mobiles / @手机号 (可选)
需要 @ 的群成员手机号。
*   **格式**: 英文逗号分隔，例如 `13800000000,13900000000`。

---

## ⚠️ 常见问题：为什么收不到自动通知？

很多用户反馈手动 "Test Plugin" 成功，但真实报错没反应。这通常是 **Alert Rules (告警规则)** 设置的问题。

### "New Issue" 的陷阱
Sentry 默认的告警规则通常是：
> **WHEN** `A new issue is created` (当新问题创建时)

这意味着，同一个错误只有在**第一次**出现时才会发送通知。后续重复的报错会被合并，不再触发通知。

### 推荐规则设置
为了更好的测试和监控，建议将规则修改为：

1.  **WHEN**: `An event is captured` (当捕获到任意事件时)
2.  **IF**: `The event's level is equal to or greater than error` (级别 >= Error)
3.  **Action Interval**: 设置为 `5 minutes` 或 `10 minutes` (避免刷屏)

### ⚡️ 快速验证技巧
不想修改规则？

1.  **方法一：Curl 验证 (最推荐 - 100% 有效)**
    *   直接向 Sentry 发送模拟请求（无需前端项目）：
    ```bash
    # 请替换 YOUR_KEY (DSN Key) 和 PROJECT_ID
    # 注意：需替换 sentry.your-domain.com 为您的 Sentry 地址
    curl https://sentry.your-domain.com/api/PROJECT_ID/store/ \
      -H "X-Sentry-Auth: Sentry sentry_version=7, sentry_key=YOUR_KEY, sentry_client=curl/1.0" \
      -H "Content-Type: application/json" \
      -d '{"message": "DingTalk Test '`date +%s`'", "level": "error"}'
    ```

2.  **方法二：浏览器验证 (仅当页面有 Sentry SDK 时)**
    *   在控制台运行（包裹在 setTimeout 中以确保触发全局捕获）：
        ```javascript
        Sentry.captureException(new Error("DingTalk Test Error " + new Date().getTime()));
        ```

## 🛠 故障排查

*   **插件没显示？** 检查 `docker-compose logs web` 日志，确保没有安装报错。
*   **签名错误？** 钉钉签名依赖时间戳，请确保您的服务器时间与标准时间同步。
*   **消息被拒？** 检查 "Custom Keyword" 是否与钉钉后台设置一致。

## 🤝 贡献与开发

欢迎提交 PR！本地开发调试请参考 [本地开发指南](docs/LOCAL_DEV_GUIDE_zh-CN.md)。


