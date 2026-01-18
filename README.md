<div align="center">

# Sentry DingTalk Notify

A Sentry extension to post notifications to DingTalk (钉钉) robot.

[![PyPI Version](https://img.shields.io/pypi/v/sentry-dingtalk-notify.svg?style=flat-square)](https://pypi.org/project/sentry-dingtalk-notify)
[![PyPI Downloads](https://img.shields.io/pypi/dm/sentry-dingtalk-notify.svg?style=flat-square)](https://pypi.org/project/sentry-dingtalk-notify)
[![Python Versions](https://img.shields.io/pypi/pyversions/sentry-dingtalk-notify.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/sentry-dingtalk-notify)
[![License](https://img.shields.io/github/license/lanxuexing/sentry-dingtalk-notify.svg?style=flat-square)](https://github.com/lanxuexing/sentry-dingtalk-notify/blob/main/LICENSE)

</div>

**中文** | [English](./README_EN.md)

Sentry 集成钉钉机器人通知插件 (Sentry DingTalk Integration)

## ✨ 特性 (Features)

- **异常通知**: 发送 Sentry 捕获的异常通知到钉钉群。
- **关键字过滤**:
    - **自定义关键字**: 为每个 Sentry 项目设置自定义前缀，便于在钉钉中快速识别（也用于满足钉钉机器人的安全设置要求）。
    - **包含/排除规则**: 支持配置“包含关键字”和“排除关键字”，精确控制哪些报错需要发送通知。
- **环境配置**: 支持通过环境变量预配置缺省值。

## 📦 安装 (Installation)

### 1. 使用 `pip` 安装
```bash
pip install sentry-dingtalk-notify
```

### 2. 通过 `requirements.txt` 安装 (推荐 Docker/On-Premise)
在你的 Sentry 自定义构建目录 (`onpremise/sentry/`) 下的 `requirements.txt` 中添加：
```text
sentry-dingtalk-notify
```
然后重新构建并启动 Sentry:
```bash
./install.sh
docker-compose up -d
```

## ⚙️ 配置 (Configuration)

### 1. 全局环境变量 (可选)
可以在 `sentry.conf.py` 或环境变量中设置默认值：
- `DINGTALK_WEBHOOK`: 默认钉钉 Webhook URL
- `DINGTALK_CUSTOM_KEYWORD`: 默认自定义前缀
- `DINGTALK_INCLUDE_KEYWORDS`: 默认包含关键字 (逗号分隔)
- `DINGTALK_EXCLUDE_KEYWORDS`: 默认排除关键字 (逗号分隔)

### 2. 项目级配置 (Project Settings)
进入 **Sentry 项目面板 -> Settings -> Integrations -> DingTalk Notify**：

| 选项 | 说明 | 示例 |
| --- | --- | --- |
| **Webhook** | [必填] 钉钉机器人的 Webhook 地址 | `https://oapi.dingtalk.com/robot/send?access_token=xxx` |
| **Custom Keyword** | [选填] 自定义前缀。如果钉钉机器人设置了关键字安全策略，此处必须包含该关键字。 | `[Sentry Alert]` |
| **Include Keywords** | [选填] **包含关键字**。如果设置，只有错误标题或内容中**包含**其中任意一个关键字时，才会发送通知。(逗号分隔) | `Critical, Production` |
| **Exclude Keywords** | [选填] **排除关键字**。如果错误标题或内容中**包含**其中任意一个关键字，将**不会**发送通知。(逗号分隔) | `Timeout, 404 Not Found` |

> **注意**: **排除关键字**的优先级高于**包含关键字**。

## 🛠 开发与测试 (Development & Testing)

### 运行单元测试
```bash
pip install -r requirements-test.txt  # (如果需要)
python3 tests/test_plugin_logic.py
```

### 手动发送真实通知测试
编辑 `tests/manual_test_dingtalk.py`，填入你的真实 Webhook URL，然后运行：
```bash
python3 tests/manual_test_dingtalk.py
```

## 🚀 发布指南 (Publishing)

本项目包含自动化发布流程。

### 1. 发布到 TestPyPI (测试环境)
你可以使用脚本手动发布测试版本：
```bash
./scripts/publish_test.sh
```
或者在 GitHub Actions 中手动触发 `Upload Python Package to TestPyPI` workflow。

### 2. 发布到 PyPI (正式环境 - Trusted Publishing)
**自动化**: 当你在 GitHub 上创建一个新的 Release 时，GitHub Actions 会自动构建并发布到 PyPI。

**配置 Trusted Publishing (推荐)**:
这是目前最安全的方式（类似 npm 的 OIDC），无需在 GitHub 保存长效 Token。

1.  登录 [PyPI](https://pypi.org/manage/account/publishing/)。
2.  进入 **Publishing** 设置页面。
3.  添加一个新的 **Trusted Publisher**。
4.  填写你的 GitHub 仓库信息：
    - **Owner**: `你的GitHub用户名`
    - **Repository**: `sentry-dingtalk-notify`
    - **Workflow name**: `publish.yml`
    - **Environment**: (留空)
5.  提交代码并打 tag，或在 GitHub Release 页面发布新版本，Actions 将自动鉴权并发布。
