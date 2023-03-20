"""
SPARTN Protocol core globals and constants

Created on 10 Feb 2023

Information Sourced from https://www.spartnformat.org/download/
(available in the public domain) © 2021 u-blox AG. All rights reserved.

:author: semuadmin
"""
# pylint: disable=too-many-lines, line-too-long

OCB_HDR = {  # OCB Header
    "SF005": "Solution issue of update (SIOU)",
    "SF010": "End of set",
    "SF069": "Reserved",
    "SF008": "Yaw present flag",
}

HPAC_HDR = {  # HPAC Header
    "SF005": "Solution issue of update (SIOU)",
    "SF068": "Area issue of update (AIOU)",
    "SF069": "Reserved",
    "SF030": "Area count",
}

CLK_BLOCK = {  # table 6.6 Clock Block
    "groupClock": (
        "NCLOK",
        {
            "SF027": "IODE continuity",
            "SF020": "Clock correction",
            "SF024": "User range error",
        },
    ),
}

PHAS_BIAS_BLOCK = {  # table 6.12 Phase Bias Block
    "groupPhaseBias": (
        "NPBIAS",
        {
            "SF023": "Fix flag",
            "SF015": "Continuity indicator",
            "SF020": "Phase bias correction",
        },
    ),
}

AREA_DATA_BLOCK = {  # table 6.15 Area Data Block
    "SF031": "Area ID",
    "SF039": "Number of grid points present",
    "SF040T": "Tropo blocks indicator",
    "SF040i": "Iono blocks indicator",
}

TROP_DATA_BLOCK = {  # table 6.16 Troposphere Data Block
    "optSF040T-12": (  # if SF040T = 1,2
        "NSF040t-12",
        {
            "SF041": "Troposhere equation type",
            "SF042": "Troposphere quality",
            "SF043": "Area average vertical hydrostatic delay",
            "SF044": "Troposphere polynomial coefficient size indicator",
            "optSF044-0": (  # if SF044 = 0
                "NSF044-0",  # table 6.17
                {
                    "SF045": "Troposphere coefficient T00",
                    "optSF041-12": (  # if SF041 = 1,2
                        "NSF014-12",
                        {
                            "SF046a": "Troposphere coefficient T01",
                            "SF046b": "Troposphere coefficient T10",
                        },
                    ),
                    "optSF041-2": (  # if SF041 = 2
                        "NSF014-2",
                        {
                            "SF047": "Troposphere coefficient T11",
                        },
                    ),
                },
            ),
            "optSF044-1": (  # if SF044 = 1
                "NSF044-1",  # table 6.18
                {
                    "SF048": "Troposphere coefficient T00",
                    "optSF041-12": (  # if SF041 = 1,2
                        "NSF014-12",
                        {
                            "SF049a": "Troposphere coefficient T01",
                            "SF049b": "Troposphere coefficient T10",
                        },
                    ),
                    "optSF041-2": (  # if SF041 = 2
                        "NSF014-2",
                        {
                            "SF050": "Troposphere coefficient T11",
                        },
                    ),
                },
            ),
        },
    ),
    "optSF040t-2": (  # if SF040T = 1,2
        "NSF040t-2",
        {
            "SF051": "Troposphere residual field size",
            "optSF051-0": (  # if SF051 = 0
                "NSF051-0",
                {"SF052": "Troposphere grid residuals"},
            ),
            "optSF051-1": (  # if SF051 = 1
                "NSF051-1",
                {"SF053": "Troposphere grid residuals"},
            ),
        },
    ),
}

