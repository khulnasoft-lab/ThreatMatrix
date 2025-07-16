# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.

from django.apps import AppConfig


class EnginesManagerConfig(AppConfig):
    name = "api_app.engines_manager"

    @staticmethod
    def ready(**kwargs) -> None:
        from . import signals  # noqa
