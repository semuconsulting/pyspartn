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
    "groupArea": (
        "NAREA",
        {
            "SF031": "Area ID",
            "SF039": "Number of grid points present",
            "SF040t": "Tropo blocks indicator",
            "SF040i": "Iono blocks indicator",
        },
    ),
}

TROP_DATA_BLOCK = {  # table 6.16 Troposphere Data Block
    "groupTrop": (
        "NTROP",
        {
            "SF041": "Troposhere equation type",
            "SF042": "Troposphere quality",
            "SF043": "Area average vertical hydrostatic delay",
            "SF044": "Troposphere polynomial coefficient size indicator",
            "groupTropS": (  # if SF044 = 0
                "NTROPS",
                {
                    "SF045": "Troposphere coefficient T00",
                    "SF046a": "Troposphere coefficient T01",
                    "SF046b": "Troposphere coefficient T10",
                    "SF047": "Troposphere coefficient T11",
                },
            ),
            "groupTropL": (  # if SF044 = 1
                "NTROPL",
                {
                    "SF048": "Troposphere coefficient T00",
                    "SF049a": "Troposphere coefficient T01",
                    "SF049b": "Troposphere coefficient T10",
                    "SF050": "Troposphere coefficient T11",
                },
            ),
            "SF051": "Troposphere residual field size",
            "groupTropION_GRID_BLOCK0": (  # if SF051 = 0
                "NTROPION_GRID_BLOCK0",
                {"SF052": "Troposphere grid residuals"},
            ),
            "groupTropION_GRID_BLOCK1": (  # if SF051 = 1
                "NTROOPION_GRID_BLOCK1",
                {"SF053": "Troposphere grid residuals"},
            ),
        },
    ),
}

ION_SAT_BLOCK = {  # Ionosphere Satellite Block
    "groupIonoSat": (
        "NIONOSAT",
        {
            "SF055": "Ionosphere quality",
            "SF056": "Ionosphere polynomial coefficient size indicator",
            "groupIonoSatS": (  # if SF056 = 0
                "IONOSATS",
                {
                    "SF057": "Ionosphere coefficient C00",
                    "SF058a": "Ionosphere coefficient C01",
                    "SF058b": "Ionosphere coefficient C10",
                    "SF059": "Ionosphere coefficient C11",
                },
            ),
            "groupIonoSatL": (  # if SF056 = 1
                "IONOSATL",
                {
                    "SF060": "Ionosphere coefficient C00",
                    "SF061a": "Ionosphere coefficient C01",
                    "SF061b": "Ionosphere coefficient C10",
                    "SF062": "Ionosphere coefficient C11",
                },
            ),
            "SF063": "Ionosphere residual field size",
            "groupIonoION_GRID_BLOCK0": (  # if SF063 = 0
                "NIONOION_GRID_BLOCK0",
                {"SF064": "Ionosphere grid residuals"},
            ),
            "groupIonoION_GRID_BLOCK1": (  # if SF063 = 1
                "NIONOION_GRID_BLOCK1",
                {"SF065": "Ionosphere grid residuals"},
            ),
            "groupIonoION_GRID_BLOCK2": (  # if SF063 = 2
                "NIONOION_GRID_BLOCK2",
                {"SF066": "Ionosphere grid residuals"},
            ),
            "groupIonoION_GRID_BLOCK3": (  # if SF063 = 3
                "NIONOION_GRID_BLOCK2",
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
        "groupAtm": (  # Atmosphere Data Block
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "groupIono": (  # Ionosphere Data Block
                    "NIONO",
                    {
                        "SF054": "Ionosphere equation type",
                        "SF011": "GPS Satellite mask",
                        **ION_SAT_BLOCK,
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-HPAC-GLO": {
        **HPAC_HDR,
        "groupAtm": (  # Atmosphere Data Block
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "groupIono": (  # Ionosphere Data Block
                    "NIONO",
                    {
                        "SF054": "Ionosphere equation type",
                        "SF012": "GLONASS Satellite mask",
                        **ION_SAT_BLOCK,
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-HPAC-GAL": {
        **HPAC_HDR,
        "groupAtm": (  # Atmosphere Data Block
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "groupIono": (  # Ionosphere Data Block
                    "NIONO",
                    {
                        "SF054": "Ionosphere equation type",
                        "SF093": "GALILEO Satellite mask",
                        **ION_SAT_BLOCK,
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-HPAC-BEI": {
        **HPAC_HDR,
        "groupAtm": (  # Atmosphere Data Block
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "groupIono": (  # Ionosphere Data Block
                    "NIONO",
                    {
                        "SF054": "Ionosphere equation type",
                        "SF094": "BEIDOU Satellite mask",
                        **ION_SAT_BLOCK,
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-HPAC-QZS": {
        **HPAC_HDR,
        "groupAtm": (  # Atmosphere Data Block
            "SF030",
            {
                **AREA_DATA_BLOCK,
                **TROP_DATA_BLOCK,
                "groupIono": (  # Ionosphere Data Block
                    "NIONO",
                    {
                        "SF054": "Ionosphere equation type",
                        "SF095": "QZSS Satellite mask",
                        **ION_SAT_BLOCK,
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
