"""
SPARTN Protocol core globals and constants

Created on 10 Feb 2023

Information from pubic domain SPARTN Protocol v2.0.3 (November 2025) © 2025 u-blox AG.
https://www.spartnformat.org/download/

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

:author: semuadmin (Steve Smith)
:copyright: semuadmin © 2023
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
    "SF008-1_alt": (
        ("SF008", 1),  # if SF008 = 1
        {
            "SF021": "Satellite yaw",
        },
    ),
}

OCB_CLOCK_BLOCK = {  # table 6.6 Clock Block
    "Clock_alt": (
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
    "SF040T-12_alt": (
        ("SF040T+1", [1, 2]),  # if SF040T in 1,2
        {
            "SF041": "Troposhere equation type",
            "SF042": "Troposphere quality",
            "SF043": "Area average vertical hydrostatic delay",
            "SF044": "Troposphere polynomial coefficient size indicator",
            "SF044-0_alt": (
                ("SF044+1", 0),  # if SF044 = 0 table 6.17
                {
                    "SF045": "Troposphere coefficient T00",
                    "SF041-12_alt": (
                        ("SF041+1", [1, 2]),  # if SF041 in 1,2
                        {
                            "SF046a": "Troposphere coefficient T01",
                            "SF046b": "Troposphere coefficient T10",
                        },
                    ),
                    "SF041-2_alt": (
                        ("SF041+1", 2),  # if SF041 = 2
                        {
                            "SF047": "Troposphere coefficient T11",
                        },
                    ),
                },
            ),
            "SF044-1_alt": (
                ("SF044+1", 1),  # if SF044 = 1 table 6.18
                {
                    "SF048": "Troposphere coefficient T00",
                    "SF041-12_alt": (
                        ("SF041+1", [1, 2]),  # if SF041 in 1,2
                        {
                            "SF049a": "Troposphere coefficient T01",
                            "SF049b": "Troposphere coefficient T10",
                        },
                    ),
                    "SF041-2_alt": (
                        ("SF041+1", 2),  # if SF041 = 2
                        {
                            "SF050": "Troposphere coefficient T11",
                        },
                    ),
                },
            ),
        },
    ),
    "SF040T-2_alt": (  # if SF040T = 2
        ("SF040T+1", 2),  # if SF040T = 2
        {
            "SF051": "Troposphere residual field size",
            "SF051-0_alt": (
                ("SF051+1", 0),  # if SF051 = 0
                {
                    "SF052_grp": (
                        "SF039+1",
                        {"SF052": "Troposphere grid residuals"},
                    )
                },
            ),
            "SF051-1_alt": (  # if SF051 = 1
                ("SF051+1", 1),  # if SF051 = 1
                {
                    "SF053_grp": (
                        "SF039+1",
                        {"SF053": "Troposphere grid residuals"},
                    )
                },
            ),
        },
    ),
}

ION_SAT_BLOCK = {  # table 6.20 Ionosphere Satellite Block
    "SF040I-12_alt": (
        ("SF040I+1", [1, 2]),  # if SF040I in 1,2
        {
            PRN: "Satellite PRN",
            "SF055": "Ionosphere quality",
            "SF056": "Ionosphere polynomial coefficient size indicator",
            "SF056-0_alt": (
                ("SF056+2", 0),  # if SF056 = 0 table 6.21
                {
                    "SF057": "Ionosphere coefficient C00",
                    "SF054-12_alt": (
                        ("SF054+1", [1, 2]),  # if SF054 in 1,2
                        {
                            "SF058a": "Ionosphere coefficient C01",
                            "SF058b": "Ionosphere coefficient C10",
                        },
                    ),
                    "SF054-2_alt": (
                        ("SF054+1", 2),  # if SF054 = 2
                        {
                            "SF059": "Ionosphere coefficient C11",
                        },
                    ),
                },
            ),
            "SF056-1_alt": (
                ("SF056+2", 1),  # if SF056 = 1 table 6.22
                {
                    "SF060": "Ionosphere coefficient C00",
                    "SF054-12_alt": (
                        ("SF054+1", [1, 2]),  # if SF054 in 1,2
                        {
                            "SF061a": "Ionosphere coefficient C01",
                            "SF061b": "Ionosphere coefficient C10",
                        },
                    ),
                    "SF054-2_alt": (
                        ("SF054+1", 2),  # if SF054 = 2
                        {
                            "SF062": "Ionosphere coefficient C11",
                        },
                    ),
                },
            ),
        },
    ),
    "SF040I-2_alt": (
        ("SF040I+1", 2),  # if SF040I = 2
        {
            "SF063": "Ionosphere residual field size",
            "SF063-0_alt": (
                ("SF063+2", 0),  # if SF063 = 0
                {"SF064_grp": ("SF039+1", {"SF064": "Ionosphere grid residuals"})},
            ),
            "SF063-1_alt": (
                ("SF063+2", 1),  # if SF063 = 1
                {"SF065_grp": ("SF039+1", {"SF065": "Ionosphere grid residuals"})},
            ),
            "SF063-2_alt": (
                ("SF063+2", 2),  # if SF063 = 2
                {"SF066_grp": ("SF039+1", {"SF066": "Ionosphere grid residuals"})},
            ),
            "SF063-3_alt": (
                ("SF063+2", 3),  # if SF063 = 3
                {"SF067_grp": ("SF039+1", {"SF067": "Ionosphere grid residuals"})},
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
        "Sat_grp": (  # Satellite Block table 6.4
            NB + "SF011",  # repeating group * num bits set in SF011
            {
                "SF013": "Do not use (DNU)",
                "Sat_alt": (
                    ("SF013+1", 0),  # if SF013 = 0
                    {
                        **OCB_SAT_FLAGS,
                        "Orbit_alt": (  # # table 6.5 Orbit Block
                            ("SF014O+1", 1),  # if SF014O = 1
                            {
                                "SF018": "GPS IODE",
                                **OCB_ORBIT_BLOCK,
                            },
                        ),
                        **OCB_CLOCK_BLOCK,
                        "Bias_alt": (
                            ("SF014B+1", 1),  # if SF014B = 1
                            {
                                PBBMLEN: "Phase bias mask length",
                                "SF025": "GPS phase bias mask",
                                "SF025-BITS_grp": (
                                    NB
                                    + "SF025+1",  # repeating group * num bits set in SF025
                                    {
                                        **PHAS_BIAS_BLOCK,
                                    },
                                ),
                                CBBMLEN: "Code bias mask length",
                                "SF027": "GPS code bias mask",
                                "SF027-BITS_grp": (
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
        "Sat_grp": (  # Satellite Block table 6.4
            NB + "SF012",  # repeating group * num bits set in SF012
            {
                "SF013": "Do not use (DNU)",
                "Sat_alt": (
                    ("SF013+1", 0),  # if SF013 = 0
                    {
                        **OCB_SAT_FLAGS,
                        "Orbit_alt": (  # table 6.5 Orbit Block
                            ("SF014O+1", 1),  # if SF014O = 1
                            {
                                "SF019": "GLONASS IODE",
                                **OCB_ORBIT_BLOCK,
                            },
                        ),
                        **OCB_CLOCK_BLOCK,
                        "Bias_alt": (
                            ("SF014B+1", 1),  # if SF014B = 1
                            {
                                PBBMLEN: "Phase bias mask length",
                                "SF026": "GLONASS phase bias mask",
                                "SF026-BITS_grp": (
                                    NB
                                    + "SF026+1",  # repeating group * num bits set in SF026
                                    {
                                        **PHAS_BIAS_BLOCK,
                                    },
                                ),
                                CBBMLEN: "Code bias mask length",
                                "SF028": "GLONASScode bias mask",
                                "SF028-BITS_grp": (
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
        "Sat_grp": (  # Satellite Block table 6.4
            NB + "SF093",  # repeating group * num bits set in SF093
            {
                "SF013": "Do not use (DNU)",
                "Sat_alt": (
                    ("SF013+1", 0),  # if SF013 = 0
                    {
                        **OCB_SAT_FLAGS,
                        "Orbit_alt": (  # table 6.5 Orbit Block
                            ("SF014O+1", 1),  # if SF014O = 1
                            {
                                "SF099": "GALILEO IODE",
                                **OCB_ORBIT_BLOCK,
                            },
                        ),
                        **OCB_CLOCK_BLOCK,
                        "Bias_alt": (
                            ("SF014B+1", 1),  # if SF014B = 1
                            {
                                PBBMLEN: "Phase bias mask length",
                                "SF102": "GALILEO phase bias mask",
                                "SF102-BITS_grp": (
                                    NB
                                    + "SF102+1",  # repeating group * num bits set in SF0102
                                    {
                                        **PHAS_BIAS_BLOCK,
                                    },
                                ),
                                CBBMLEN: "Code bias mask length",
                                "SF105": "GALILEO code bias mask",
                                "SF105-BITS_grp": (
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
        "Sat_grp": (  # Satellite Block table 6.4
            NB + "SF094",  # repeating group * num bits set in SF094
            {
                "SF013": "Do not use (DNU)",
                "Sat_alt": (
                    ("SF013+1", 0),  # if SF013 = 0
                    {
                        **OCB_SAT_FLAGS,
                        "Orbit_alt": (  # table 6.5 Orbit Block
                            ("SF014O+1", 1),  # if SF014O = 1
                            {
                                "SF100": "BEIDOU IODE",
                                **OCB_ORBIT_BLOCK,
                            },
                        ),
                        **OCB_CLOCK_BLOCK,
                        "Bias_alt": (
                            ("SF014B+1", 1),  # if SF014B = 1
                            {
                                PBBMLEN: "Phase bias mask length",
                                "SF103": "BEIDOU phase bias mask",
                                "SF103-BITS_grp": (
                                    NB
                                    + "SF103+1",  # repeating group * num bits set in SF0103
                                    {
                                        **PHAS_BIAS_BLOCK,
                                    },
                                ),
                                CBBMLEN: "Code bias mask length",
                                "SF106": "BEIDOU code bias mask",
                                "SF106-BITS_grp": (
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
        "Sat_grp": (  # Satellite Block table 6.4
            NB + "SF095",  # repeating group * num bits set in SF095
            {
                "SF013": "Do not use (DNU)",
                "Sat_alt": (
                    ("SF013+1", 0),  # if SF013 = 0
                    {
                        **OCB_SAT_FLAGS,
                        "Orbit_alt": (  # table 6.5 Orbit Block
                            ("SF014O+1", 1),  # if SF014O = 1
                            {
                                "SF101": "QZSS IODE",
                                **OCB_ORBIT_BLOCK,
                            },
                        ),
                        **OCB_CLOCK_BLOCK,
                        "Bias_alt": (
                            ("SF014B+1", 1),  # if SF014B = 1
                            {
                                PBBMLEN: "Phase bias mask length",
                                "SF104": "QZSS phase bias mask",
                                "SF104-BITS_grp": (
                                    NB
                                    + "SF104+1",  # repeating group * num bits set in SF0104
                                    {
                                        **PHAS_BIAS_BLOCK,
                                    },
                                ),
                                CBBMLEN: "Code bias mask length",
                                "SF107": "QZSS code bias mask",
                                "SF107-BITS_grp": (
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
        "Atm_grp": (  # Atmosphere Data Block repeating group * (SF030 + 1)
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "SF040I-12_alt": (  # table 6.19 Ionosphere Data Block
                    ("SF040I+1", [1, 2]),  # if SF040I in 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        STBMLEN: "GPS Satellite mask length",
                        "SF011": "GPS Satellite mask",
                        "SF011_grp": (  # repeating group * num bits set in SF011
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
        "Atm_grp": (  # Atmosphere Data Block repeating group * (SF030 + 1)
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "SF040I-12_alt": (  # table 6.19 Ionosphere Data Block
                    ("SF040I+1", [1, 2]),  # if SF040I in 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        STBMLEN: "GPS Satellite mask length",
                        "SF012": "GLONASS Satellite mask",
                        "SF012_grp": (  # repeating group * num bits set in SF012
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
        "Atm_grp": (  # Atmosphere Data Block repeating group * (SF030 + 1)
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "SF040I-12_alt": (  # table 6.19 Ionosphere Data Block
                    ("SF040I+1", [1, 2]),  # if SF040I in 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        STBMLEN: "GPS Satellite mask length",
                        "SF093": "GALILEO Satellite mask",
                        "SF093_grp": (  # repeating group * num bits set in SF093
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
        "Atm_grp": (  # Atmosphere Data Block repeating group * (SF030 + 1)
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "SF040I-12_alt": (  # table 6.19 Ionosphere Data Block
                    ("SF040I+1", [1, 2]),  # if SF040I in 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        STBMLEN: "GPS Satellite mask length",
                        "SF094": "BEIDOU Satellite mask",
                        "SF094_grp": (  # repeating group * num bits set in SF094
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
        "Atm_grp": (  # Atmosphere Data Block repeating group * (SF030 + 1)
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "SF040I-12_alt": (  # table 6.19 Ionosphere Data Block
                    ("SF040I+1", [1, 2]),  # if SF040I in 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        STBMLEN: "GPS Satellite mask length",
                        "SF095": "QZSS Satellite mask",
                        "SF095_grp": (  # repeating group * num bits set in SF095
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
        "area_grp": (  # repeating group * (SF030 + 1)
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
        "BPAC_grp": (  # repeating group * (SF071 + 1)
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
                "VTEC_grp": (
                    NB + "SF079+1",  # repeating group
                    {
                        "SF055": "VTEC quality",
                        "SF081": "VTEC size indicator",
                        "SF081-0_alt": (
                            ("SF081+2", 0),  # if SF081 = 0
                            {
                                "SF082": "Small VTEC residual",
                            },
                        ),
                        "SF081-1_alt": (
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
