import sys
import os
import json
from unittest.mock import MagicMock

# 1. Mock Sentry and Django dependencies BEFORE importing the plugin
# We do NOT mock 'requests' because we want to initiate real network calls.

# Mock base classes to avoid metaclass conflicts
class MockNotificationPlugin:
    pass

class MockCorePluginMixin:
    pass

# Mocking the module structure
sys.modules['sentry'] = MagicMock()
sys.modules['sentry.plugins'] = MagicMock()
sys.modules['sentry.plugins.bases'] = MagicMock()

notify_mock = MagicMock()
notify_mock.NotificationPlugin = MockNotificationPlugin
sys.modules['sentry.plugins.bases.notify'] = notify_mock
# Also ensure sentry.plugins.bases.notify is accessible via the parent
sys.modules['sentry.plugins.bases'].notify = notify_mock

sys.modules['sentry.utils'] = MagicMock()
# sentry.utils.json is used module-wise, so we mock it but point dumps to real json.dumps
sys.modules['sentry.utils'].json = MagicMock()
sys.modules['sentry.utils'].json.dumps = json.dumps 

sys.modules['sentry.integrations'] = MagicMock()
sys.modules['django'] = MagicMock()
sys.modules['django.conf'] = MagicMock()
sys.modules['sentry_plugins'] = MagicMock()

# Mock sentry_plugins.base
sentry_plugins_base_mock = MagicMock()
sentry_plugins_base_mock.CorePluginMixin = MockCorePluginMixin
sys.modules['sentry_plugins.base'] = sentry_plugins_base_mock

# Ensure we can find the project source
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# NOW import the plugin
try:
    from sentry_dingtalk_notify.plugin import DingTalkNotifyPlugin
except ImportError as e:
    print(f"Error importing plugin: {e}")
    print("Ensure you are in the project root and requirements are met.")
    sys.exit(1)

def send_test_message(webhook_url):
    if not webhook_url or "dingtalk.com" not in webhook_url:
        print("Error: Invalid or missing Webhook URL.")
        print("Please edit this script and set TEST_WEBHOOK_URL.")
        return

    print(f"Attempting to send test message to: {webhook_url}")

    plugin = DingTalkNotifyPlugin()
    
    # Mock get_option to return our config
    def mock_get_option(key, project):
        if key == "webhook":
            return webhook_url
        if key == "custom_keyword":
            return "[Test Message]"
        if key == "include_keywords":
            return None
        if key == "exclude_keywords":
            return None
        return None
    
    plugin.get_option = mock_get_option

    # Create dummy Group and Project objects
    group = MagicMock()
    group.title = "Test Error: Hello from the Manual Test Script"
    group.message = "This is a test notification generated manually to verify DingTalk integration."
    group.project.name = "Manual Test Project"
    group.get_absolute_url.return_value = "http://localhost/mock-issue-link"

    project = MagicMock()

    try:
        # We need to ensure requests is installed in the environment running this script
        try:
            import requests
        except ImportError:
            print("Error: 'requests' module is missing. Please run: pip install requests")
            return

        plugin._post(group, project)
        print("----------------------------------------------------------------")
        print("✅ Function _post execution completed.")
        print("Check your DingTalk group for the message.")
        print("----------------------------------------------------------------")
    except Exception as e:
        print(f"❌ An error occurred during execution: {e}")

if __name__ == "__main__":
    # --- CONFIGURATION ---
    # Replace the empty string below with your real DingTalk Webhook URL
    TEST_WEBHOOK_URL = "" 
    # ---------------------
    
    if not TEST_WEBHOOK_URL:
        print("Please open this file (tests/manual_test_dingtalk.py) and fill in TEST_WEBHOOK_URL with your real webhook.")
    else:
        send_test_message(TEST_WEBHOOK_URL)
