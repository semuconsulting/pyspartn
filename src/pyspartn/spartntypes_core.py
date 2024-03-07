"""
SPARTN Protocol core globals and constants

Created on 10 Feb 2023

Information Sourced from https://www.spartnformat.org/download/
(available in the public domain) © 2021 u-blox AG. All rights reserved.

:author: semuadmin
"""

# pylint: disable=line-too-long

from datetime import datetime

TIMEBASE = datetime(2010, 1, 1, 0, 0)
ERRRAISE = 2
ERRLOG = 1
ERRIGNORE = 0
VALNONE = 0
VALCRC = 1
VALMSGID = 2
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

# Transient attribute names used to store variable bitmask length flags
NB = "NB_"
STBMLEN = "SatBitmaskLen"
PBBMLEN = "PhaseBiasBitmaskLen"
CBBMLEN = "CodeBiasBitmaskLen"

# Nested group depth for conditional attributes
# (so we know how many group indices to add e.g. SF011_02, SF056_02_04)
NESTED_DEPTH = {
    "SF008": -1,
    "SF011": 0,
    "SF012": 0,
    "SF013": 0,
    "SF014O": 0,
    "SF014C": 0,
    "SF014B": 0,
    "SF093": 0,
    "SF094": 0,
    "SF095": 0,
    "SF040T": 0,
    "SF040I": 0,
    "SF041": 0,
    "SF044": 0,
    "SF054": 0,
    "SF056": 1,
}

