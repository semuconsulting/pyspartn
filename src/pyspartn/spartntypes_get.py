"""
SPARTN Protocol core globals and constants

Created on 10 Feb 2023

Information Sourced from https://www.spartnformat.org/download/
(available in the public domain) © 2021 u-blox AG. All rights reserved.

Payload definitions are contained in a series of dictionaries.
Repeating and conditional elements are defined as a tuple of
(element size/presence designator, element dictionary). The element
size/presence designator can take one of the following forms:

*Repeating elements:*
 - an integer representing the fixed size of the repeating element N.
 - a string representing the name of a preceding attribute containing
   the size of the repeating element N (note that in some cases the
   attribute represents N - 1) e.g.

.. code-block:: python

  "group": (  # repeating group * (SF030 + 1)
      "SF030",
      {
          "SF031": "Area ID",
          etc ...
      },
  )

*Conditional elements:*
 - a tuple containing a string and either a single value or a list of values,
   representing the name of a preceding attribute and the value(s) it must take
   in order for the optional element to be present e.g.

.. code-block:: python

  "optSF041-12": (
      ("SF041+1", [1, 2]),  # if SF041I in 1,2
      {
          "SF055": "Ionosphere quality",
          etc ...
      }
  )

An 'NB' prefix indicates that the element size is given by the number of set bits
in the attribute, rather than its integer value e.g.
'NB + "SF011"' -> if SF011 = 0b0101101, the size of the repeating element is 4.

A '+1' or '+2' suffix indicates that the attribute name must be suffixed
with the specified number of nested element indices e.g. 'SF041+1' -> 'SF041_01'

In some instances, the size of the repeating element must be derived from
multiple attributes. In these cases the element size is denoted by a composite
attribute name which is calculated within `spartnmessage.py` e.g. 'PBBMLEN'

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

# pylint: disable=too-many-lines, line-too-long

from pyspartn.spartntypes_core import CBBMLEN, NB, PBBMLEN, PRN, STBMLEN

OCB_HDR = {  # OCB Header
    "SF005": "Solution issue of update (SIOU)",
    "SF010": "End of set",
    "SF069": "Reserved",
    "SF008": "Yaw present flag",
    "SF009": "Satellite reference datum",
}

HPAC_HDR = {  # HPAC Header
    "SF005": "Solution issue of update (SIOU)",
    "SF068": "Area issue of update (AIOU)",
    "SF069": "Reserved",
    "SF030": "Area count",  # NB: N - 1
}

OCB_SAT_FLAGS = {  # table 6.4
    PRN: "Satellite PRN",
    "SF014O": "Orbit data present flag",
    "SF014C": "Clock data present flag",
    "SF014B": "Bias data present flag",
    "SF015": "Continuity indicator",
}

OCB_ORBIT_BLOCK = {  # part of table 6.5 Orbit Block
    "SF020R": "Orbit radial correction",
    "SF020A": "Orbit along-track correction",
    "SF020C": "Orbit cross-track correction",
    "optSF008-1": (
        ("SF008", 1),  # if SF008 = 1
        {
            "SF021": "Satellite yaw",
        },
    ),
}

OCB_CLOCK_BLOCK = {  # table 6.6 Clock Block
    "optClock": (
        ("SF014C+1", 1),  # if SF014C = 1
        {
            "SF022": "IODE continuity",
            "SF020CK": "Clock correction",
            "SF024": "User range error",
        },
    ),
}

PHAS_BIAS_BLOCK = {  # table 6.12 Phase Bias Block
    "PhaseBias": "Phase Bias type",
    "SF023": "Fix flag",
    "SF015": "Continuity indicator",
    "SF020PB": "Phase bias correction",
}

CODE_BIAS_BLOCK = {  # tables 6.7 - 6.12
    "CodeBias": "Code Bias type",
    "SF029": "Code bias correction",
}

AREA_DATA_BLOCK = {  # table 6.15 Area Data Block
    "SF031": "Area ID",
    "SF039": "Number of grid points present",
    "SF040T": "Tropo blocks indicator",
    "SF040I": "Iono blocks indicator",
}

TROP_DATA_BLOCK = {  # table 6.16 Troposphere Data Block
    "optSF040T-12": (
        ("SF040T+1", [1, 2]),  # if SF040T in 1,2
        {
            "SF041": "Troposhere equation type",
            "SF042": "Troposphere quality",
            "SF043": "Area average vertical hydrostatic delay",
            "SF044": "Troposphere polynomial coefficient size indicator",
            "optSF044-0": (
                ("SF044+1", 0),  # if SF044 = 0 table 6.17
                {
                    "SF045": "Troposphere coefficient T00",
                    "optSF041-12": (
                        ("SF041+1", [1, 2]),  # if SF041 in 1,2
                        {
                            "SF046a": "Troposphere coefficient T01",
                            "SF046b": "Troposphere coefficient T10",
                        },
                    ),
                    "optSF041-2": (
                        ("SF041+1", 2),  # if SF041 = 2
                        {
                            "SF047": "Troposphere coefficient T11",
                        },
                    ),
                },
            ),
            "optSF044-1": (
                ("SF044+1", 1),  # if SF044 = 1 table 6.18
                {
                    "SF048": "Troposphere coefficient T00",
                    "optSF041-12": (
                        ("SF041+1", [1, 2]),  # if SF041 in 1,2
                        {
                            "SF049a": "Troposphere coefficient T01",
                            "SF049b": "Troposphere coefficient T10",
                        },
                    ),
                    "optSF041-2": (
                        ("SF041+1", 2),  # if SF041 = 2
                        {
                            "SF050": "Troposphere coefficient T11",
                        },
                    ),
                },
            ),
        },
    ),
    "optSF040T-2": (  # if SF040T = 2
        ("SF040T+1", 2),  # if SF040T = 2
        {
            "SF051": "Troposphere residual field size",
            "optSF051-0": (
                ("SF051", 0),  # if SF051 = 0
                {"SF052": "Troposphere grid residuals"},
            ),
            "optSF051-1": (  # if SF051 = 1
                ("SF051", 1),  # if SF051 = 1
                {"SF053": "Troposphere grid residuals"},
            ),
        },
    ),
}

ION_SAT_BLOCK = {  # table 6.20 Ionosphere Satellite Block
    "optSF041-12": (
        ("SF041+1", [1, 2]),  # if SF041I in 1,2
        {
            PRN: "Satellite PRN",
            "SF055": "Ionosphere quality",
            "SF056": "Ionosphere polynomial coefficient size indicator",
            "optSF056-0": (
                ("SF056+2", 0),  # if SF056 = 0 table 6.21
                {
                    "SF057": "Ionosphere coefficient C00",
                    "optSF054-12": (
                        ("SF054+1", [1, 2]),  # if SF054 in 1,2
                        {
                            "SF058a": "Ionosphere coefficient C01",
                            "SF058b": "Ionosphere coefficient C10",
                        },
                    ),
                    "optSF054-2": (
                        ("SF054+1", 2),  # if SF054 = 2
                        {
                            "SF059": "Ionosphere coefficient C11",
                        },
                    ),
                },
            ),
            "optSF056-1": (
                ("SF056+2", 1),  # if SF056 = 1 table 6.22
                {
                    "SF060": "Ionosphere coefficient C00",
                    "optSF054-12": (
                        ("SF054+1", [1, 2]),  # if SF054 in 1,2
                        {
                            "SF061a": "Ionosphere coefficient C01",
                            "SF061b": "Ionosphere coefficient C10",
                        },
                    ),
                    "optSF054-2": (
                        ("SF054+1", 2),  # if SF054 = 2
                        {
                            "SF062": "Ionosphere coefficient C11",
                        },
                    ),
                },
            ),
        },
    ),
    "optSF041-2": (
        ("SF041+1", 2),  # if SF041I = 2
        {
            "SF063": "Ionosphere residual field size",
            "optSF063-0": (
                ("SF063", 0),  # if SF063 = 0
                {"SF064": "Ionosphere grid residuals"},
            ),
            "optSF063-1": (
                ("SF063", 1),  # if SF063 = 1
                {"SF065": "Ionosphere grid residuals"},
            ),
            "optSF063-2": (
                ("SF063", 2),  # if SF063 = 2
                {"SF066": "Ionosphere grid residuals"},
            ),
            "optSF063-3": (
                ("SF063", 3),  # if SF063 = 3
                {"SF067": "Ionosphere grid residuals"},
            ),
        },
    ),
}

# ************************************************************************
# SPARTN MESSAGE PAYLOAD DEFINITIONS (NB: PAYLOAD MUST BE DECRYPTED FIRST)
# ************************************************************************

SPARTN_PAYLOADS_GET = {
    # ********************************************************************
    # OCB
    # ********************************************************************
    "SPARTN-1X-OCB-GPS": {
        **OCB_HDR,
        "SF016": "GPS Ephemeris type",
        STBMLEN: "GPS Satellite mask length",
        "SF011": "GPS Satellite mask",
        "groupSat": (  # Satellite Block table 6.4
            NB + "SF011",  # repeating group * num bits set in SF011
            {
                "SF013": "Do not use (DNU)",
                "optSat": (
                    ("SF013+1", 0),  # if SF013 = 0
                    {
                        **OCB_SAT_FLAGS,
                        "optOrbit": (  # # table 6.5 Orbit Block
                            ("SF014O+1", 1),  # if SF014O = 1
                            {
                                "SF018": "GPS IODE",
                                **OCB_ORBIT_BLOCK,
                            },
                        ),
                        **OCB_CLOCK_BLOCK,
                        "optBias": (
                            ("SF014B+1", 1),  # if SF014B = 1
                            {
                                PBBMLEN: "Phase bias mask length",
                                "SF025": "GPS phase bias mask",
                                "groupSF025-BITS": (
                                    NB
                                    + "SF025+1",  # repeating group * num bits set in SF025
                                    {
                                        **PHAS_BIAS_BLOCK,
                                    },
                                ),
                                CBBMLEN: "Code bias mask length",
                                "SF027": "GPS code bias mask",
                                "groupSF027-BITS": (
                                    NB
                                    + "SF027+1",  # repeating group * num bits set in SF027
                                    {
                                        **CODE_BIAS_BLOCK,
                                    },
                                ),
                            },
                        ),
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-OCB-GLO": {
        **OCB_HDR,
        "SF017": "GLO Ephemeris type",
        STBMLEN: "GPS Satellite mask length",
        "SF012": "GLO Satellite mask",
        "groupSat": (  # Satellite Block table 6.4
            NB + "SF012",  # repeating group * num bits set in SF012
            {
                "SF013": "Do not use (DNU)",
                "optSat": (
                    ("SF013+1", 0),  # if SF013 = 0
                    {
                        **OCB_SAT_FLAGS,
                        "optOrbit": (  # table 6.5 Orbit Block
                            ("SF014O+1", 1),  # if SF014O = 1
                            {
                                "SF019": "GLONASS IODE",
                                **OCB_ORBIT_BLOCK,
                            },
                        ),
                        **OCB_CLOCK_BLOCK,
                        "optBias": (
                            ("SF014B+1", 1),  # if SF014B = 1
                            {
                                PBBMLEN: "Phase bias mask length",
                                "SF026": "GLONASS phase bias mask",
                                "groupSF026-BITS": (
                                    NB
                                    + "SF026+1",  # repeating group * num bits set in SF026
                                    {
                                        **PHAS_BIAS_BLOCK,
                                    },
                                ),
                                CBBMLEN: "Code bias mask length",
                                "SF028": "GLONASScode bias mask",
                                "groupSF028-BITS": (
                                    NB
                                    + "SF028+1",  # repeating group * num bits set in SF028
                                    {
                                        **CODE_BIAS_BLOCK,
                                    },
                                ),
                            },
                        ),
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-OCB-GAL": {
        **OCB_HDR,
        "SF096": "GALILEO Ephemeris type",
        STBMLEN: "GPS Satellite mask length",
        "SF093": "GALILEO Satellite mask",
        "groupSat": (  # Satellite Block table 6.4
            NB + "SF093",  # repeating group * num bits set in SF093
            {
                "SF013": "Do not use (DNU)",
                "optSat": (
                    ("SF013+1", 0),  # if SF013 = 0
                    {
                        **OCB_SAT_FLAGS,
                        "optOrbit": (  # table 6.5 Orbit Block
                            ("SF014O+1", 1),  # if SF014O = 1
                            {
                                "SF099": "GALILEO IODE",
                                **OCB_ORBIT_BLOCK,
                            },
                        ),
                        **OCB_CLOCK_BLOCK,
                        "optBias": (
                            ("SF014B+1", 1),  # if SF014B = 1
                            {
                                PBBMLEN: "Phase bias mask length",
                                "SF102": "GALILEO phase bias mask",
                                "groupSF102-BITS": (
                                    NB
                                    + "SF102+1",  # repeating group * num bits set in SF0102
                                    {
                                        **PHAS_BIAS_BLOCK,
                                    },
                                ),
                                CBBMLEN: "Code bias mask length",
                                "SF105": "GALILEO code bias mask",
                                "groupSF105-BITS": (
                                    NB
                                    + "SF105+1",  # repeating group * num bits set in SF0105
                                    {
                                        **CODE_BIAS_BLOCK,
                                    },
                                ),
                            },
                        ),
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-OCB-BEI": {
        **OCB_HDR,
        "SF097": "BEIDOU Ephemeris type",
        STBMLEN: "GPS Satellite mask length",
        "SF094": "BEIDOU Satellite mask",
        "groupSat": (  # Satellite Block table 6.4
            NB + "SF094",  # repeating group * num bits set in SF094
            {
                "SF013": "Do not use (DNU)",
                "optSat": (
                    ("SF013+1", 0),  # if SF013 = 0
                    {
                        **OCB_SAT_FLAGS,
                        "optOrbit": (  # table 6.5 Orbit Block
                            ("SF014O+1", 1),  # if SF014O = 1
                            {
                                "SF100": "BEIDOU IODE",
                                **OCB_ORBIT_BLOCK,
                            },
                        ),
                        **OCB_CLOCK_BLOCK,
                        "optBias": (
                            ("SF014B+1", 1),  # if SF014B = 1
                            {
                                PBBMLEN: "Phase bias mask length",
                                "SF103": "BEIDOU phase bias mask",
                                "groupSF103-BITS": (
                                    NB
                                    + "SF103+1",  # repeating group * num bits set in SF0103
                                    {
                                        **PHAS_BIAS_BLOCK,
                                    },
                                ),
                                CBBMLEN: "Code bias mask length",
                                "SF106": "BEIDOU code bias mask",
                                "groupSF106-BITS": (
                                    NB
                                    + "SF106+1",  # repeating group * num bits set in SF0106
                                    {
                                        **CODE_BIAS_BLOCK,
                                    },
                                ),
                            },
                        ),
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-OCB-QZS": {
        **OCB_HDR,
        "SF098": "QZSS Ephemeris type",
        STBMLEN: "GPS Satellite mask length",
        "SF095": "QZSS Satellite mask",
        "groupSat": (  # Satellite Block table 6.4
            NB + "SF095",  # repeating group * num bits set in SF095
            {
                "SF013": "Do not use (DNU)",
                "optSat": (
                    ("SF013+1", 0),  # if SF013 = 0
                    {
                        **OCB_SAT_FLAGS,
                        "optOrbit": (  # table 6.5 Orbit Block
                            ("SF014O+1", 1),  # if SF014O = 1
                            {
                                "SF101": "QZSS IODE",
                                **OCB_ORBIT_BLOCK,
                            },
                        ),
                        **OCB_CLOCK_BLOCK,
                        "optBias": (
                            ("SF014B+1", 1),  # if SF014B = 1
                            {
                                PBBMLEN: "Phase bias mask length",
                                "SF104": "QZSS phase bias mask",
                                "groupSF104-BITS": (
                                    NB
                                    + "SF104+1",  # repeating group * num bits set in SF0104
                                    {
                                        **PHAS_BIAS_BLOCK,
                                    },
                                ),
                                CBBMLEN: "Code bias mask length",
                                "SF107": "QZSS code bias mask",
                                "groupSF107-BITS": (
                                    NB
                                    + "SF107+1",  # repeating group * num bits set in SF0107
                                    {
                                        **CODE_BIAS_BLOCK,
                                    },
                                ),
                            },
                        ),
                    },
                ),
            },
        ),
    },
    # ********************************************************************
    # HPAC
    # ********************************************************************
    "SPARTN-1X-HPAC-GPS": {
        **HPAC_HDR,
        "groupAtm": (  # Atmosphere Data Block repeating group * (SF030 + 1)
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "optSF040I-12": (  # table 6.19 Ionosphere Data Block
                    ("SF040I+1", [1, 2]),  # if SF040I in 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        STBMLEN: "GPS Satellite mask length",
                        "SF011": "GPS Satellite mask",
                        "groupSF011": (  # repeating group * num bits set in SF011
                            NB + "SF011+1",
                            {
                                **ION_SAT_BLOCK,
                            },
                        ),
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-HPAC-GLO": {
        **HPAC_HDR,
        "groupAtm": (  # Atmosphere Data Block repeating group * (SF030 + 1)
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "optSF040I-12": (  # table 6.19 Ionosphere Data Block
                    ("SF040I+1", [1, 2]),  # if SF040I in 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        STBMLEN: "GPS Satellite mask length",
                        "SF012": "GLONASS Satellite mask",
                        "groupSF012": (  # repeating group * num bits set in SF012
                            NB + "SF012+1",
                            {
                                **ION_SAT_BLOCK,
                            },
                        ),
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-HPAC-GAL": {
        **HPAC_HDR,
        "groupAtm": (  # Atmosphere Data Block repeating group * (SF030 + 1)
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "optSF040I-12": (  # table 6.19 Ionosphere Data Block
                    ("SF040I+1", [1, 2]),  # if SF040I in 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        STBMLEN: "GPS Satellite mask length",
                        "SF093": "GALILEO Satellite mask",
                        "groupSF093": (  # repeating group * num bits set in SF093
                            NB + "SF093+1",
                            {
                                **ION_SAT_BLOCK,
                            },
                        ),
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-HPAC-BEI": {
        **HPAC_HDR,
        "groupAtm": (  # Atmosphere Data Block repeating group * (SF030 + 1)
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "optSF040I-12": (  # table 6.19 Ionosphere Data Block
                    ("SF040I+1", [1, 2]),  # if SF040I in 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        STBMLEN: "GPS Satellite mask length",
                        "SF094": "BEIDOU Satellite mask",
                        "groupSF094": (  # repeating group * num bits set in SF094
                            NB + "SF094+1",
                            {
                                **ION_SAT_BLOCK,
                            },
                        ),
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-HPAC-QZS": {
        **HPAC_HDR,
        "groupAtm": (  # Atmosphere Data Block repeating group * (SF030 + 1)
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "optSF040I-12": (  # table 6.19 Ionosphere Data Block
                    ("SF040I+1", [1, 2]),  # if SF040I in 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        STBMLEN: "GPS Satellite mask length",
                        "SF095": "QZSS Satellite mask",
                        "groupSF095": (  # repeating group * num bits set in SF095
                            NB + "SF095+1",
                            {
                                **ION_SAT_BLOCK,
                            },
                        ),
                    },
                ),
            },
        ),
    },
    # ********************************************************************
    # GAD
    # ********************************************************************
    "SPARTN-1X-GAD": {
        "SF005": "Solution issue of updated (SIOU)",
        "SF068": "Area issue of update (AIOU)",
        "SF069": "Reserved",
        "SF030": "Area Count",  # NB:  N - 1
        "group": (  # repeating group * (SF030 + 1)
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
    # ********************************************************************
    # BPAC TODO not yet tested - no available test data source
    # ********************************************************************
    "SPARTN-1X-BPAC": {
        "SF005": "Solution issue of updated (SIOU)",
        "SF069": "Reserved",
        "SF070": "Ionosphere shell height",
        "SF071": "BPAC area count",  # NB: N - 1
        "groupBPAC": (  # repeating group * (SF071 + 1)
            "SF071",
            {
                "SF072": "BPAC area ID",
                "SF073": "BPAC area reference latitude",
                "SF074": "BPAC area reference longitude",
                "SF075": "BPAC area latitude grid node count",  # NB: N - 1
                "SF076": "BPAC area longitude grid node count",  # NB: N - 1
                "SF077": "BPAC area latitude grid node spacing",
                "SF078": "BPAC area longitude grid node spacing",
                "SF080": "Average area VTEC",
                "SF079": "Grid node present mask",  # len = (SF075 + 1) * (SF076 + 1)
                "groupVTEC": (
                    NB + "SF079+1",  # repeating group
                    {
                        "SF055": "VTEC quality",
                        "SF081": "VTEC size indicator",
                        "optSF081-0": (
                            ("SF081+2", 0),  # if SF081 = 0
                            {
                                "SF082": "Small VTEC residual",
                            },
                        ),
                        "optSF081-1": (
                            ("SF081+2", 1),  # if SF081 = 1
                            {
                                "SF083": "Large VTEC residual",
                            },
                        ),
                    },
                ),
            },
        ),
    },
    # ********************************************************************
    # EAS-DYN TODO not yet tested - no available test data source
    # ********************************************************************
    "SPARTN-1X-EAS-DYN": {
        "SF084": "Customer key ID",  # plain text
        "SF085": "Dynamic key encryption type",  # plain text
        "SF086": "Week of applicability",
        "SF085a": "Payload encryption type",
        "SF087": "Dynamic key length",
        "SF088": "Dynamic key",  # variable length
    },
    # ********************************************************************
    # EAS-GRP deprecated
    # ********************************************************************
    "SPARTN-1X-EAS-GRP": {},  # no current plans to implement
}
