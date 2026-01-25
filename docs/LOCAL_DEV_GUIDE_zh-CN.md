# 本地测试与开发指南 (Self-Hosted Sentry)

如果您使用 Docker 部署了 Self-Hosted Sentry，可以通过挂载源码的方式在本地进行测试和开发。

## 准备工作 (Prerequisites)

为了避免路径过长影响阅读，请先在终端设置两个变量（请替换为您的实际路径）：

```bash
# 1. Sentry 部署目录 (包含 docker-compose.yml 的目录)
export SENTRY_PATH="/Users/yourname/self-hosted"

# 2. 本插件源码目录
export PLUGIN_PATH="/Users/yourname/projects/sentry-dingtalk-notify"
```

## 方法一：挂载源码（推荐用于开发）

> **注意**：如果遇到 `docker-compose` 报错，请跳过此方法。

在 `$SENTRY_PATH` 目录下创建 `docker-compose.override.yml`：


```yaml
services:
  web:
    volumes:
      - $PLUGIN_PATH:/usr/src/sentry/sentry-dingtalk-notify
  worker:
    volumes:
      - $PLUGIN_PATH:/usr/src/sentry/sentry-dingtalk-notify
```

## 第二步：应用更改

在 `$SENTRY_PATH` 目录下运行：

```bash
docker-compose up -d
```

## 第三步：安装插件

分别进入容器安装插件（以可编辑模式 `-e` 安装）：

```bash
# Web 容器
docker-compose exec web pip install -e /usr/src/sentry/sentry-dingtalk-notify

# Worker 容器
docker-compose exec worker pip install -e /usr/src/sentry/sentry-dingtalk-notify
```

## 第四步：重启服务

```bash
docker-compose restart web worker
```

## 第五步：验证

1. 登录 Sentry Web 界面。
2. 进入 **项目设置 > Integrations**。
3. 启用并配置 **DingTalk** 插件进行测试。

## 修改代码

由于使用了挂载和 `-e` 模式，只需重启服务即可生效：

```bash
docker-compose restart web worker
```

## 方法二：直接复制（推荐用于快速测试）

如果方法一即 `docker-compose.override.yml` 遇到兼容性问题，或者出现 `invalid compose project` 错误，请删除 override 文件并尝试此方法。

### 0. 清理环境（如果运行过方法一）
如果不受影响可跳过。如果之前创建了 override 文件导致报错，请先删除：
```bash
rm docker-compose.override.yml
docker-compose up -d
```

### 1. 复制插件代码

在 `sentry-notify` 项目根目录下运行：

```bash
# 1. 复制插件到容器
# 复制到 Web 容器
docker cp $PLUGIN_PATH $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q web):/usr/src/sentry/

# 复制到 Worker 容器
docker cp $PLUGIN_PATH $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q taskworker):/usr/src/sentry/
```



### 2. 安装插件

```bash
# Web 容器安装
docker exec $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q web) pip install -e /usr/src/sentry/sentry-dingtalk-notify

# Worker 容器安装
docker exec $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q taskworker) pip install -e /usr/src/sentry/sentry-dingtalk-notify
```

### 3. 重启服务

```bash
cd $SENTRY_PATH
docker-compose restart web taskworker
```

## 故障排查 (Troubleshooting)

### 1. 插件未显示在 Integrations 列表

如果重启后插件未显示，或者点击配置没有反应，请检查 Web 容器日志：

```bash
cd $SENTRY_PATH
docker-compose logs -f --tail=100 web
```

*   搜索 `DingTalk` 关键字查看是否有报错（如 `ImportError`, `AppRegistryNotReady` 等）。
*   确保 `setup.py` 中的 `entry_points` 名称不与官方旧版冲突（推荐使用 `dingtalk_notify`）。

### 2. 无法发送消息（自动通知失效）

如果手动点击 "Test Plugin" 可以发送消息，但真实报错时不发送：

1.  **检查 Alert Rules (告警规则)**：
    *   Sentry 默认规则可能是 "A new issue is created"（创建新问题时）。这会导致同一个错误只触发一次。
    *   测试时建议改为 "An event is captured"（捕获任意事件）或移除 "New issue" 条件。
2.  **检查日志**：
    *   查看日志中是否有 `DingTalk notify_users called`。如果没有，说明 Sentry 根本没有触发插件逻辑（通常是规则配置问题）。
    *   如有 `should_notify` 日志，检查返回是 True 还是 False。

### 3. Service "worker" not found

在某些 Sentry 版本中，后台 Worker 服务名为 `taskworker` 而不是 `worker`。
可以通过 `docker-compose ps` 查看实际的服务名称。本指南中使用的是 `taskworker`。

## 常用命令速查 (Quick Reference)

### 场景一：只修改了 Python 代码 (快速迭代)

如果只修改了 `plugin.py` 等逻辑代码，无需重新安装 `pip`，只需复制文件并重启：

```bash
# 1. 复制最新代码
docker cp $PLUGIN_PATH $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q web):/usr/src/sentry/
docker cp $PLUGIN_PATH $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q taskworker):/usr/src/sentry/

# 2. 重启服务
cd $SENTRY_PATH
docker-compose restart web taskworker

# 3. 查看日志
docker-compose logs -f --tail=100 web
```

## 钉钉安全设置说明 (Security Settings)

钉钉机器人提供了三种安全设置，建议根据您的环境选择：

### 1. 自定义关键词 (Custom Keyword) - **推荐**
*   **说明**：消息内容必须包含至少一个关键词。
*   **插件支持**：在本插件配置中填写该关键词，插件会自动将其拼接到消息标题中。
*   **配置**：在钉钉后台设置如 `Sentry`，在插件配置 "Custom Keyword" 中填入 `Sentry`。

### 2. 加签 (Secret) - **推荐**
*   **说明**：使用 HmacSHA256 算法验证签名。
*   **插件支持**：在本插件配置中填入以 `SEC` 开头的字符串。
*   **注意**：如果是多个机器人，且有的需要加签有的不需要，请在不需要的行填入 `-` 占位。

### 3. IP 地址段 (IP Whitelist)
*   **说明**：只允许特定 IP 发起请求。
*   **插件支持**：此功能**无需插件代码支持**，由网络层控制。
*   **配置**：
    *   **本地开发**：填写您公司或家庭网络的公网出口 IP（百度搜索 "IP"）。
    *   **服务器部署**：填写服务器的公网 IP。
*   **注意**：如果您的 IP 是动态的，不建议使用此选项，否则 IP 变动后会导致发送失败。

### 场景二：修改了配置或元数据 (Setup.py)

如果修改了 `setup.py` (如更改 Entry Point、版本号)，必须重新执行 `pip install`：

```bash
# 1. 复制代码
docker cp $PLUGIN_PATH $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q web):/usr/src/sentry/
docker cp $PLUGIN_PATH $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q taskworker):/usr/src/sentry/

# 2. 重新安装 (注册 Entry Points)
docker exec $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q web) pip install -e /usr/src/sentry/sentry-dingtalk-notify
docker exec $(docker-compose -f $SENTRY_PATH/docker-compose.yml ps -q taskworker) pip install -e /usr/src/sentry/sentry-dingtalk-notify

# 3. 重启服务
cd $SENTRY_PATH
docker-compose restart web taskworker
```

## 🚀 发布指南 (Publishing)

本项目包含自动化发布流程。

### 1. 发布到 TestPyPI (测试环境)
你可以使用脚本手动发布测试版本：
```bash
./sentry-dingtalk-notify/scripts/publish_test.sh
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
