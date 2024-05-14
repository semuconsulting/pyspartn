"""
SPARTN Protocol core globals and constants

Created on 10 Feb 2023

Information Sourced from https://www.spartnformat.org/download/
(available in the public domain) © 2021 u-blox AG. All rights reserved.

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

# pylint: disable=line-too-long

from datetime import datetime, timezone

TIMEBASE = datetime(2010, 1, 1, 0, 0, tzinfo=timezone.utc)
ERRRAISE = 2
ERRLOG = 1
ERRIGNORE = 0
VALNONE = 0
VALCRC = 1
VALMSGID = 2
SPARTN_PRE = 0x73
SPARTN_PREB = b"s"
NA = "N/A"

# Attribute types
IN = "IN"  # integer
EN = "EN"  # enumeration
BM = "BM"  # bitmask
FL = "FL"  # float
PRN = "PRN"  # PRN lookup value
PBS = "PBS"  # phase bias value
CBS = "CBS"  # code bias value

# Transient attribute names used to store variable bitmask length flags
NB = "NB_"
STBMLEN = "SatBitmaskLen"
PBBMLEN = "PhaseBiasBitmaskLen"
CBBMLEN = "CodeBiasBitmaskLen"


# SPARTN message types
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

# Datafields used in message definitions
# key (IN, BM, EN): (length in bits, type, resolution or n/a, description)
# key (FL): (length in bits, type, resolution, range minimum, description)
SPARTN_DATA_FIELDS = {
    "PRN": (0, PRN, "n/a", "Satellite PRN"),  # attribute derived by pyspartn
    "PhaseBias": (0, PBS, "n/a", "Phase Bias"),  # attribute derived by pyspartn
    "CodeBias": (0, CBS, "n/a", "Code Bias"),  # attribute derived by pyspartn
    "SF005": (9, IN, 1, "Solution issue of update (SIOU)"),
    "SF008": (1, EN, "n/a", "Yaw present flag"),
    "SF009": (1, IN, 1, "Satellite reference datum"),
    "SF010": (1, IN, "n/a", "End of OCB set (EOS)"),
    STBMLEN: (2, IN, "n/a", "Length of satellite bitmask"),
    "SF011": ("34 to 66", BM, "Bitmask", "GPS Satellite mask"),
    "SF012": ("26 to 65", BM, "Bitmask", "GLONASS Satellite mask"),
    "SF013": (1, IN, "n/a", "Do not use (DNU)"),
    "SF014O": (1, BM, "Bitmask", "Orbit data present flag"),
    "SF014C": (1, BM, "Bitmask", "Clock data present flag"),
    "SF014B": (1, BM, "Bitmask", "Bias data present flag"),
    "SF015": (3, IN, "n/a", "Continuity indicator"),
    "SF016": (2, EN, "n/a", "GPS ephemeris type"),
    "SF017": (2, EN, "n/a", "GLO ephemeris type"),
    "SF018": (8, IN, 1, "GPS IODE"),
    "SF019": (7, IN, 1, "GLO IODE"),
    "SF020R": (14, FL, 0.002, -16.382, "Satellite radial corrections"),
    "SF020A": (14, FL, 0.002, -16.382, "Satellite along-track corrections"),
    "SF020C": (14, FL, 0.002, -16.382, "Satellite cross-track corrections"),
    "SF020CK": (14, FL, 0.002, -16.382, "Satellite clock corrections"),
    "SF020PB": (14, FL, 0.002, -16.382, "Phase bias correction"),
    "SF021": (6, FL, 6, 0, "Satellite yaw"),
    "SF022": (3, IN, "n/a", "IODE continuity"),
    "SF023": (1, EN, "n/a", "Fix flag"),
    "SF024": (3, IN, "n/a", "User range error (URE)"),
    PBBMLEN: (1, IN, "n/a", "Length of phase bias bitmask"),
    "SF025": ("7 or 12", BM, "bitmask", "GPS phase bias mask"),
    "SF026": ("6 or 10", BM, "bitmask", "GLONASS phase bias mask"),
    CBBMLEN: (1, IN, "n/a", "Length of code bias bitmask"),
    "SF027": ("7 or 12", BM, "bitmask", "GPS code bias mask"),
    "SF028": ("6 or 10", BM, "bitmask", "GLONASS code bias mask"),
    "SF029": (11, FL, 0.02, -20.46, "Code bias correction"),
    "SF030": (5, IN, 1, "Area Count"),  # NB: area count = SF030 + 1
    "SF031": (8, IN, 1, "Area ID"),
    "SF032": (11, FL, 0.1, -90, "Area reference latitude"),
    "SF033": (12, FL, 0.1, -180, "Area reference longitude"),
    "SF034": (3, IN, 1, "Area latitude grid node count"),
    "SF035": (3, IN, 1, "Area longitude grid node count"),
    "SF036": (5, FL, 0.1, 0.1, "Area latitude grid node spacing"),
    "SF037": (5, FL, 0.1, 0.1, "Area longitude grid node spacing"),
    "SF039": (7, IN, 1, "Number of grid points present"),
    "SF040": (2, IN, 1, "Poly/Grid block present indicator"),
    "SF040T": (2, IN, 1, "Troposphere Poly/Grid block present indicator"),
    "SF040I": (2, IN, 1, "Ionoshere Poly/Grid block present indicator"),
    "SF041": (3, EN, 1, "Troposphere equation type"),
    "SF042": (3, IN, 1, "Troposphere quality"),
    "SF043": (8, FL, 0.004, -0.508, "Area average vertical hydrostatic delay"),
    "SF044": (1, IN, 1, "Troposphere polynomial coefficient size indicator"),
    "SF045": (7, FL, 0.004, -0.252, "Small troposphere coefficient T00"),
    "SF046a": (7, FL, 0.001, -0.063, "Small troposphere coefficient T01"),
    "SF046b": (7, FL, 0.001, -0.063, "Small troposphere coefficient T10"),
    "SF047": (9, FL, 0.0002, -0.0510, "Small troposphere coefficient T11"),
    "SF048": (9, FL, 0.004, -1.020, "Large troposphere coefficient T00"),
    "SF049a": (9, FL, 0.001, -0.255, "Large troposphere coefficient T01"),
    "SF049b": (9, FL, 0.001, -0.255, "Large troposphere coefficient T10"),
    "SF050": (11, FL, 0.0002, -0.2046, "Large troposphere coefficient T11"),
    "SF051": (1, IN, 1, "Troposphere residual field size"),
    "SF052": (6, FL, 0.004, -0.124, "Small troposphere residual zenith delay"),
    "SF053": (8, FL, 0.004, -0.508, "Large troposphere residual zenith delay"),
    "SF054": (3, EN, 1, "Ionosphere equation type"),
    "SF055": (4, IN, 1, "Ionosphere quality"),
    "SF056": (1, IN, 1, "Ionosphere polynomial coefficient size indicator"),
    "SF057": (12, FL, 0.04, -81.88, "Small ionosphere coefficient C00"),
    "SF058a": (12, FL, 0.008, -16.376, "Small ionosphere coefficient C01"),
    "SF058b": (12, FL, 0.008, -16.376, "Small ionosphere coefficient C10"),
    "SF059": (13, FL, 0.002, -8.190, "Small ionosphere coefficient C11"),
    "SF060": (14, FL, 0.04, -327.64, "Large ionosphere coefficient C00"),
    "SF061a": (14, FL, 0.008, -65.528, "Large ionosphere coefficient C01"),
    "SF061b": (14, FL, 0.008, -65.528, "Large ionosphere coefficient C10"),
    "SF062": (15, FL, 0.002, -32.766, "Large ionosphere coefficient C11"),
    "SF063": (2, IN, 1, "Ionosphere residual field size"),
    "SF064": (4, FL, 0.04, -0.28, "Small ionosphere residual slant delay"),
    "SF065": (7, FL, 0.04, -2.52, "Medium ionosphere residual slant delay"),
    "SF066": (10, FL, 0.04, -20.44, "Large ionosphere residual slant delay"),
    "SF067": (14, FL, 0.04, -327.64, "Extra-large ionosphere residual slant delay"),
    "SF068": (4, IN, 1, "Area Issue of Update (AIOU)"),
    "SF069": (1, IN, "n/a", "Reserved"),
    "SF070": (2, IN, 1, "Ionosphere shell height"),
    "SF071": (2, IN, 1, "BPAC area count"),
    "SF072": (2, IN, 1, "BPAC area ID"),
    "SF073": (8, FL, 1.0, -85.0, "BPAC area reference latitude"),
    "SF074": (9, FL, 1.0, -180.0, "BPAC area reference longitude"),
    "SF075": (4, IN, 1, "BPAC area latitude grid node count"),
    "SF076": (4, IN, 1, "BPAC area longitude grid node count"),
    "SF077": (2, IN, 1, "BPAC area latitude grid node spacing "),
    "SF078": (2, IN, 1, "BPAC area longitude grid node spacing "),
    "SF079": ("N", BM, "Bitmask", "Grid node present mask"),
    "SF080": (12, FL, 0.25, -511.75, "Area average VTEC"),
    "SF081": (1, IN, 1, "VTEC size indicator"),
    "SF082": (7, FL, 0.25, -15.75, "Small VTEC residual "),
    "SF083": (11, FL, 0.25, -255.75, "Large VTEC residual "),
    "SF084": (20, IN, 1, "Customer Key ID"),
    "SF085": (4, EN, 1, "Encryption Type"),
    "SF085a": (4, EN, 1, "Encryption Type"),
    "SF086": (6, IN, 1, "Week of Applicability"),
    "SF087": (4, IN, 1, "Key length"),
    "SF088": ("Key length (SF087)", IN, "1", "Cryptographic Key"),
    "SF089": (5, IN, 1, "Count of Message IDs"),
    "SF090": (4, EN, 1, "Group Authentication Type"),
    "SF091": (4, IN, 1, "Computed Authentication Data (CAD) Length"),
    "SF092": ("CAD length (SF091)", IN, 1, "Computed Authentication Data (CAD)"),
    "SF093": ("38 to 66", BM, "Bitmask", "Galileo satellite mask"),
    "SF094": ("39 to 66", BM, "Bitmask", "BDS satellite mask"),
    "SF095": ("12 to 66", BM, "Bitmask", "QZSS satellite mask"),
    "SF096": (3, EN, "n/a", "Galileo ephemeris type"),
    "SF097": (4, EN, "n/a", "BDS ephemeris type"),
    "SF098": (3, EN, "n/a", "QZSS ephemeris type"),
    "SF099": (10, IN, 1, "Galileo IODnav"),
    "SF100": (8, IN, 1, "BDS IODE/IODC"),
    "SF101": (8, IN, 1, "QZSS IODE"),
    "SF102": ("9 or 16", BM, "Bitmask", "Galileo phase bias mask"),
    "SF103": ("9 or 16", BM, "Bitmask", "BDS phase bias mask"),
    "SF104": ("7 or 12", BM, "Bitmask", "QZSS phase bias mask"),
    "SF105": ("9 or 16", BM, "Bitmask", "Galileo code bias mask"),
    "SF106": ("9 or 16", BM, "Bitmask", "BDS code bias mask"),
    "SF107": ("7 or 12", BM, "Bitmask", "QZSS code bias mask"),
}
