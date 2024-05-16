"""
SPARTN Bitmask, Lookup and Decode Tables

Created on 10 Feb 2023

Information Sourced from https://www.spartnformat.org/download/
(available in the public domain) © 2021 u-blox AG. All rights reserved.

:author: semuadmin
"""

# satellite PRN bitmask keys
SATBITMASKKEY = {
    "GPS": "SF011",
    "GLO": "SF012",
    "GAL": "SF093",
    "BEI": "SF094",
    "QZS": "SF095",
}
# satellite IODE keys
SATIODEKEY = {
    "GPS": "SF018",
    "GLO": "SF019",
    "GAL": "SF099",
    "BEI": "SF100",
    "QZS": "SF101",
}
# satellite PRN bitmask lengths (PRN values are bitmask position + 1)
SATBITMASKLEN = {
    "SF011": [32, 44, 56, 64],
    "SF012": [24, 36, 48, 63],
    "SF093": [36, 45, 54, 64],
    "SF094": [37, 46, 55, 64],
    "SF095": [10, 40, 48, 64],
}

# phase bias bitmask keys
PBBITMASKKEY = {
    "GPS": "SF025",
    "GLO": "SF026",
    "GAL": "SF102",
    "BEI": "SF103",
    "QZS": "SF104",
}
# phase bias bitmask lengths, phase bias values
PBBITMASKLEN = {
    "SF025": (  # GPS
        [6, 11],
        {
            0: "L1C",
            1: "L2W",
            2: "L2L",
            3: "L5Q",
            # 4-10: spare phase bias
        },
    ),
    "SF026": (  # GLO
        [5, 9],
        {
            0: "L1C",
            1: "L2C",
            # 2-8: spare phase bias
        },
    ),
    "SF102": (  # GAL
        [8, 15],
        {
            0: "L1C",
            1: "L5Q",
            2: "L7Q",
            # 3-14: spare phase bias
        },
    ),
    "SF103": (  # BEI
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
    "SF104": (  # QZS
        [6, 11],
        {
            0: "L1C",
            1: "L2L",
            2: "L5Q",
            # 3-10: spare phase bias
        },
    ),
}

# code bias bitmask keys
CBBITMASKKEY = {
    "GPS": "SF027",
    "GLO": "SF028",
    "GAL": "SF105",
    "BEI": "SF106",
    "QZS": "SF107",
}
# code bias bitmask lengths, code bias values
CBBITMASKLEN = {
    "SF027": (  # GPS
        [6, 11],
        {
            0: "C1C",
            1: "C2W",
            2: "C2L",
            3: "C5Q",
            # 4-10: spare code bias
        },
    ),
    "SF028": (  # GLO
        [5, 9],
        {
            0: "C1C",
            1: "C2C",
            # 2 to 8 : spare code bias
        },
    ),
    "SF105": (  # GAL
        [8, 15],
        {
            0: "C1C",
            1: "C5Q",
            2: "C7Q",
            # 3-14: spare code bias
        },
    ),
    "SF106": (  # BEI
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
    "SF107": (  # QZS
        [6, 11],
        {
            0: "C1C",
            1: "C2L",
            2: "C5Q",
            # 3-10: spare code bias
        },
    ),
}

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

SF044_ENUM = {
    0: "Troposphere small coefficient block",
    1: "Troposphere large coefficient block",
}

SF051_ENUM = {
    0: "Troposphere small residual",
    1: "Tropospherelarge residual",
}

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

SF056_ENUM = {
    0: "Ionosphere small coefficient block",
    1: "Ionosphere large coefficient block",
}

SF063_ENUM = {
    0: "Ionosphere small residual",
    1: "Ionosphere medium residual",
    2: "Ionosphere large residual",
    3: "Ionosphere extra large residual",
}

SF070_ENUM = {
    0: "350 km",
    1: "400 km",
    2: "450 km",
    3: "500 km",
}

SF077_ENUM = SF078_ENUM = {
    0: "2.5 deg",
    1: "5.0 deg",
    2: "10.0 deg",
    3: "15.0 deg",
}

SF081_ENUM = {
    0: "small VTEC residual",
    1: "large VTEC residual",
}

SF085_ENUM = {
    0: "AES",
    1: "ChaCha12",
    2: "ChaCha20",
    # 3-15 : TBD
}

SF087_ENUM = {  # no bits
    0: 96,
    1: 128,
    2: 192,
    3: 256,
    4: 512,
    # 5-15 : TBD
}


SF090_ENUM = {
    0: "none",
    1: "Ed25519",
    2: "SHA-2",
    3: "SHA-3",
    # 4-15 : TBD
}

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

SF093_ENUM = {  # leftmost 2 bits
    0: 36,
    1: 45,
    2: 54,
    3: 64,
}

SF094_ENUM = {  # leftmost 2 bits
    0: 37,
    1: 46,
    2: 55,
    3: 64,
}

SF095_ENUM = {  # leftmost 2 bits
    0: 10,
    1: 40,
    2: 48,
    3: 64,
}

SF096_ENUM = {
    0: "Galileo F/NAV",
    1: "Galileo I/NAV",
    2: "Galileo C/NAV",
    # 3-7: TBD
}

SF097_ENUM = {
    0: "D1 Nav (B1I)",
    1: "D2 Nav (B1I)",
    2: "D1 Nav (B3I)",
    3: "D2 Nav (B3I)",
    4: "B-CNAV1",
    5: "B-CNAV2",
    # 6-15: TBD
}

SF098_ENUM = {
    0: "LNAV (L1C/A)",
    1: "CNAV2 (L1C)",
    2: "CNAV (L2C,L5)",
    # 3-7: TBD
}
