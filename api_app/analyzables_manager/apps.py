# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.

from django.apps import AppConfig


class AnalyzablesManagerConfig(AppConfig):
    name = "api_app.analyzables_manager"

    @staticmethod
    def ready() -> None:
        from . import signals  # noqa
