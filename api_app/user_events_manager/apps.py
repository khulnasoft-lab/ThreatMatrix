# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.

from django.apps import AppConfig


class UserEventsManagerConfig(AppConfig):
    name = "api_app.user_events_manager"

    @staticmethod
    def ready(**kwargs) -> None:
        from . import signals  # noqa
