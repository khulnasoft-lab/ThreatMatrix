# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.
from typing import Type

from api_app.analyzables_manager.models import Analyzable
from api_app.choices import Classification
from api_app.connectors_manager.models import ConnectorConfig, ConnectorReport
from api_app.models import Job, PluginConfig
from tests import CustomViewSetTestCase, PluginActionViewsetTestCase
from tests.api_app.test_views import AbstractConfigViewSetTestCaseMixin


class ConnectorConfigViewSetTestCase(
    AbstractConfigViewSetTestCaseMixin, CustomViewSetTestCase
):
    URL = "/api/connector"

    @classmethod
    @property
    def model_class(cls) -> Type[ConnectorConfig]:
        return ConnectorConfig

    def test_health_check(self):
        connector: ConnectorConfig = ConnectorConfig.objects.get(name="YETI")
        pc1 = PluginConfig.objects.create(
            parameter=connector.parameters.get(name="api_key_name"),
            value="test",
            for_organization=False,
            owner=None,
            connector_config=connector,
        )
        pc2 = PluginConfig.objects.create(
            parameter=connector.parameters.get(name="url_key_name"),
            value="https://test",
            for_organization=False,
            owner=None,
            connector_config=connector,
        )
        response = self.client.get(f"{self.URL}/{connector.name}/health_check")
        self.assertEqual(response.status_code, 200)

        self.client.force_authenticate(self.superuser)
        response = self.client.get(f"{self.URL}/{connector.name}/health_check")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("status", result)
        self.assertTrue(result["status"])
        pc1.delete()
        pc2.delete()


class ConnectorActionViewSetTests(CustomViewSetTestCase, PluginActionViewsetTestCase):
    fixtures = [
        "api_app/fixtures/0001_user.json",
    ]

    @property
    def plugin_type(self):
        return "connector"

    def setUp(self):
        super().setUp()
        self.config = ConnectorConfig.objects.get(name="MISP")

    def init_report(self, status: str, user) -> ConnectorReport:
        an1 = Analyzable.objects.create(
            name="8.8.8.8",
            classification=Classification.IP,
        )

        _job = Job.objects.create(
            user=user, status=Job.STATUSES.REPORTED_WITHOUT_FAILS, analyzable=an1
        )
        _job.connectors_to_execute.set([self.config])
        _report, _ = ConnectorReport.objects.get_or_create(
            **{
                "job_id": _job.id,
                "status": status,
                "config": self.config,
                "task_id": "4b77bdd6-d05b-442b-92e8-d53de5d7c1a9",
                "parameters": {},
            }
        )
        return _report
