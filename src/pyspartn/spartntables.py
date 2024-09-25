"""
SPARTN Bitmask, Lookup and Decode Constants

Created on 10 Feb 2023

Information Sourced from https://www.spartnformat.org/download/
(available in the public domain) © 2021 u-blox AG. All rights reserved.

:author: semuadmin
"""

SATBITMASKKEY = {
    "GPS": "SF011",
    "GLO": "SF012",
    "GAL": "SF093",
    "BEI": "SF094",
    "QZS": "SF095",
}
"""Satellite PRN bitmask keys"""

SATIODEKEY = {
    "GPS": "SF018",
    "GLO": "SF019",
    "GAL": "SF099",
    "BEI": "SF100",
    "QZS": "SF101",
}
"""Satellite IODE keys"""

SF011_ENUM = {
    0: 32,
    1: 44,
    2: 56,
    3: 64,
}
"""GPS satellite mask length (leftmost 2 bits of SF011)"""

SF012_ENUM = {
    0: 24,
    1: 36,
    2: 48,
    3: 63,
}
"""GLONASS satellite mask length (leftmost 2 bits of SF012)"""

SF093_ENUM = {
    0: 36,
    1: 45,
    2: 54,
    3: 64,
}
"""Galileo satellite mask length (leftmost 2 bits of SF093)"""

SF094_ENUM = {
    0: 37,
    1: 46,
    2: 55,
    3: 64,
}
"""BDS satellite mask length (leftmost 2 bits of SF094)"""

SF095_ENUM = {
    0: 10,
    1: 40,
    2: 48,
    3: 64,
}
"""QZSS satellite mask length (leftmost 2 bits of SF095)"""

SATBITMASKLEN = {
    SATBITMASKKEY["GPS"]: list(SF011_ENUM.values()),
    SATBITMASKKEY["GLO"]: list(SF012_ENUM.values()),
    SATBITMASKKEY["GAL"]: list(SF093_ENUM.values()),
    SATBITMASKKEY["BEI"]: list(SF094_ENUM.values()),
    SATBITMASKKEY["QZS"]: list(SF095_ENUM.values()),
}
"""Satellite PRN bitmask lengths (PRN values are bitmask position + 1)"""

PBBITMASKKEY = {
    "GPS": "SF025",
    "GLO": "SF026",
    "GAL": "SF102",
    "BEI": "SF103",
    "QZS": "SF104",
}
"""Phase bias bitmask keys"""

PBBITMASKLEN = {
    PBBITMASKKEY["GPS"]: (
        [6, 11],
        {
            0: "L1C",
            1: "L2W",
            2: "L2L",
            3: "L5Q",
            # 4-10: spare phase bias
        },
    ),
    PBBITMASKKEY["GLO"]: (
        [5, 9],
        {
            0: "L1C",
            1: "L2C",
            # 2-8: spare phase bias
        },
    ),
    PBBITMASKKEY["GAL"]: (
        [8, 15],
        {
            0: "L1C",
            1: "L5Q",
            2: "L7Q",
            # 3-14: spare phase bias
        },
    ),
    PBBITMASKKEY["BEI"]: (
        [8, 15],
        {
            0: "L2I",
            1: "L5P",
            2: "L7I",
            3: "L6I",
            4: "L1P",
            5: "L7P",
            6: "L8P",
            # 7-14: spare phase bias
        },
    ),
    PBBITMASKKEY["QZS"]: (
        [6, 11],
        {
            0: "L1C",
            1: "L2L",
            2: "L5Q",
            # 3-10: spare phase bias
        },
    ),
}
"""Phase bias bitmask lengths and enumerations"""

CBBITMASKKEY = {
    "GPS": "SF027",
    "GLO": "SF028",
    "GAL": "SF105",
    "BEI": "SF106",
    "QZS": "SF107",
}
"""Code bias bitmask keys"""

CBBITMASKLEN = {
    CBBITMASKKEY["GPS"]: (
        [6, 11],
        {
            0: "C1C",
            1: "C2W",
            2: "C2L",
            3: "C5Q",
            # 4-10: spare code bias
        },
    ),
    CBBITMASKKEY["GLO"]: (
        [5, 9],
        {
            0: "C1C",
            1: "C2C",
            # 2 to 8 : spare code bias
        },
    ),
    CBBITMASKKEY["GAL"]: (
        [8, 15],
        {
            0: "C1C",
            1: "C5Q",
            2: "C7Q",
            # 3-14: spare code bias
        },
    ),
    CBBITMASKKEY["BEI"]: (
        [8, 15],
        {
            0: "C2I",
            1: "C5P",
            2: "C7I",
            3: "C6I",
            4: "C1P",
            5: "C7P",
            6: "C8P",
            # 7-14: spare code bias
        },
    ),
    CBBITMASKKEY["QZS"]: (
        [6, 11],
        {
            0: "C1C",
            1: "C2L",
            2: "C5Q",
            # 3-10: spare code bias
        },
    ),
}
"""Code bias bitmask lengths and enumerations"""

