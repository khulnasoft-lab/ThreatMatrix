# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.
from django.contrib import admin

from api_app.admin import AbstractReportAdminView, PythonConfigAdminView
from api_app.analyzers_manager.models import AnalyzerConfig, AnalyzerReport


# flake8: noqa
@admin.register(AnalyzerReport)
class AnalyzerReportAdminView(AbstractReportAdminView): ...


@admin.register(AnalyzerConfig)
class AnalyzerConfigAdminView(PythonConfigAdminView):
    list_display = PythonConfigAdminView.list_display + (
        "type",
        "docker_based",
        "maximum_tlp",
    )
    list_filter = ["type", "maximum_tlp"] + PythonConfigAdminView.list_filter
    exclude = ["update_task"]
