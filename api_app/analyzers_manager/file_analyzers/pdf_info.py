# This file is a part of ThreatMatrix https://github.com/khulnasoft/ThreatMatrix
# See the file 'LICENSE' for copying permission.

import logging
from typing import Any, List

import peepdf
from pdfid import pdfid

from api_app.analyzers_manager.classes import FileAnalyzer
from api_app.analyzers_manager.exceptions import AnalyzerRunException

logger = logging.getLogger(__name__)


class PDFInfo(FileAnalyzer):
    @staticmethod
    def flatten(list_of_lists: List[List[Any]]) -> List[Any]:
        return [item for sublist in list_of_lists for item in sublist]

    @classmethod
    def update(cls) -> bool:
        pass

    def run(self):
        self.results = {"peepdf": {}, "pdfid": {}, "uris": []}
        # the analysis fails only when BOTH fails
        peepdf_success = self.__peepdf_analysis()
        pdfid_success = self.__pdfid_analysis()
        if not peepdf_success and not pdfid_success:
            raise AnalyzerRunException("both peepdf and pdfid failed")

        # pivot uris in the pdf only if we have one page
        if (
            "reports" in self.results["pdfid"]
            and isinstance(self.results["pdfid"]["reports"], list)
            and peepdf_success
        ):
            for elem in self.results["pdfid"]["reports"]:
                if "/Page" in elem and elem["/Page"] == 1:
                    for s in self.results["peepdf"]["stats"]:
                        self.results["uris"].extend(s["uris"])

        logger.info(f"extracted urls from file {self.md5}: {self.results['uris']}")

        return self.results

    def __peepdf_analysis(self):
        success = False
        peepdf_analysis = {}
        try:
            pdf_parser = peepdf.PDFCore.PDFParser()
            ret, pdf = pdf_parser.parse(self.filepath, True)
            if ret:
                peepdf_analysis["status_code"] = ret
            else:
                stats = pdf.getStats()
                peepdf_analysis["stats"] = []
                for version in stats.get("Versions", []):
                    version_dict = {
                        "events": version.get("Events", {}),
                        "actions": version.get("Actions", {}),
                        "urls": self.flatten(pdf.getURLs()),
                        "uris": self.flatten(pdf.getURIs()),
                        "elements": version.get("Elements", {}),
                        "vulns": version.get("Vulns", []),
                        "objects_with_js_code": version.get("Objects with JS code", []),
                    }
                    peepdf_analysis["stats"].append(version_dict)

            self.results["peepdf"] = peepdf_analysis
        except TypeError as e:
            # rc4Key = rc4Key[:keyLength]
            # TypeError: slice indices must be integers or None or
            # have an __index__ method
            self.results["peepdf"]["error"] = str(e)
        except UnboundLocalError as e:
            logger.info(e, stack_info=True)
            self.results["peepdf"]["error"] = str(e)
        except Exception as e:
            logger.exception(e)
            self.results["peepdf"]["error"] = str(e)
        else:
            success = True
        return success

    def __pdfid_analysis(self):
        success = False
        try:
            options = pdfid.get_fake_options()
            options.json = True
            list_of_dict = pdfid.PDFiDMain([self.filepath], options)
            self.results["pdfid"] = list_of_dict
        except Exception as e:
            logger.exception(e)
            self.results["pdfid"]["error"] = str(e)
        else:
            success = True
        return success
