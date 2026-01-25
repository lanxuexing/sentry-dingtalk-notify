
import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add the package to pythnon path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock sentry dependencies before importing the plugin
sys.modules['sentry'] = MagicMock()
sys.modules['sentry.plugins'] = MagicMock()
sys.modules['sentry.plugins.bases'] = MagicMock()
sys.modules['sentry.plugins.bases.notify'] = MagicMock()
sys.modules['sentry.utils'] = MagicMock()
sys.modules['sentry.utils.http'] = MagicMock()
sys.modules['requests'] = MagicMock() # Mock requests as it is not installed

# Define a MockNotifyPlugin to inherit from
class MockNotifyPlugin:
    def get_option(self, key, project):
        return None

sys.modules['sentry.plugins.bases.notify'].NotifyPlugin = MockNotifyPlugin

from sentry_dingtalk.plugin import DingTalkPlugin

class TestDingTalkPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = DingTalkPlugin()
        self.options = {
            'access_token': 'fake_token',
            'secret': 'fake_secret',
            'custom_keyword': 'TestKeyword',
            'at_mobiles': '12345678901',
            'is_at_all': False
        }
        
        # Mock get_option to return values from self.options
        self.plugin.get_option = MagicMock(side_effect=lambda key, project: self.options.get(key))
        
        # Mock get_group_url
        self.plugin.get_group_url = MagicMock(return_value='http://sentry.example.com/group/1/')

    @patch('requests.post')
    def test_notify_users(self, mock_post):
        # Mock Event and Group
        group = MagicMock()
        group.project.name = 'TestProject'
        group.get_level_display.return_value = 'Error'
        group.message = 'Group Message'
        
        event = MagicMock()
        event.title = 'Event Title'
        event.message = 'Event Message'

        mock_response = MagicMock()
        mock_response.json.return_value = {'errcode': 0}
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        # Execute
        self.plugin.notify_users(group, event)

        # Verify calls
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        url = args[0]
        json_data = kwargs['json']

        self.assertIn('https://oapi.dingtalk.com/robot/send', url)
        self.assertIn('access_token=fake_token', url)
        self.assertIn('timestamp=', url)
        self.assertIn('sign=', url)
        
        self.assertEqual(json_data['msgtype'], 'markdown')
        self.assertIn('TestKeyword', json_data['markdown']['title'])
        self.assertIn('TestProject', json_data['markdown']['title'])
        self.assertIn('12345678901', json_data['at']['atMobiles'])

    @patch('requests.post')
    def test_notify_users_no_config(self, mock_post):
        self.options = {} # Empty config
        group = MagicMock()
        event = MagicMock()
        
        self.plugin.notify_users(group, event)
        
        mock_post.assert_not_called()

if __name__ == '__main__':
    unittest.main()
