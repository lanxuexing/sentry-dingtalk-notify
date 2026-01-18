import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the project directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mocking base classes to avoid metaclass conflicts
class MockNotificationPlugin:
    pass

class MockCorePluginMixin:
    pass

notify_mock = MagicMock()
notify_mock.NotificationPlugin = MockNotificationPlugin
sys.modules['sentry.plugins.bases.notify'] = notify_mock
sys.modules['sentry.plugins.bases'] = MagicMock()
sys.modules['sentry.plugins.bases'].notify = notify_mock

sentry_plugins_base_mock = MagicMock()
sentry_plugins_base_mock.CorePluginMixin = MockCorePluginMixin
sys.modules['sentry_plugins.base'] = sentry_plugins_base_mock

sys.modules['sentry.utils'] = MagicMock()
sys.modules['sentry.integrations'] = MagicMock()
sys.modules['django.conf'] = MagicMock()
sys.modules['requests'] = MagicMock()
# sys.modules['requests'] = MagicMock() # This line will be replaced

# Configure six to work as expected for text_type
six_mock = MagicMock()
six_mock.text_type = str
sys.modules['six'] = six_mock

from sentry_dingtalk_notify.plugin import DingTalkNotifyPlugin

class TestDingTalkNotifyPlugin(unittest.TestCase):
    def setUp(self):
        # Manually patch the class method to avoid decorator lifecycle issues
        self.original_send_request = DingTalkNotifyPlugin.send_request
        self.mock_send_request = MagicMock()
        DingTalkNotifyPlugin.send_request = self.mock_send_request
        
        self.plugin = DingTalkNotifyPlugin()
        self.plugin.get_option = MagicMock()
        self.plugin.get_option.side_effect = self.mock_get_option
        
        self.options = {
            "webhook": "http://example.com",
            "custom_keyword": "[Sentry]",
            "include_keywords": "",
            "exclude_keywords": "",
        }

        self.group = MagicMock()
        self.group.title = "Test Error Title"
        self.group.message = "This is a test error message"
        self.group.project.name = "Test Project"
        self.group.get_absolute_url.return_value = "http://sentry.example.com/issues/123"
        
        self.project = MagicMock()

    def tearDown(self):
        # Restore the original method
        DingTalkNotifyPlugin.send_request = self.original_send_request

    def mock_get_option(self, key, project):
        return self.options.get(key)
    
    def test_notify_default(self):
        """Test default behavior: send notification when no filters are set"""
        self.plugin._post(self.group, self.project)
        self.mock_send_request.assert_called_once()
        
    def test_exclude_keyword_match(self):
        """Test exclusion: do NOT send if keyword matches"""
        self.options["exclude_keywords"] = "test,error" # Changed to comma separation
        self.plugin._post(self.group, self.project)
        self.mock_send_request.assert_not_called()

    def test_exclude_keyword_no_match(self):
        """Test exclusion: SEND if keyword does not match"""
        self.options["exclude_keywords"] = "foobar"
        self.plugin._post(self.group, self.project)
        self.mock_send_request.assert_called_once()
        
    def test_include_keyword_match(self):
        """Test inclusion: SEND if keyword matches"""
        self.options["include_keywords"] = "message"
        self.plugin._post(self.group, self.project)
        self.mock_send_request.assert_called_once()

    def test_include_keyword_no_match(self):
        """Test inclusion: do NOT send if keyword does not match"""
        self.options["include_keywords"] = "urgent"
        self.plugin._post(self.group, self.project)
        self.mock_send_request.assert_not_called()

    def test_exclude_takes_precedence(self):
        """Test that exclusion takes precedence over inclusion"""
        self.options["include_keywords"] = "test"
        self.options["exclude_keywords"] = "error"
        # "test" is in text (should include), but "error" is in text (should exclude)
        self.plugin._post(self.group, self.project)
        self.mock_send_request.assert_not_called()
    
    @patch('os.getenv')
    def test_env_var_fallback(self, mock_getenv):
        """Test fallback to environment variables if project option is missing"""
        # Scenario: Project config is empty, but ENV VAR is set
        self.options["webhook"] = None 
        
        # Configure the os.getenv mock
        def side_effect(key):
            if key == "DINGTALK_WEBHOOK":
                return "http://env-var-webhook.com"
            return None
        mock_getenv.side_effect = side_effect
        
        self.plugin._post(self.group, self.project)
        
        # Should call send_request with the env var URL
        self.mock_send_request.assert_called_with(
            "http://env-var-webhook.com", 
            unittest.mock.ANY, 
            unittest.mock.ANY
        )

if __name__ == '__main__':
    unittest.main()
