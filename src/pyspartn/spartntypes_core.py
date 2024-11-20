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
""" Initial epoch for SPARTN protocol. """
DEFAULTKEY = "abcd1234abcd1234abcd1234abcd1234"  # nominal 32-char hex key
""" Nominal 32-char hex key. """
ERRRAISE = 2
""" (Re)raise errors """
ERRLOG = 1
""" Log errors and continue """
ERRIGNORE = 0
""" Ignore errors """
VALNONE = 0
""" No validation of CRC or Message ID """
VALCRC = 1
""" Valildate CRC checksum """
VALMSGID = 2
""" Validate Message ID """
SPARTN_PRE = 0x73
SPARTN_PREB = b"s"
""" SPARTN preamble byte """
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
# key (IN, BM, EN): (type length in bits, resolution or n/a, description)
# key (FL): (type, length in bits, resolution, range minimum, [offset], description)
SPARTN_DATA_FIELDS = {
    PRN: (PRN, 0, "n/a", "Satellite PRN"),
    "PhaseBias": (PBS, 0, "n/a", "Phase Bias"),
    "CodeBias": (CBS, 0, "n/a", "Code Bias"),
    "SF005": (IN, 9, 1, "Solution issue of update (SIOU)"),
    "SF008": (EN, 1, "n/a", "Yaw present flag"),
    "SF009": (IN, 1, 1, "Satellite reference datum"),
    "SF010": (IN, 1, "n/a", "End of OCB set (EOS)"),
    STBMLEN: (IN, 2, "n/a", "Length of satellite bitmask"),
    "SF011": (BM, "34 to 66", "Bitmask", "GPS Satellite mask"),
    "SF012": (BM, "26 to 65", "Bitmask", "GLONASS Satellite mask"),
    "SF013": (IN, 1, "n/a", "Do not use (DNU)"),
    "SF014O": (BM, 1, "Bitmask", "Orbit data present flag"),
    "SF014C": (BM, 1, "Bitmask", "Clock data present flag"),
    "SF014B": (BM, 1, "Bitmask", "Bias data present flag"),
    "SF015": (IN, 3, "n/a", "Continuity indicator"),
    "SF016": (EN, 2, "n/a", "GPS ephemeris type"),
    "SF017": (EN, 2, "n/a", "GLO ephemeris type"),
    "SF018": (IN, 8, 1, "GPS IODE"),
    "SF019": (IN, 7, 1, "GLO IODE"),
    "SF020R": (FL, 14, 0.002, -16.382, "Satellite radial corrections"),
    "SF020A": (FL, 14, 0.002, -16.382, "Satellite along-track corrections"),
    "SF020C": (FL, 14, 0.002, -16.382, "Satellite cross-track corrections"),
    "SF020CK": (FL, 14, 0.002, -16.382, "Satellite clock corrections"),
    "SF020PB": (FL, 14, 0.002, -16.382, "Phase bias correction"),
    "SF021": (FL, 6, 6, 0, "Satellite yaw"),
    "SF022": (IN, 3, "n/a", "IODE continuity"),
    "SF023": (EN, 1, "n/a", "Fix flag"),
    "SF024": (IN, 3, "n/a", "User range error (URE)"),
    PBBMLEN: (IN, 1, "n/a", "Length of phase bias bitmask"),
    "SF025": (BM, "7 or 12", "bitmask", "GPS phase bias mask"),
    "SF026": (BM, "6 or 10", "bitmask", "GLONASS phase bias mask"),
    CBBMLEN: (IN, 1, "n/a", "Length of code bias bitmask"),
    "SF027": (BM, "7 or 12", "bitmask", "GPS code bias mask"),
    "SF028": (BM, "6 or 10", "bitmask", "GLONASS code bias mask"),
    "SF029": (FL, 11, 0.02, -20.46, "Code bias correction"),
    "SF030": (IN, 5, 1, "Area Count"),
    "SF031": (IN, 8, 1, "Area ID"),
    "SF032": (FL, 11, 0.1, -90, "Area reference latitude"),
    "SF033": (FL, 12, 0.1, -180, "Area reference longitude"),
    "SF034": (IN, 3, 1, "Area latitude grid node count"),
    "SF035": (IN, 3, 1, "Area longitude grid node count"),
    "SF036": (FL, 5, 0.1, 0.1, "Area latitude grid node spacing"),
    "SF037": (FL, 5, 0.1, 0.1, "Area longitude grid node spacing"),
    "SF039": (IN, 7, 1, "Number of grid points present"),
    "SF040": (IN, 2, 1, "Poly/Grid block present indicator"),
    "SF040T": (IN, 2, 1, "Troposphere Poly/Grid block present indicator"),
    "SF040I": (IN, 2, 1, "Ionoshere Poly/Grid block present indicator"),
    "SF041": (EN, 3, 1, "Troposphere equation type"),
    "SF042": (IN, 3, 1, "Troposphere quality"),
    "SF043": (FL, 8, 0.004, -0.508, 2.3, "Area average vertical hydrostatic delay"),
    "SF044": (IN, 1, 1, "Troposphere polynomial coefficient size indicator"),
    "SF045": (FL, 7, 0.004, -0.252, 0.252, "Small troposphere coefficient T00"),
    "SF046a": (FL, 7, 0.001, -0.063, "Small troposphere coefficient T01"),
    "SF046b": (FL, 7, 0.001, -0.063, "Small troposphere coefficient T10"),
    "SF047": (FL, 9, 0.0002, -0.051, "Small troposphere coefficient T11"),
    "SF048": (FL, 9, 0.004, -1.02, 0.252, "Large troposphere coefficient T00"),
    "SF049a": (FL, 9, 0.001, -0.255, "Large troposphere coefficient T01"),
    "SF049b": (FL, 9, 0.001, -0.255, "Large troposphere coefficient T10"),
    "SF050": (FL, 11, 0.0002, -0.2046, "Large troposphere coefficient T11"),
    "SF051": (IN, 1, 1, "Troposphere residual field size"),
    "SF052": (FL, 6, 0.004, -0.124, "Small troposphere residual zenith delay"),
    "SF053": (FL, 8, 0.004, -0.508, "Large troposphere residual zenith delay"),
    "SF054": (EN, 3, 1, "Ionosphere equation type"),
    "SF055": (IN, 4, 1, "Ionosphere quality"),
    "SF056": (IN, 1, 1, "Ionosphere polynomial coefficient size indicator"),
    "SF057": (FL, 12, 0.04, -81.88, "Small ionosphere coefficient C00"),
    "SF058a": (FL, 12, 0.008, -16.376, "Small ionosphere coefficient C01"),
    "SF058b": (FL, 12, 0.008, -16.376, "Small ionosphere coefficient C10"),
    "SF059": (FL, 13, 0.002, -8.19, "Small ionosphere coefficient C11"),
    "SF060": (FL, 14, 0.04, -327.64, "Large ionosphere coefficient C00"),
    "SF061a": (FL, 14, 0.008, -65.528, "Large ionosphere coefficient C01"),
    "SF061b": (FL, 14, 0.008, -65.528, "Large ionosphere coefficient C10"),
    "SF062": (FL, 15, 0.002, -32.766, "Large ionosphere coefficient C11"),
    "SF063": (IN, 2, 1, "Ionosphere residual field size"),
    "SF064": (FL, 4, 0.04, -0.28, "Small ionosphere residual slant delay"),
    "SF065": (FL, 7, 0.04, -2.52, "Medium ionosphere residual slant delay"),
    "SF066": (FL, 10, 0.04, -20.44, "Large ionosphere residual slant delay"),
    "SF067": (FL, 14, 0.04, -327.64, "Extra-large ionosphere residual slant delay"),
    "SF068": (IN, 4, 1, "Area Issue of Update (AIOU)"),
    "SF069": (IN, 1, "n/a", "Reserved"),
    "SF070": (IN, 2, 1, "Ionosphere shell height"),
    "SF071": (IN, 2, 1, "BPAC area count"),
    "SF072": (IN, 2, 1, "BPAC area ID"),
    "SF073": (FL, 8, 1.0, -85.0, "BPAC area reference latitude"),
    "SF074": (FL, 9, 1.0, -180.0, "BPAC area reference longitude"),
    "SF075": (IN, 4, 1, "BPAC area latitude grid node count"),
    "SF076": (IN, 4, 1, "BPAC area longitude grid node count"),
    "SF077": (IN, 2, 1, "BPAC area latitude grid node spacing"),
    "SF078": (IN, 2, 1, "BPAC area longitude grid node spacing"),
    "SF079": (BM, "N", "Bitmask", "Grid node present mask"),
    "SF080": (FL, 12, 0.25, -511.75, "Area average VTEC"),
    "SF081": (IN, 1, 1, "VTEC size indicator"),
    "SF082": (FL, 7, 0.25, -15.75, "Small VTEC residual"),
    "SF083": (FL, 11, 0.25, -255.75, "Large VTEC residual"),
    "SF084": (IN, 20, 1, "Customer Key ID"),
    "SF085": (EN, 4, 1, "Encryption Type"),
    "SF085a": (EN, 4, 1, "Encryption Type"),
    "SF086": (IN, 6, 1, "Week of Applicability"),
    "SF087": (IN, 4, 1, "Key length"),
    "SF088": (IN, "Key length (SF087)", "1", "Cryptographic Key"),
    "SF089": (IN, 5, 1, "Count of Message IDs"),
    "SF090": (EN, 4, 1, "Group Authentication Type"),
    "SF091": (IN, 4, 1, "Computed Authentication Data (CAD) Length"),
    "SF092": (IN, "CAD length (SF091)", 1, "Computed Authentication Data (CAD)"),
    "SF093": (BM, "38 to 66", "Bitmask", "Galileo satellite mask"),
    "SF094": (BM, "39 to 66", "Bitmask", "BDS satellite mask"),
    "SF095": (BM, "12 to 66", "Bitmask", "QZSS satellite mask"),
    "SF096": (EN, 3, "n/a", "Galileo ephemeris type"),
    "SF097": (EN, 4, "n/a", "BDS ephemeris type"),
    "SF098": (EN, 3, "n/a", "QZSS ephemeris type"),
    "SF099": (IN, 10, 1, "Galileo IODnav"),
    "SF100": (IN, 8, 1, "BDS IODE/IODC"),
    "SF101": (IN, 8, 1, "QZSS IODE"),
    "SF102": (BM, "9 or 16", "Bitmask", "Galileo phase bias mask"),
    "SF103": (BM, "9 or 16", "Bitmask", "BDS phase bias mask"),
    "SF104": (BM, "7 or 12", "Bitmask", "QZSS phase bias mask"),
    "SF105": (BM, "9 or 16", "Bitmask", "Galileo code bias mask"),
    "SF106": (BM, "9 or 16", "Bitmask", "BDS code bias mask"),
    "SF107": (BM, "7 or 12", "Bitmask", "QZSS code bias mask"),
}
