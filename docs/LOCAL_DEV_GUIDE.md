# How to Test `sentry-dingtalk-notify` Locally

For local development with Self-Hosted Sentry (Docker), the recommended approach is to mount the source code into the running containers. This allows you to edit code and see changes (after a restart) without rebuilding images.

## Prerequisites

To keep commands clean, please define these variables in your terminal first:

```bash
# 1. Your Sentry installation folder (where docker-compose.yml is)
export SENTRY_PATH="/Users/yourname/self-hosted"

# 2. This plugin's source code folder
export PLUGIN_PATH="/Users/yourname/projects/sentry-dingtalk-notify"
```

## Method: Direct Copy (Recommended)

Since `docker-compose` mounting can be tricky with Sentry's strict configuration, we recommend directly copying the plugin code into the running containers.

### 1. Copy Plugin Code

Run these commands from the `sentry-notify` project root:

```bash
# Copy to Web container
docker cp $PLUGIN_PATH $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q web):/usr/src/sentry/

# Copy to Worker container
docker cp $PLUGIN_PATH $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q taskworker):/usr/src/sentry/
```

### 2. Install Plugin

```bash
# Install in Web container
docker exec $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q web) pip install -e /usr/src/sentry/sentry-dingtalk-notify

# Install in Worker container
docker exec $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q taskworker) pip install -e /usr/src/sentry/sentry-dingtalk-notify
```

### 3. Restart Sentry Services

```bash
cd $SENTRY_PATH
docker-compose restart web taskworker
```

## Troubleshooting

### 1. Plugin Not Visible

If the plugin doesn't appear in **Integrations** or the configuration form is empty:

*   **Check logs**:
    ```bash
    cd $SENTRY_PATH
    docker-compose logs -f --tail=100 web
    ```
*   Look for `ImportError` or `AppRegistryNotReady`.
*   Ensure `setup.py` uses `dingtalk_notify` as the entry point name to avoid conflicts with legacy built-ins.

### 2. Automatic Notifications Not working

If "Test Plugin" works but real errors don't trigger notifications:

1.  **Check Alert Rules**:
    *   Sentry's default rule is often **"A new issue is created"**. This triggers ONLY ONCE per issue.
    *   For testing, change the rule to **"An event is captured"** or remove the "New issue" condition.
2.  **Check Logs**:
    *   Look for `DingTalk notify_users called` in the web logs.
    *   If you don't see it, Sentry's rule engine didn't select the plugin.

### 3. Service "worker" vs "taskworker"

Your Sentry installation uses `taskworker` as the service name. Standard installations might use `worker`. Use `docker-compose ps` to confirm.

## Quick Reference Commands

### Scenario 1: Only Code Changes (Fast Iteration)

If you only modified `plugin.py` or logic files, you do NOT need to re-run pip. Just copy and restart.

```bash
# 1. Copy Code
docker cp $PLUGIN_PATH $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q web):/usr/src/sentry/
docker cp $PLUGIN_PATH $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q taskworker):/usr/src/sentry/

# 2. Restart Services
cd $SENTRY_PATH
docker-compose restart web taskworker

# 3. Check Logs
docker-compose logs -f --tail=100 web
```

### Scenario 2: Metadata/Setup Changes

If you modified `setup.py` (e.g. changing Entry Points or Version), you MUST re-run `pip install`.

```bash
```bash
# 1. Copy Code
docker cp $PLUGIN_PATH $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q web):/usr/src/sentry/
docker cp $PLUGIN_PATH $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q taskworker):/usr/src/sentry/

# 2. Re-install (Registers new Entry Points)
docker exec $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q web) pip install -e /usr/src/sentry/sentry-dingtalk-notify
docker exec $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q taskworker) pip install -e /usr/src/sentry/sentry-dingtalk-notify

# 3. Check Logs
docker-compose logs -f --tail=100 web
```
```

## 🚀 Publishing Guide

This project includes automated publishing workflows.

### 1. Publish to TestPyPI
You can manually publish a test version using the script:
```bash
./sentry-dingtalk-notify/scripts/publish_test.sh
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

## DingTalk Security Settings

DingTalk requires at least one security setting. Here is how to configure them with this plugin:

### 1. Custom Keyword (Recommended)
*   **What it is**: The message must contain a specific word.
*   **How to use**: Set a keyword (e.g., `Sentry`) in DingTalk. Then, enter the **same keyword** in the plugin's "Custom Keyword" field. The plugin will automatically add it to the message title.

### 2. Secret / Sign (Recommended)
*   **What it is**: Validates the request signature using a shared secret.
*   **How to use**: Copy the `SEC...` string from DingTalk to the plugin's "Secret" field.
*   **Note**: If you have multiple bots and some don't use secrets, use `-` as a placeholder for those lines.

### 3. IP Address (IP Whitelist)
*   **What it is**: Only allows requests from specific IPs.
*   **How to use**: This requires **no changes** in the plugin.
    *   **Local Dev**: Add your current public IP (search "what is my ip").
    *   **Server**: Add your server's static public IP.
*   **Warning**: Do not use this if your IP changes dynamically (e.g., home wifi), or messages will fail to send.