ALN_ENUM = {0: 8, 1: 12, 2: 16, 3: 32, 4: 64}
"""Embedded authorisation length enumeration"""

SF015_ENUM = SF022_ENUM = {
    0: "0 secs",
    1: "1 secs",
    2: "5 secs",
    3: "10 secs",
    4: "30 secs",
    5: "60 secs",
    6: "120 secs",
    7: "320 secs",
}
"""Continuity indicator enumeration"""

SF024_ENUM = {
    0: "unknown",
    1: "0.01 m",
    2: "0.02 m",
    3: "0.05 m",
    4: "0.1 m",
    5: "0.3 m",
    6: "1.0 m",
    7: "> 1.0 m",
}
"""User range error (URE) enumeration"""

SF042_ENUM = {
    0: "unknown",
    1: "<= 0.010 m",
    2: "<= 0.020 m",
    3: "<= 0.040 m",
    4: "<= 0.080 m",
    5: "<= 0.160 m",
    6: "<= 0.320 m",
    7: "> 0.320 m",
}
"""Troposphere quality enumeration"""

SF044_ENUM = {
    0: "Troposphere small coefficient block",
    1: "Troposphere large coefficient block",
}
"""Troposphere polynomial coefficient size indicator"""

SF051_ENUM = {
    0: "Troposphere small residual",
    1: "Tropospherelarge residual",
}
"""Troposphere residual field size"""

SF055_ENUM = {
    0: "Unknown",
    1: "<= 0.03 TECU",
    2: "<= 0.05 TECU",
    3: "<= 0.07 TECU",
    4: "<= 0.14 TECU",
    5: "<= 0.28 TECU",
    6: "<= 0.56 TECU",
    7: "<= 1.12 TECU",
    8: "<= 2.24 TECU",
    9: "<= 4.48 TECU",
    10: "<= 8.96 TECU",
    11: "<= 17.92 TECU",
    12: "<= 35.84 TECU",
    13: "<= 71.68 TECU",
    14: "<= 143.36 TECU",
    15: "> 143.36 TECU",
}
"""Ionosphere quality enumeration"""

SF056_ENUM = {
    0: "Ionosphere small coefficient block",
    1: "Ionosphere large coefficient block",
}
"""Ionosphere polynomial coefficient size indicator"""

SF063_ENUM = {
    0: "Ionosphere small residual",
    1: "Ionosphere medium residual",
    2: "Ionosphere large residual",
    3: "Ionosphere extra large residual",
}
"""Ionosphere residual field size enumeration"""

SF070_ENUM = {
    0: "350 km",
    1: "400 km",
    2: "450 km",
    3: "500 km",
}
"""Ionosphere shell height enumeration"""

SF077_ENUM = SF078_ENUM = {
    0: "2.5 deg",
    1: "5.0 deg",
    2: "10.0 deg",
    3: "15.0 deg",
}
"""BPAC area latitude/longitude grid node spacing enumeration"""

SF081_ENUM = {
    0: "small VTEC residual",
    1: "large VTEC residual",
}
"""VTEC size indicator"""

SF085_ENUM = {
    0: "AES",
    1: "ChaCha12",
    2: "ChaCha20",
    # 3-15 : TBD
}
"""Encryption Type enumeration"""

SF087_ENUM = {  # no bits
    0: 96,
    1: 128,
    2: 192,
    3: 256,
    4: 512,
    # 5-15 : TBD
}
"""Key length enumeration"""

SF090_ENUM = {
    0: "none",
    1: "Ed25519",
    2: "SHA-2",
    3: "SHA-3",
    # 4-15 : TBD
}
"""Group Authentication Type enumeration"""

SF091_ENUM = {  # no bits
    0: 32,
    1: 64,
    2: 96,
    3: 128,
    4: 192,
    5: 256,
    6: 512,
    # 7-15 : TBD
}
"""Computed Authentication Data (CAD) Length enumeration"""

SF096_ENUM = {
    0: "Galileo F/NAV",
    1: "Galileo I/NAV",
    2: "Galileo C/NAV",
    # 3-7: TBD
}
"""Galileo ephemeris type"""

SF097_ENUM = {
    0: "D1 Nav (B1I)",
    1: "D2 Nav (B1I)",
    2: "D1 Nav (B3I)",
    3: "D2 Nav (B3I)",
    4: "B-CNAV1",
    5: "B-CNAV2",
    # 6-15: TBD
}
"""BDS ephemeris type"""

SF098_ENUM = {
    0: "LNAV (L1C/A)",
    1: "CNAV2 (L1C)",
    2: "CNAV (L2C,L5)",
    # 3-7: TBD
}
"""QZSS ephemeris type"""
