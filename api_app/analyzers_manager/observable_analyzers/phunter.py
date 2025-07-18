import logging

import phonenumbers
import requests

from api_app.analyzers_manager.classes import DockerBasedAnalyzer, ObservableAnalyzer
from api_app.analyzers_manager.exceptions import AnalyzerRunException
from tests.mock_utils import MockUpResponse

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class PhunterAnalyzer(ObservableAnalyzer, DockerBasedAnalyzer):
    name: str = "Phunter"
    url: str = "http://phunter:5612/analyze"
    max_tries: int = 1
    poll_distance: int = 0

    def run(self):
        try:
            parsed_number = phonenumbers.parse(self.observable_name)

            formatted_number = phonenumbers.format_number(
                parsed_number, phonenumbers.PhoneNumberFormat.E164
            )
        except phonenumbers.phonenumberutil.NumberParseException:
            logger.error(f"Phone number parsing failed for: {self.observable_name}")
            return {"success": False, "error": "Invalid phone number"}

        req_data = {"phone_number": formatted_number}
        logger.info(f"Sending {self.name} scan request: {req_data} to {self.url}")

        try:
            response = self._docker_run(
                req_data, analyzer_name=self.name, avoid_polling=True
            )
            logger.info(f"[{self.name}] Scan successful by Phunter. Result: {response}")
            return response

        except requests.exceptions.RequestException as e:
            raise AnalyzerRunException(
                f"[{self.name}] Request failed due to network issue: {e}"
            )

        except ValueError as e:
            raise AnalyzerRunException(f"[{self.name}] Invalid response format: {e}")

        except Exception as e:
            raise AnalyzerRunException(f"{self.name} An unexpected error occurred: {e}")

    @classmethod
    def update(self):
        pass

    @staticmethod
    def mocked_docker_analyzer_post(*args, **kwargs):
        mock_response = {
            "success": True,
            "report": {
                "valid": "yes",
                "views": "9",
                "carrier": "Vodafone",
                "location": "India",
                "operator": "Vodafone",
                "possible": "yes",
                "line_type": "FIXED LINE OR MOBILE",
                "local_time": "21:34:45",
                "spam_status": "Not spammer",
                "phone_number": "+911234567890",
                "national_format": "01234567890",
                "international_format": "+91 1234567890",
            },
        }
        return MockUpResponse(mock_response, 200)
