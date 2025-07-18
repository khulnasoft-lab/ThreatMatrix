# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.

import requests

from api_app.analyzers_manager import classes
from api_app.analyzers_manager.exceptions import AnalyzerRunException
from api_app.choices import Classification
from tests.mock_utils import MockUpResponse, if_mock_connections, patch


class Threatminer(classes.ObservableAnalyzer):
    url = "https://api.threatminer.org/v2/"
    rt_value: str

    @classmethod
    def update(cls) -> bool:
        pass

    def run(self):
        params = {"q": self.observable_name}
        if self.rt_value:
            params["rt"] = self.rt_value

        if self.observable_classification == Classification.DOMAIN:
            uri = "domain.php"
        elif self.observable_classification == Classification.IP:
            uri = "host.php"
        elif self.observable_classification == Classification.HASH:
            uri = "sample.php"
        else:
            raise AnalyzerRunException(
                "Unable to retrieve the uri for classification"
                f" {self.observable_classification}"
            )

        try:
            response = requests.get(self.url + uri, params=params)
            response.raise_for_status()
        except requests.RequestException as e:
            raise AnalyzerRunException(e)

        return response.json()

    @classmethod
    def _monkeypatch(cls):
        patches = [
            if_mock_connections(
                patch(
                    "requests.get",
                    return_value=MockUpResponse({}, 200),
                ),
            )
        ]
        return super()._monkeypatch(patches=patches)
