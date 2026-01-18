<div align="center">

# Sentry DingTalk Notify

A Sentry extension to post notifications to DingTalk (钉钉) robot.

[![PyPI Version](https://img.shields.io/pypi/v/sentry-dingtalk-notify.svg?style=flat-square)](https://pypi.org/project/sentry-dingtalk-notify)
[![PyPI Downloads](https://img.shields.io/pypi/dm/sentry-dingtalk-notify.svg?style=flat-square)](https://pypi.org/project/sentry-dingtalk-notify)
[![Python Versions](https://img.shields.io/pypi/pyversions/sentry-dingtalk-notify.svg?style=flat-square&logo=python&logoColor=white)](https://pypi.org/project/sentry-dingtalk-notify)
[![License](https://img.shields.io/github/license/lanxuexing/sentry-dingtalk-notify.svg?style=flat-square)](https://github.com/lanxuexing/sentry-dingtalk-notify/blob/main/LICENSE)

</div>

[中文](./README.md) | **English**

## ✨ Features

- **Exception Notifications**: Send notifications of exceptions captured by Sentry to DingTalk groups.
- **Keyword Filtering**:
    - **Custom Keyword**: Set a custom prefix for each Sentry project to quickly identify messages in DingTalk (also satisfies DingTalk robot security settings).
    - **Include/Exclude Rules**: Support configuring "Include Keywords" and "Exclude Keywords" to precisely control which errors trigger notifications.
- **Environment Configuration**: Support pre-configuring default values via environment variables.

## 📦 Installation

### 1. Install via `pip`
```bash
pip install sentry-dingtalk-notify
```

### 2. Install via `requirements.txt` (Recommended for Docker/On-Premise)
Add the following to `requirements.txt` in your Sentry custom build directory (`onpremise/sentry/`):
```text
sentry-dingtalk-notify
```
Then rebuild and restart Sentry:
```bash
./install.sh
docker-compose up -d
```

## ⚙️ Configuration

### 1. Global Environment Variables (Optional)
You can set defaults in `sentry.conf.py` or environment variables:
- `DINGTALK_WEBHOOK`: Default DingTalk Webhook URL
- `DINGTALK_CUSTOM_KEYWORD`: Default custom prefix
- `DINGTALK_INCLUDE_KEYWORDS`: Default include keywords (comma separated)
- `DINGTALK_EXCLUDE_KEYWORDS`: Default exclude keywords (comma separated)

### 2. Project Settings
Go to **Sentry Project Dashboard -> Settings -> Integrations -> DingTalk Notify**:

| Option | Description | Example |
| --- | --- | --- |
| **Webhook** | [Required] DingTalk Robot Webhook URL | `https://oapi.dingtalk.com/robot/send?access_token=xxx` |
| **Custom Keyword** | [Optional] Custom prefix. Required if the DingTalk robot has a keyword security policy. | `[Sentry Alert]` |
| **Include Keywords** | [Optional] **Include Keywords**. If set, notification is sent ONLY if the title or body contains at least one of these keywords (comma separated). | `Critical, Production` |
| **Exclude Keywords** | [Optional] **Exclude Keywords**. If the title or body contains ANY of these keywords, the notification will **NOT** be sent (comma separated). | `Timeout, 404 Not Found` |

> **Note**: **Exclude Keywords** take precedence over **Include Keywords**.

## 🛠 Development & Testing

### Run Unit Tests
```bash
pip install -r requirements-test.txt  # (If needed)
python3 tests/test_plugin_logic.py
```

### Manual Real Notification Test
Edit `tests/manual_test_dingtalk.py`, fill in your real Webhook URL, and run:
```bash
python3 tests/manual_test_dingtalk.py
```

## 🚀 Publishing

This project includes automated publishing workflows.

### 1. Publish to TestPyPI
You can manually publish a test version using the script:
```bash
./scripts/publish_test.sh
```
Or trigger the `Upload Python Package to TestPyPI` workflow manually in GitHub Actions.

### 2. Publish to PyPI (Production - Trusted Publishing)
**Automation**: When you create a new Release on GitHub, GitHub Actions updates PyPI automatically.

**Configure Trusted Publishing (Recommended)**:
This is the most secure method (OIDC), effectively tokenless for the repository.

1.  Login to [PyPI](https://pypi.org/manage/account/publishing/).
2.  Go to **Publishing** settings.
3.  Add a new **Trusted Publisher**.
4.  Fill in your GitHub repo info:
    - **Owner**: `your-github-username`
    - **Repository**: `sentry-dingtalk-notify`
    - **Workflow name**: `publish.yml`
    - **Environment**: (leave empty)
5.  Commit code and tag, or publish a release on GitHub. Actions will authenticate and publish.
