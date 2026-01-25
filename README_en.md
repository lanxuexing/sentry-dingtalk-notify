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
  <strong>English</strong> | <a href="https://github.com/lanxuexing/sentry-dingtalk-notify/blob/main/README.md">简体中文</a>
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

## ✨ Features

- **📝 Markdown Support**: Sends rich text messages with Project, Level, Environment, and clickable links.
- **🤖 Multi-Robot**: Configure multiple DingTalk robots to notify different groups simultaneously.
- **🔒 Security**: Full support for DingTalk's **SEC (Signature)** and **Keyword** security settings.
- **📱 @Mentions**: Automatically @ specific users (via mobile number) in the group chat.
- **⚡ High Performance**: Lightweight and non-blocking integration.

## 🚀 Installation

Choose the method that fits your environment:

### Method 1: Production (Recommended)
For Sentry Self-Hosted users, this is the official way to add plugins. It ensures the plugin persists across container rebuilds.

1.  In your Sentry `self-hosted/` directory, create or edit `sentry/enhance-image.sh`.
2.  Add the following line:
    ```bash
    #!/bin/bash
    pip install sentry-dingtalk-notify
    ```
    *(Ensure it is executable: `chmod +x sentry/enhance-image.sh`)*
3.  Rebuild and restart:
    ```bash
    ./install.sh
    docker-compose up -d
    ```

### Method 2: Temporary / Fast Test
Quickly install without rebuilding images. **Note: The plugin will disappear if containers are destroyed.**

1.  Install inside containers:
    ```bash
    docker-compose exec web pip install sentry-dingtalk-notify
    docker-compose exec worker pip install sentry-dingtalk-notify
    ```
2.  Restart services:
    ```bash
    docker-compose restart web worker
    ```

## ⚙️ Configuration Guide

Go to **Sentry > Project Settings > Legacy Integrations > DingTalk**.

### 1. Access Token (Required)
The access token for your DingTalk robot. You can find this in the Webhook URL: `https://oapi.dingtalk.com/robot/send?access_token=YOUR_TOKEN`.

*   **Format**: One token per line.
    ```text
    80dc91e4d2...
    1284401411...
    ```

### 2. Secret / Sign (Recommended)
The secret string (starting with `SEC...`) found in the "Security Settings" of your DingTalk robot.

*   **Format**: One secret per line, **strictly corresponding** to the Access Tokens above.
*   **Placeholder**: If a robot does **not** use a secret, use a single dash `-` as a placeholder for that line.

    **Example**:
    ```text
    SEC3390d51...    <-- Secret for Token 1
    -                <-- No secret for Token 2
    SEC8888888...    <-- Secret for Token 3
    ```

### 3. Custom Keyword (Optional)
If your robot uses "Keyword" security verification.
*   **How it works**: The plugin will automatically append this keyword to the message title (e.g., `【Sentry】 Error Title`).
*   **Setup**: Enter the same keyword you set in DingTalk (e.g., `Sentry`).

### 4. At Mobiles (Optional)
Comma-separated list of mobile numbers to @ in the group chat.
*   **Example**: `13800000000,13900000000`

---

## ⚠️ Important: Why am I not receiving notifications?

If "Test Plugin" works but real errors are silent, checking your **Alert Rules** is the #1 solution.

### The "New Issue" Trap
By default, Sentry's alert rule is often set to:
> **WHEN** `A new issue is created`

This means Sentry only notifies you the **very first time** a specific error occurs. If the same error happens again, it is ignored (because it's not "new").

### Recommended Alert Rule
For reliable testing and monitoring, change your Alert Rule to:

1.  **WHEN**: `An event is captured` (Triggers on every error)
2.  **IF**: `The event's level is equal to or greater than error`
3.  **Action Interval**: Set to `5 minutes` (or limit via "Digests") to avoid spam.

### ⚡️ Quick Check
Don't want to change rules?

1.  **Method 1: Curl (Recommended - 100% Reliable)**
    *   Send a fake error directly to Sentry API:
    ```bash
    # Replace YOUR_KEY, PROJECT_ID, and Domain
    curl https://sentry.your-domain.com/api/PROJECT_ID/store/ \
      -H "X-Sentry-Auth: Sentry sentry_version=7, sentry_key=YOUR_KEY, sentry_client=curl/1.0" \
      -H "Content-Type: application/json" \
      -d '{"message": "DingTalk Test '`date +%s`'", "level": "error"}'
    ```

2.  **Method 2: Browser Console**
    *   Only works if your page has Sentry SDK initialized.
    *   Run this (wrapped in setTimeout to ensure it bubbles to global handler):
        ```javascript
        Sentry.captureException(new Error("DingTalk Test Error " + new Date().getTime()));
        ```

## 🛠 Troubleshooting

*   **Plugin not visible?** Check `docker-compose logs web`. Ensure `setup.py` entry points are correct.
*   **Signature Mismatch?** Ensure your Sentry server time is synchronized. The signature relies on `timestamp`.
*   **Message Rejected?** Check if your "Custom Keyword" matches what is configured in DingTalk.

## 🤝 Contributing

Pull requests are welcome! Check out [`docs/LOCAL_DEV_GUIDE.md`](docs/LOCAL_DEV_GUIDE.md) for how to develop locally.


