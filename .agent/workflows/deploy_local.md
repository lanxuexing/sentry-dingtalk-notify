---
description: Deploy sentry-dingtalk-notify source code to local Sentry containers (Copy -> Install -> Restart)
---

Prerequisites:
- Ensure `SENTRY_PATH` environment variable is set to your Sentry self-hosted directory.
- Ensure `PLUGIN_PATH` environment variable is set to this project's directory.
- If not set, please run: `export SENTRY_PATH=/path/to/self-hosted` and `export PLUGIN_PATH=$(pwd)`

1. Copy plugin to Web container
   ```bash
   docker cp "$PLUGIN_PATH" $(docker-compose -f "$SENTRY_PATH/docker-compose.yml" ps -q web):/usr/src/sentry/
   ```

2. Copy plugin to Worker container
   ```bash
   docker cp "$PLUGIN_PATH" $(docker-compose -f "$SENTRY_PATH/docker-compose.yml" ps -q taskworker):/usr/src/sentry/
   # Note: If service is named 'worker', use 'worker' instead of 'taskworker'
   ```

3. Re-install plugin (to register entry points)
   ```bash
   docker exec $(docker-compose -f "$SENTRY_PATH/docker-compose.yml" ps -q web) pip install -e /usr/src/sentry/sentry-dingtalk-notify
   docker exec $(docker-compose -f "$SENTRY_PATH/docker-compose.yml" ps -q taskworker) pip install -e /usr/src/sentry/sentry-dingtalk-notify
   ```

4. Restart Sentry services
   ```bash
   cd "$SENTRY_PATH"
   docker-compose restart web taskworker
   ```
