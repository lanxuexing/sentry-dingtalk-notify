"""
  @Project     : sentry-dingtalk-notify
  @Time        : 2021/07/17 18:24:53
  @File        : plugin.py
  @Author      : lanxuexing
  @Software    : VSCode
  @Desc        : 
"""


import requests
import six
from sentry.plugins.bases import notify
from sentry.utils import json
from sentry.integrations import FeatureDescription, IntegrationFeatures
from sentry_plugins.base import CorePluginMixin
from django.conf import settings


class DingTalkNotifyPlugin(CorePluginMixin, notify.NotificationPlugin):
    title = "DingTalk Notify"
    slug = "dingtalknotify"
    description = "Post notifications to Dingtalk."
    conf_key = "dingtalknotify"
    required_field = "webhook"
    author = "lanxuexing"
    author_url = "https://github.com/lanxuexing/sentry-dingtalk-notify"
    version = "1.0.0"
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
        return bool(self.get_option("webhook", project))

    def get_config(self, project, **kwargs):
        return [
            {
                "name": "webhook",
                "label": "webhook",
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
                "help": "Optional - custom keyword",
                "default": self.set_default(
                    project, "custom_keyword", "DINGTALK_CUSTOM_KEYWORD"
                ),
            },
        ]

    def set_default(self, project, option, env_var):
        if self.get_option(option, project) != None:
            return self.get_option(option, project)
        if hasattr(settings, env_var):
            return six.text_type(getattr(settings, env_var))
        return None

    def split_urls(self, value):
        if not value:
            return ()
        return filter(bool, (url.strip() for url in value.splitlines()))
    
    def get_webhook_urls(self, project):
        return self.split_urls(self.get_option("webhook", project))

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
        custom_keyword = self.get_option("custom_keyword", project)

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

        for webhook_url in self.get_webhook_urls(group.project):
            requests.post(webhook_url, data=json.dumps(data), headers=headers)
