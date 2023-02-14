"""
SPARTN Protocol core globals and constants

Created on 10 Feb 2023

Information Sourced from https://www.spartnformat.org/download/
(available in the public domain) © 2021 u-blox AG. All rights reserved.

:author: semuadmin
"""
# pylint: disable=too-many-lines, line-too-long


# ************************************************************************
# SPARTN MESSAGE PAYLOAD DEFINITIONS (NB: PAYLOAD MUST BE DECRYPTED FIRST)
# ************************************************************************
SPARTN_PAYLOADS_GET = {
    "SPARTN-1X-OCB-GPS": {},
    "SPARTN-1X-OCB-GLO": {},
    "SPARTN-1X-OCB-GAL": {},
    "SPARTN-1X-OCB-BEI": {},
    "SPARTN-1X-OCB-QZS": {},
    "SPARTN-1X-HPAC-GPS": {},
    "SPARTN-1X-HPAC-GLO": {},
    "SPARTN-1X-HPAC-GAL": {},
    "SPARTN-1X-HPAC-BEI": {},
    "SPARTN-1X-HPAC-QZS": {},
    "SPARTN-1X-GAD": {
        "SF005": "Solution issue of updated (SIOU)",
        "SF068": "Area issue of update (AIOU)",
        "SF069": "Reserved",
        "SF030": "Area Count",
        "group": (
            "SF030",
            {
                "SF031": "Area ID",
                "SF032": "Area reference latitude",
                "SF033": "Area reference longitude",
                "SF034": "Are latitude grid node count",
                "SF035": "Area longitude grid node count",
                "SF036": "Area latitude grid node spacing",
                "SF037": "Area longitude grid node spacing",
            },
        ),
    },
    "SPARTN-1X-BPAC": {},
    "SPARTN-1X-EAS-DYN": {},
    "SPARTN-1X-EAS-GRP": {},  # deprecated
}