ION_SAT_BLOCK = {  # table 6.20 Ionosphere Satellite Block
    "optSF040I-12": (  # if SF041I = 1,2
        "NSF040I-12",
        {
            "SF055": "Ionosphere quality",
            "SF056": "Ionosphere polynomial coefficient size indicator",
            "optSF064-0": (  # if SF056 = 0
                "NSF056-0",  # table 6.21
                {
                    "SF057": "Ionosphere coefficient C00",
                    "optSF054-12": (  # if SF054 = 1,2
                        "NSF054-12",
                        {
                            "SF058a": "Ionosphere coefficient C01",
                            "SF058b": "Ionosphere coefficient C10",
                        },
                    ),
                    "optSF054-2": (  # if SF054 = 2
                        "NSF054-2",
                        {
                            "SF059": "Ionosphere coefficient C11",
                        },
                    ),
                },
            ),
            "optSF056-1": (  # if SF056 = 1
                "NSF056-0",  # table 6.22
                {
                    "SF060": "Ionosphere coefficient C00",
                    "optSF054-12": (  # if SF054 = 1,2
                        "NSF054-12",
                        {
                            "SF061a": "Ionosphere coefficient C01",
                            "SF061b": "Ionosphere coefficient C10",
                        },
                    ),
                    "optSF054-2": (  # if SF054 = 2
                        "NSF054-2",
                        {
                            "SF062": "Ionosphere coefficient C11",
                        },
                    ),
                },
            ),
        },
    ),
    "optSF040I-2": (  # if SF041I = 2
        "NSF040I-2",
        {
            "SF063": "Ionosphere residual field size",
            "optSF063-0": (  # if SF063 = 0
                "NSF063-0",
                {"SF064": "Ionosphere grid residuals"},
            ),
            "optSF063-1": (  # if SF063 = 1
                "NSF063-1",
                {"SF065": "Ionosphere grid residuals"},
            ),
            "optSF063-2": (  # if SF063 = 2
                "NSF063-2",
                {"SF066": "Ionosphere grid residuals"},
            ),
            "optSF063-3": (  # if SF063 = 3
                "NSF063-3",
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
        "SF011": "GPS Satellite mask",
        "groupSat": (  # Satellite Block
            "NSAT",
            {
                "SF013": "Do not use (DNU)",
                "SF014": "OCB present flags",
                "SF015": "Continuity indicator",
                "groupOrb": (  # Orbit Block
                    "NORB",
                    {
                        "SF018": "GPS IODE",
                        "SF020r": "Orbit radial correction",
                        "SF020a": "Orbit along-track correction",
                        "SF020c": "Orbit cross-track correction",
                        "SF021": "Satellite yaw",
                    },
                ),
                **CLK_BLOCK,
                "groupBias": (  # Bias Block
                    "NBIAS",
                    {
                        "SF025": "GPS phase bias mask",
                        **PHAS_BIAS_BLOCK,
                        "SF027": "GPS code bias mask",
                        "SF029": "Code bias correction",
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-OCB-GLO": {
        **OCB_HDR,
        "SF017": "GLO Ephemeris type",
        "SF012": "GLO Satellite mask",
        "groupSat": (  # Satellite Block
            "NSAT",
            {
                "SF013": "Do not use (DNU)",
                "SF014": "OCB present flags",
                "SF015": "Continuity indicator",
                "groupOrb": (  # Orbit Block
                    "NORB",
                    {
                        "SF019": "GLONASS IODE",
                        "SF020r": "Orbit radial correction",
                        "SF020a": "Orbit along-track correction",
                        "SF020c": "Orbit cross-track correction",
                        "SF021": "Satellite yaw",
                    },
                ),
                **CLK_BLOCK,
                "groupBias": (  # Bias Block
                    "NBIAS",
                    {
                        "SF026": "GLONASS phase bias mask",
                        **PHAS_BIAS_BLOCK,
                        "SF028": "GLONASS code bias mask",
                        "SF029": "Code bias correction",
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-OCB-GAL": {
        **OCB_HDR,
        "SF096": "GALILEO Ephemeris type",
        "SF093": "GALILEO Satellite mask",
        "groupSat": (  # Satellite Block
            "NSAT",
            {
                "SF013": "Do not use (DNU)",
                "SF014": "OCB present flags",
                "SF015": "Continuity indicator",
                "groupOrb": (  # Orbit Block
                    "NORB",
                    {
                        "SF099": "GALILEO IODE",
                        "SF020r": "Orbit radial correction",
                        "SF020a": "Orbit along-track correction",
                        "SF020c": "Orbit cross-track correction",
                        "SF021": "Satellite yaw",
                    },
                ),
                **CLK_BLOCK,
                "groupBias": (  # Bias Block
                    "NBIAS",
                    {
                        "SF0102": "GALILEO phase bias mask",
                        **PHAS_BIAS_BLOCK,
                        "SF105": "GALILEO code bias mask",
                        "SF029": "Code bias correction",
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-OCB-BEI": {
        **OCB_HDR,
        "SF097": "BEIDOU Ephemeris type",
        "SF094": "BEIDOU Satellite mask",
        "groupSat": (  # Satellite Block
            "NSAT",
            {
                "SF013": "Do not use (DNU)",
                "SF014": "OCB present flags",
                "SF015": "Continuity indicator",
                "groupOrb": (  # Orbit Block
                    "NORB",
                    {
                        "SF0100": "BEIDOU IODE",
                        "SF020r": "Orbit radial correction",
                        "SF020a": "Orbit along-track correction",
                        "SF020c": "Orbit cross-track correction",
                        "SF021": "Satellite yaw",
                    },
                ),
                **CLK_BLOCK,
                "groupBias": (  # Bias Block
                    "NBIAS",
                    {
                        "SF0103": "BEIDOU phase bias mask",
                        **PHAS_BIAS_BLOCK,
                        "SF106": "BEIDOU code bias mask",
                        "SF029": "Code bias correction",
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-OCB-QZS": {
        **OCB_HDR,
        "SF098": "QZSS Ephemeris type",
        "SF095": "QZSS Satellite mask",
        "groupSat": (  # Satellite Block
            "NSAT",
            {
                "SF013": "Do not use (DNU)",
                "SF014": "OCB present flags",
                "SF015": "Continuity indicator",
                "groupOrb": (  # Orbit Block
                    "NORB",
                    {
                        "SF0101": "QZSS IODE",
                        "SF020r": "Orbit radial correction",
                        "SF020a": "Orbit along-track correction",
                        "SF020c": "Orbit cross-track correction",
                        "SF021": "Satellite yaw",
                    },
                ),
                **CLK_BLOCK,
                "groupBias": (  # Bias Block
                    "NBIAS",
                    {
                        "SF0104": "QZSS phase bias mask",
                        **PHAS_BIAS_BLOCK,
                        "SF107": "QZSS code bias mask",
                        "SF029": "Code bias correction",
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
        "groupAtm": (  # Atmosphere Data Block repeating group * SF030
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "optSF040I-12": (  # table 6.19 Ionosphere Data Block
                    "NSF040i-12",  # if SF040I = 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        "SF011": "GPS Satellite mask",
                        "groupSF011": (  # repeating group * num bits set in SF011
                            "NSF011-BITS",
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
        "groupAtm": (  # Atmosphere Data Block repeating group * SF030
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "optSF040I-12": (  # table 6.19 Ionosphere Data Block
                    "NSF040i-12",  # if SF040I = 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        "SF012": "GLONASS Satellite mask",
                        "groupSF012": (  # repeating group * num bits set in SF012
                            "NSF012-BITS",
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
        "groupAtm": (  # Atmosphere Data Block repeating group * SF030
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "optSF040I-12": (  # table 6.19 Ionosphere Data Block
                    "NSF040i-12",  # if SF040I = 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        "SF093": "GALILEO Satellite mask",
                        "groupSF093": (  # repeating group * num bits set in SF093
                            "NSF093-BITS",
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
        "groupAtm": (  # Atmosphere Data Block repeating group * SF030
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "optSF040I-12": (  # table 6.19 Ionosphere Data Block
                    "NSF040i-12",  # if SF040I = 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        "SF094": "BEIDOU Satellite mask",
                        "groupSF094": (  # repeating group * num bits set in SF094
                            "NSF094-BITS",
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
        "groupAtm": (  # Atmosphere Data Block repeating group * SF030
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "optSF040I-12": (  # table 6.19 Ionosphere Data Block
                    "NSF040i-12",  # if SF040I = 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        "SF095": "QZSS Satellite mask",
                        "groupSF095": (  # repeating group * num bits set in SF095
                            "NSF095-BITS",
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
    # ********************************************************************
    # BPAC
    # ********************************************************************
    "SPARTN-1X-BPAC": {},  # TODO
    # ********************************************************************
    # EAS-DYN
    # ********************************************************************
    "SPARTN-1X-EAS-DYN": {},  # TODO
    # ********************************************************************
    # EAS-GRP deprecated
    # ********************************************************************
    "SPARTN-1X-EAS-GRP": {},  # TODO
}
