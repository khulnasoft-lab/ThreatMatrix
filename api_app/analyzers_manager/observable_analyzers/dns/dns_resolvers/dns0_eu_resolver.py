# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.

import logging
from ipaddress import AddressValueError, IPv4Address
from urllib.parse import urlparse

import requests

from api_app.analyzers_manager import classes
from api_app.analyzers_manager.exceptions import AnalyzerRunException
from api_app.choices import Classification
from tests.mock_utils import MockUpResponse, if_mock_connections, patch

from ..dns_responses import dns_resolver_response

logger = logging.getLogger(__name__)


class DNS0EUResolver(classes.ObservableAnalyzer):
    """Resolve a DNS query with DNS0.eu"""

    class NotADomain(Exception):
        pass

    url = "https://dns0.eu"
    headers = {"Accept": "application/dns-json"}

    query_type: str

    def run(self):
        observable = self.observable_name
        resolutions = None
        try:
            # for URLs we are checking the relative domain
            if self.observable_classification == Classification.URL:
                observable = urlparse(self.observable_name).hostname
                try:
                    IPv4Address(observable)
                except AddressValueError:
                    pass
                else:
                    raise self.NotADomain()

            params = {"name": observable, "type": self.query_type}

            response = requests.get(self.url, headers=self.headers, params=params)
            response.raise_for_status()
            resolutions = response.json().get("Answer", [])
        except requests.RequestException:
            raise AnalyzerRunException(
                "an error occurred during the connection to DNS0"
            )
        except self.NotADomain:
            logger.info(f"not analyzing {observable} because not a domain")

        return dns_resolver_response(self.observable_name, resolutions)

    @classmethod
    def _monkeypatch(cls):
        patches = [
            if_mock_connections(
                patch(
                    "requests.get",
                    return_value=MockUpResponse({"Answer": ["test1", "test2"]}, 200),
                ),
            )
        ]
        return super()._monkeypatch(patches=patches)
