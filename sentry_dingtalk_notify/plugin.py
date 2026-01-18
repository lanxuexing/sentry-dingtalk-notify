"""
  @Project     : sentry-dingtalk-notify
  @Time        : 2021/07/17 18:24:53
  @File        : plugin.py
  @Author      : lanxuexing
  @Software    : VSCode
  @Desc        : 
"""


import os
import requests
import six
import logging
from sentry.plugins.bases import notify

from sentry.utils import json
from sentry.integrations import FeatureDescription, IntegrationFeatures
from sentry_plugins.base import CorePluginMixin
from django.conf import settings

logger = logging.getLogger(__name__)

class DingTalkNotifyPlugin(CorePluginMixin, notify.NotificationPlugin):
    title = "DingTalk Notify"
    slug = "dingtalknotify"
    description = "Post notifications to Dingtalk."
    conf_key = "dingtalknotify"
    required_field = "webhook"
    author = "lanxuexing"
    author_url = "https://github.com/lanxuexing/sentry-dingtalk-notify"
    version = "1.1.1"
    resource_links = [
        ("Report Issue", "https://github.com/lanxuexing/sentry-dingtalk-notify/issues"),
        ("View Source", "https://github.com/lanxuexing/sentry-dingtalk-notify"),
    ]

    feature_descriptions = [
        FeatureDescription(
            """
                Configure rule based Dingtalk notifications to automatically be posted into a
                specific channel.
                """,
            IntegrationFeatures.ALERT_RULE,
        )
    ]

    def is_configured(self, project):
        return bool(self.get_conf(project, "webhook", "DINGTALK_WEBHOOK"))

    def get_config(self, project, **kwargs):
        return [
            {
                "name": "webhook",
                "label": "Webhook",
                "type": "textarea",
                "placeholder": "https://oapi.dingtalk.com/robot/send?access_token=**********",
                "required": True,
                "help": "Your custom DingTalk webhook (one per line).",
                "default": self.set_default(project, "webhook", "DINGTALK_WEBHOOK"),
            },
            {
                "name": "custom_keyword",
                "label": "Custom Keyword",
                "type": "string",
                "placeholder": "e.g. [Sentry] Error title",
                "required": False,
                "help": "Optional - custom keyword to prefix the notification title",
                "default": self.set_default(
                    project, "custom_keyword", "DINGTALK_CUSTOM_KEYWORD"
                ),
            },
            {
                "name": "include_keywords",
                "label": "Include Keywords",
                "type": "textarea",
                "placeholder": "keyword1,keyword2",
                "required": False,
                "help": "Optional - If set, only notifications containing at least one of these keywords will be sent (comma separated).",
                "default": self.set_default(project, "include_keywords", "DINGTALK_INCLUDE_KEYWORDS"),
            },
            {
                "name": "exclude_keywords",
                "label": "Exclude Keywords",
                "type": "textarea",
                "placeholder": "keyword1,keyword2",
                "required": False,
                "help": "Optional - Notifications containing any of these keywords will be ignored (comma separated).",
                "default": self.set_default(project, "exclude_keywords", "DINGTALK_EXCLUDE_KEYWORDS"),
            },
        ]

    def set_default(self, project, option, env_var):
        # Kept for backward compatibility in form defaults
        if self.get_option(option, project) != None:
            return self.get_option(option, project)
        if hasattr(settings, env_var):
            return six.text_type(getattr(settings, env_var))
        return None

    def get_conf(self, project, option, env_var=None):
        """
        Get config value with fallback to os.getenv (environment variables).
        """
        value = self.get_option(option, project)
        if not value and env_var:
            value = os.getenv(env_var)
        return value

    def split_urls(self, value):
        if not value:
            return ()
        return filter(bool, (url.strip() for url in value.splitlines()))

    def get_webhook_urls(self, project):
        return self.split_urls(self.get_option("webhook", project))

    def split_keywords(self, value):
        if not value:
            return []
        return [k.strip() for k in value.split(",") if k.strip()]

    def notify(self, notification, raise_exception=False):
        event = notification.event
        group = event.group
        project = group.project
        self._post(group, project)

    def notify_about_activity(self, activity):
        project = activity.project
        group = activity.group
        self._post(group, project)

    def _post(self, group, project):
        custom_keyword = self.get_conf(project, "custom_keyword", "DINGTALK_CUSTOM_KEYWORD")
        include_keywords = self.split_keywords(self.get_conf(project, "include_keywords", "DINGTALK_INCLUDE_KEYWORDS"))
        exclude_keywords = self.split_keywords(self.get_conf(project, "exclude_keywords", "DINGTALK_EXCLUDE_KEYWORDS"))

        title = group.title or ""
        message = group.message or ""
        # Combine title and message for keyword checking
        full_text = (title + "\n" + message).lower()

        # Check for inclusions if configured
        if include_keywords:
            if not any(k.lower() in full_text for k in include_keywords):
                logger.info("DingTalk notification skipped: No matching include_keywords found.")
                return

        # Check for exclusions: strict exclusion if any keyword matches
        
        if exclude_keywords:
            if any(k.lower() in full_text for k in exclude_keywords):
                logger.info("DingTalk notification excluded by keyword.")
                return

        issue_link = group.get_absolute_url(params={"referrer": "dingtalknotify"})

        payload = f"## {custom_keyword}\n\n" if custom_keyword else ""
        payload = f"{payload} #### Project: {project.name} \n\n"
        payload = f"{payload} #### Error: [{group.title}]({issue_link}) \n\n"
        payload = f"{payload} #### Detail: {group.message} \n\n"

        headers = {
            "Content-type": "application/json",
            "Accept": "text/plain",
            "charset": "utf8"
        }

        data = {
            "msgtype": "markdown",
            "markdown": {
                "title": group.title,
                "text": payload,
            },
        }
        
        webhook_url_conf = self.get_conf(project, "webhook", "DINGTALK_WEBHOOK")
        if not webhook_url_conf:
            logger.warning("DingTalk notification failed: No Webhook URL configured.")
            return

        urls = self.split_urls(webhook_url_conf)

        for webhook_url in urls:
            try:
                self.send_request(webhook_url, data, headers)
            except Exception as e:
                logger.error(f"Failed to send DingTalk notification: {e}", exc_info=True)

    def send_request(self, url, data, headers):
        requests.post(url, data=json.dumps(data), headers=headers)
