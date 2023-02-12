"""
RTCM Protocol core globals and constants

Created on 10 Feb 2023

Information sourced from

:author: semuadmin
"""
# pylint: disable=line-too-long

SPARTN_PRE = 0x73
SPARTN_PREB = b"s"
SPARTN_MSGIDS = {
    0: "SPARTN-1X-OCB",  # Orbit, Clock, Bias
    (0, 0): "SPARTN-1X-OCB-GPS",
    (0, 1): "SPARTN-1X-OCB-GLO",
    (0, 2): "SPARTN-1X-OCB-GAL",
    (0, 3): "SPARTN-1X-OCB-BEI",
    (0, 4): "SPARTN-1X-OCB-QZS",
    1: "SPARTN-1X-HPAC",  # High-precision atmosphere correction
    (1, 0): "SPARTN-1X-HPAC-GPS",
    (1, 1): "SPARTN-1X-HPAC-GLO",
    (1, 2): "SPARTN-1X-HPAC-GAL",
    (1, 3): "SPARTN-1X-HPAC-BEI",
    (1, 4): "SPARTN-1X-HPAC-QZS",
    2: "SPARTN-1X-GAD",  # Geographic Area Definition
    (2, 0): "SPARTN-1X-GAD",
    3: "SPARTN-1X-BPAC",  # Basic-precision atmosphere correction
    (3, 0): "SPARTN-1X-BPAC",
    4: "SPARTN-1X-EAS",  # Encryption and Authentication Support
    (4, 0): "SPARTN-1X-EAS-DYN",
    (4, 1): "SPARTN-1X-EAS-GRP",  # deprecated
    120: "SPARTN_1X-PROP",  # Proprietary messages
    (120, 0): "SPARTN-1X-PROP-TEST",
    (120, 1): "SPARTN-1X-PROP-UBLOX",
    (120, 2): "SPARTN-1X-PROP-SWIFT",
}