# datafields used in message definitions
# key: (length in bits, resolution, description)
SPARTN_DATA_FIELDS = {
    "SF005": (9, "1", "Solution issue of update (SIOU)"),
    "SF008": (1, "n/a", "Yaw present flag"),
    "SF009": (1, "1", "Satellite reference datum"),
    "SF010": (1, "n/a", "End of OCB set (EOS)"),
    STBMLEN: (2, "n/a", "Length of satellite bitmask"),
    "SF011": ("34 to 66", "Bitmask", "GPS Satellite mask"),
    "SF012": ("26 to 65", "Bitmask", "GLONASS Satellite mask"),
    "SF013": (1, "n/a", "Do not use (DNU)"),
    "SF014O": (1, "Bitmask", "Orbit data present flag"),
    "SF014C": (1, "Bitmask", "Clock data present flag"),
    "SF014B": (1, "Bitmask", "Bias data present flag"),
    "SF015": (3, "n/a", "Continuity indicator"),
    "SF016": (2, "n/a", "GPS ephemeris type"),
    "SF017": (2, "n/a", "GLO ephemeris type"),
    "SF018": (8, "1", "GPS IODE"),
    "SF019": (7, "1", "GLO IODE"),
    "SF020R": (14, "0.002 m", "Satellite radial corrections"),
    "SF020A": (14, "0.002 m", "Satellite along-track corrections"),
    "SF020C": (14, "0.002 m", "Satellite cross-track corrections"),
    "SF020CK": (14, "0.002 m", "Satellite clock corrections"),
    "SF020PB": (14, "0.002 m", "Phase bias correction"),
    "SF021": (6, "6°", "Satellite yaw"),
    "SF022": (3, "n/a", "IODE continuity"),
    "SF023": (1, "n/a", "Fix flag"),
    "SF024": (3, "n/a", "User range error (URE)"),
    PBBMLEN: (1, "n/a", "Length of phase bias bitmask"),
    "SF025": ("7 or 12", "bitmask", "GPS phase bias mask"),
    "SF026": ("6 or 10", "bitmask", "GLONASS phase bias mask"),
    CBBMLEN: (1, "n/a", "Length of code bias bitmask"),
    "SF027": ("7 or 12", "bitmask", "GPS code bias mask"),
    "SF028": ("6 or 10", "bitmask", "GLONASS code bias mask"),
    "SF029": (11, "0.02 m", "Code bias correction"),
    "SF030": (5, "1", "Area Count"),
    "SF031": (8, "1", "Area ID"),
    "SF032": (11, "0.1 degrees", "Area reference latitude"),
    "SF033": (12, "0.1 degrees", "Area reference longitude"),
    "SF034": (3, "1", "Area latitude grid node count"),
    "SF035": (3, "1", "Area longitude grid node count"),
    "SF036": (5, "0.1 degrees", "Area latitude grid node spacing"),
    "SF037": (5, "0.1 degrees", "Area longitude grid node spacing"),
    "SF039": (7, "1", "Number of grid points present"),
    "SF040": (2, "1", "Poly/Grid block present indicator"),
    "SF040T": (2, "1", "Troposphere Poly/Grid block present indicator"),
    "SF040I": (2, "1", "Ionoshere Poly/Grid block present indicator"),
    "SF041": (3, "1", "Troposphere equation type"),
    "SF042": (3, "1", "Troposphere quality"),
    "SF043": (8, "0.004 m", "Area average vertical hydrostatic delay"),
    "SF044": (1, "1", "Troposphere polynomial coefficient size indicator"),
    "SF045": (7, "0.004 m", "Small troposphere coefficient T00"),
    "SF046a": (7, "0.001 m / degree", "Small troposphere coefficient T01"),
    "SF046b": (7, "0.001 m / degree", "Small troposphere coefficient T10"),
    "SF047": (9, "0.0002 m /degree2", "Small troposphere coefficient T11"),
    "SF048": (9, "0.004 m", "Large troposphere coefficient T00"),
    "SF049a": (9, "0.001 m / degree", "Large troposphere coefficient T01"),
    "SF049b": (9, "0.001 m / degree", "Large troposphere coefficient T10"),
    "SF050": (11, "0.0002 m / degree2", "Large troposphere coefficient T11"),
    "SF051": (1, "1", "Troposphere residual field size"),
    "SF052": (6, "0.004 m", "Small troposphere residual zenith delay"),
    "SF053": (8, "0.004 m", "Large troposphere residual zenith delay"),
    "SF054": (3, "1", "Ionosphere equation type"),
    "SF055": (4, "1", "Ionosphere quality"),
    "SF056": (1, "1", "Ionosphere polynomial coefficient size indicator"),
    "SF057": (12, "0.04 TECU", "Small ionosphere coefficient C00"),
    "SF058a": (12, "0.008 TECU / degree", "Small ionosphere coefficient C01"),
    "SF058b": (12, "0.008 TECU / degree", "Small ionosphere coefficient C10"),
    "SF059": (13, "0.002 TECU / degree2 ", "Small ionosphere coefficient C11"),
    "SF060": (14, "0.04 TECU", "Large ionosphere coefficient C00"),
    "SF061a": (14, "0.008 TECU / degree", "Large ionosphere coefficient C01"),
    "SF061b": (14, "0.008 TECU / degree", "Large ionosphere coefficient C10"),
    "SF062": (15, "0.002 TECU / degree2", "Large ionosphere coefficient C11"),
    "SF063": (2, "1", "Ionosphere residual field size"),
    "SF064": (4, "0.04 TECU", "Small ionosphere residual slant delay"),
    "SF065": (7, "0.04 TECU", "Medium ionosphere residual slant delay"),
    "SF066": (10, "0.04 TECU", "Large ionosphere residual slant delay"),
    "SF067": (14, "0.04 TECU", "Extra-large ionosphere residual slant delay"),
    "SF068": (4, "1", "Area Issue of Update (AIOU)"),
    "SF069": (1, "N/A", "Reserved"),
    "SF070": (2, "1", "Ionosphere shell height"),
    "SF071": (2, "1", "BPAC area count"),
    "SF072": (2, "1", "BPAC area ID"),
    "SF073": (8, "1.0 degrees", "BPAC area reference latitude"),
    "SF074": (9, "1.0 degrees", "BPAC area reference longitude"),
    "SF075": (4, "1", "BPAC area latitude grid node count"),
    "SF076": (4, "1", "BPAC area longitude grid node count"),
    "SF077": (2, "1", "BPAC area latitude grid node spacing "),
    "SF078": (2, "1", "BPAC area longitude grid node spacing "),
    "SF079": ("N", "Bitmask", "Grid node present mask"),
    "SF080": (12, "0.25 TECU", "Area average VTEC"),
    "SF081": (1, "1", "VTEC size indicator"),
    "SF082": (7, "0.25 TECU", "Small VTEC residual "),
    "SF083": (11, "0.25 TECU", "Large VTEC residual "),
    "SF084": (20, "1", "Customer Key ID"),
    "SF085": (4, "1", "Encryption Type"),
    "SF086": (6, "1", "Week of Applicability"),
    "SF087": (4, "1", "Key length"),
    "SF088": ("Key length (SF087)", "1", "Cryptographic Key"),
    "SF089": (5, "1", "Count of Message IDs"),
    "SF090": (4, "1", "Group Authentication Type"),
    "SF091": (4, "1", "Computed Authentication Data (CAD) Length"),
    "SF092": ("CAD length (SF091)", "1", "Computed Authentication Data (CAD)"),
    "SF093": ("38 to 66", "Bitmask", "Galileo satellite mask"),
    "SF094": ("39 to 66", "Bitmask", "BDS satellite mask"),
    "SF095": ("12 to 66", "Bitmask", "QZSS satellite mask"),
    "SF096": (3, "n/a", "Galileo ephemeris type"),
    "SF097": (4, "n/a", "BDS ephemeris type"),
    "SF098": (3, "n/a", "QZSS ephemeris type"),
    "SF099": (10, "1", "Galileo IODnav"),
    "SF100": (8, "1", "BDS IODE/IODC"),
    "SF101": (8, "1", "QZSS IODE"),
    "SF102": ("9 or 16", "Bitmask", "Galileo phase bias mask"),
    "SF103": ("9 or 16", "Bitmask", "BDS phase bias mask"),
    "SF104": ("7 or 12", "Bitmask", "QZSS phase bias mask"),
    "SF105": ("9 or 16", "Bitmask", "Galileo code bias mask"),
    "SF106": ("9 or 16", "Bitmask", "BDS code bias mask"),
    "SF107": ("7 or 12", "Bitmask", "QZSS code bias mask"),
}
