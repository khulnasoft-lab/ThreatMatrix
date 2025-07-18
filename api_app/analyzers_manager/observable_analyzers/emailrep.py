# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.

import requests

from api_app.analyzers_manager import classes
from api_app.analyzers_manager.exceptions import AnalyzerRunException
from api_app.choices import Classification
from tests.mock_utils import MockUpResponse, if_mock_connections, patch


class EmailRep(classes.ObservableAnalyzer):
    url: str = "https://emailrep.io/{}"

    _api_key_name: str

    @classmethod
    def update(cls) -> bool:
        pass

    def run(self):
        """
        API key is not mandatory, emailrep supports requests with no key:
        a valid key let you to do more requests per day.
        therefore we're not checking if a key has been configured.
        """

        headers = {
            "User-Agent": "ThreatMatrix",
            "Key": self._api_key_name,
            "Accept": "application/json",
        }

        if self.observable_classification not in [Classification.GENERIC]:
            raise AnalyzerRunException(
                f"not supported observable type {self.observable_classification}."
                f" Supported: generic"
            )

        url = self.url.format(self.observable_name)

        response = requests.get(url, headers=headers)
        response.raise_for_status()

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
