
import logging
import time
import hmac
import hashlib
import base64
import urllib.parse
import requests

from sentry.plugins.bases.notify import NotificationPlugin
from sentry.utils.http import absolute_uri

logger = logging.getLogger('sentry.plugins.dingtalk')

from django import forms

class DingTalkOptionsForm(forms.Form):
    access_token = forms.CharField(
        label='Access Token',
        widget=forms.Textarea(attrs={'class': 'span6', 'placeholder': 'e.g. xxxxxxxx\nyyyyyyyy'}),
        help_text='The access token for your DingTalk robot webhook. One per line.',
        required=True
    )
    secret = forms.CharField(
        label='Secret',
        widget=forms.Textarea(attrs={'class': 'span6', 'placeholder': 'e.g. SECxxxxxxxx\nSECyyyyyyyy'}),
        help_text='The secret for the "Sign" (加签) security setting. One per line, corresponding to the access tokens.',
        required=False
    )
    custom_keyword = forms.CharField(
        label='Custom Keyword',
        widget=forms.TextInput(attrs={'class': 'span6', 'placeholder': 'e.g. Sentry'}),
        help_text='Optional. If you set a keyword in DingTalk, include it here to ensure the message is delivered.',
        required=False
    )
    at_mobiles = forms.CharField(
        label='At Mobiles',
        widget=forms.TextInput(attrs={'class': 'span6', 'placeholder': 'e.g. 13800000000,13900000000'}),
        help_text='Optional. Comma-separated list of mobile numbers to @ in the message.',
        required=False
    )
    is_at_all = forms.BooleanField(
        label='Is At All',
        help_text='Whether to @ all members in the group.',
        required=False
    )

class DingTalkPlugin(NotificationPlugin):
    author = 'lanxuexing'
    author_url = 'https://github.com/lanxuexing/sentry-dingtalk-notify'
    version = '1.0.0'
    description = 'DingTalk integration for Sentry.'
    resource_links = [
        ('Bug Tracker', 'https://github.com/lanxuexing/sentry-dingtalk-notify/issues'),
        ('Source', 'https://github.com/lanxuexing/sentry-dingtalk-notify'),
    ]

    slug = 'dingtalk-notify'
    title = 'DingTalk Notify'
    conf_title = 'DingTalk Notify'
    conf_key = 'dingtalk-notify'
    
    project_conf_form = DingTalkOptionsForm

    def is_configured(self, project):
        is_conf = bool(self.get_option('access_token', project))
        logger.info(f"DingTalk check is_configured for project {project.slug}: {is_conf}")
        return is_conf

    def should_notify(self, group, event):
        should = super().should_notify(group, event)
        logger.info(f"DingTalk should_notify for event {event.event_id}: {should}")
        return should

    def get_group_url(self, group):
        return absolute_uri('/organizations/{}/issues/{}/'.format(
            group.organization.slug,
            group.id,
        ))

    def notify_users(self, group, event, fail_silently=False, triggering_rules=None, **kwargs):
        access_tokens_str = self.get_option('access_token', group.project)
        secrets_str = self.get_option('secret', group.project)
        custom_keyword = self.get_option('custom_keyword', group.project) or ''
        at_mobiles_str = self.get_option('at_mobiles', group.project) or ''
        is_at_all = self.get_option('is_at_all', group.project) or False

        logger.info(f"DingTalk notify_users called for event {event.event_id}")

        if not access_tokens_str:
            logger.info("DingTalk access token not configured, skipping.")
            return

        access_tokens = [t.strip() for t in access_tokens_str.strip().split('\n') if t.strip()]
        
        # Secrets: Do not strip the main string to preserve leading empty lines (for mapping)
        # We assume one line of secret corresponds to one line of access token
        secrets = secrets_str.split('\n') if secrets_str else []

        at_mobiles = [m.strip() for m in at_mobiles_str.split(',') if m.strip()]

        project = group.project
        project_name = project.name
        project_slug = project.slug
        
        # Try to get organization name
        org_name = project.organization.name if hasattr(project, 'organization') else "Unknown Org"
        
        # Tags (Environment, Level)
        tags = {}
        try:
            # Sentry Event objects usually have a .tags attribute (list of tuples)
            if hasattr(event, 'tags'):
                tags = dict(event.tags or [])
            # Fallback for older/other versions
            elif hasattr(event, 'get_tags'):
                tags = dict(event.get_tags() or [])
        except Exception as e:
            logger.info(f"DingTalk: Error getting tags: {e}")

        environment = tags.get('environment', 'N/A')
        level = group.get_level_display()
        
        # Error Title & Message
        # event.title is usually the exception type (e.g. "ValueError")
        # event.message is the description (e.g. "Something went wrong")
        # Sometimes they are same.
        evt_title = event.title or "Unknown Error"
        evt_message = event.message or ""
        
        # Culprit (Where it happened)
        culprit = event.culprit or group.culprit or "N/A"
        
        # Construct Display Title for DingTalk header
        # We put the Custom Keyword here if present to ensure reliable delivery
        header_prefix = f"【{project_name}】"
        if custom_keyword and custom_keyword not in header_prefix and custom_keyword not in evt_title:
             header_prefix = f"【{custom_keyword}】{header_prefix}"
        
        display_title = f"{header_prefix} {evt_title}"

        link = self.get_group_url(group)
        
        # Markdown Content
        # Using a list style for better readability
        text = f"### {evt_title}\n\n"
        
        # Key Metadata
        text += f"- **📦 Project**: {project_slug} ({org_name})\n"
        text += f"- **🌍 Env**: {environment}\n"
        text += f"- **🚦 Level**: {level}\n"
        text += f"- **📍 Location**: `{culprit}`\n"
        
        # Error Message (Quote block)
        if evt_message and evt_message != evt_title:
            text += f"\n> {evt_message}\n\n"
        else:
            text += "\n"

        # Trigger Context
        if triggering_rules:
            text += f"📢 **Trigger**: {', '.join(triggering_rules)}\n"
            
        # Action Link
        text += f"\n[👉 View Issue on Sentry]({link})\n"
        
        # Append @ mentions to text so they are visually highlighted
        if at_mobiles:
             at_text = ' '.join([f"@{m}" for m in at_mobiles])
             text += f"\n\n{at_text}"

        # Construct the request
        payload = {
            "msgtype": "markdown",
            "markdown": {
                "title": display_title,
                "text": text
            },
            "at": {
                "atMobiles": at_mobiles,
                "isAtAll": is_at_all
            }
        }

        for idx, access_token in enumerate(access_tokens):
            # Get corresponding secret by index
            secret = None
            if idx < len(secrets):
                s = secrets[idx].strip()
                # Allow empty line or '-' to mean "No Secret"
                if s and s != '-':
                    secret = s
            
            # 1. Signature
            timestamp = str(round(time.time() * 1000))
            sign = ''
            if secret:
                string_to_sign = f'{timestamp}\n{secret}'
                hmac_code = hmac.new(
                    secret.encode('utf-8'),
                    string_to_sign.encode('utf-8'),
                    digestmod=hashlib.sha256
                ).digest()
                sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
            
            url = f'https://oapi.dingtalk.com/robot/send?access_token={access_token}'
            if sign:
                url += f'&timestamp={timestamp}&sign={sign}'

            try:
                resp = requests.post(url, json=payload, timeout=5)
                resp.raise_for_status()
                result = resp.json()
                if result.get('errcode') != 0:
                    logger.error(f'Error communicating with DingTalk (Token ending {access_token[-4:]}): {result}')
            except Exception as e:
                logger.error(f'Error sending message to DingTalk (Token ending {access_token[-4:]}): {e}')
