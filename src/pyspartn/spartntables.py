"""
SPARTN Lookup and Decode Tables

Created on 10 Feb 2023

Information Sourced from https://www.spartnformat.org/download/
(available in the public domain) © 2021 u-blox AG. All rights reserved.

:author: semuadmin
"""

SF015 = SF022 = {
    0: "0 secs",
    1: "1 secs",
    2: "5 secs",
    3: "10 secs",
    4: "30 secs",
    5: "60 secs",
    6: "120 secs",
    7: "320 secs",
}

SF024 = {
    0: "unknown",
    1: "0.01 m",
    2: "0.02 m",
    3: "0.05 m",
    4: "0.1 m",
    5: "0.3 m",
    6: "1.0 m",
    7: "> 1.0 m",
}

SF042 = {
    0: "unknown",
    1: "<=0.010 m",
    2: "<=0.020 m",
    3: "<=0.040 m",
    4: "<=0.080 m",
    5: "<=0.160 m",
    6: "<=0.320 m",
    7: "> 0.320 m",
}

SF055 = {
    0: "Unknown",
    1: "<=0.03 TECU",
    2: "<=0.05 TECU",
    3: "<=0.07 TECU",
    4: "<=0.14 TECU",
    5: "<=0.28 TECU",
    6: "<=0.56 TECU",
    7: "<=1.12 TECU",
    8: "<=2.24 TECU",
    9: "<=4.48 TECU",
    10: "<=8.96 TECU",
    11: "<=17.92 TECU",
    12: "<=35.84 TECU",
    13: "<=71.68 TECU",
    14: "<=143.36 TECU",
    15: ">143.36 TECU",
}

SF070 = {
    0: "350 km",
    1: "400 km",
    2: "450 km",
    3: "500 km",
}

SF077 = SF078 = {
    0: "2.5 deg",
    1: "5.0 deg",
    2: "10.0 deg",
    3: "15.0 deg",
}

SF081 = {
    0: "small",
    1: "large",
}

SF085 = {
    0: "AES",
    1: "ChaCha12",
    2: "ChaCha20",
}

SF090 = {
    0: "none",
    1: "Ed25519",
    2: "SHA-2",
    3: "SHA-3",
}

SF096 = {
    0: "Galileo F/NAV",
    1: "Galileo I/NAV",
    2: "Galileo C/NAV",
}

SF097 = {
    0: "D1 Nav (B1I)",
    1: "D2 Nav (B1I)",
    2: "D1 Nav (B3I)",
    3: "D2 Nav (B3I)",
    4: "B-CNAV1",
    5: "B-CNAV2",
}

SF098 = {
    0: "LNAV (L1C/A)",
    1: "CNAV2(L1C)",
    2: "CNAV (L2C,L5)",
}
