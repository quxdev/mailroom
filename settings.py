import os

from django.conf import settings


def default_project_setting_to_app(setting, default):
    return getattr(settings, setting, os.getenv(setting, default))


def default_app_setting_to_project(setting, default):
    return os.getenv(setting, getattr(settings, setting, default))


# Examples
MAILROOM_CC = os.getenv("MAILROOM_CC", None)
MAILROOM_CC = [MAILROOM_CC] if MAILROOM_CC else []
MAILROOM_BCC = os.getenv("MAILROOM_BCC", None)
MAILROOM_BCC = [MAILROOM_BCC] if MAILROOM_BCC else []
