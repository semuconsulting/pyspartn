"""
SPARTN Protocol core globals and constants

Created on 10 Feb 2023

Information Sourced from https://www.spartnformat.org/download/
(available in the public domain) © 2021 u-blox AG. All rights reserved.

:author: semuadmin
"""
# pylint: disable=too-many-lines, line-too-long

from pyspartn.spartntypes_core import (
    NSAT,
    NPHABIAS,
    NCODBIAS,
    NTROP,
    NTROP2,
    NIONO,
    NIONO2,
    NSATMASK,
    NPHABIASMASK,
    NCODBIASMASK,
    NSF0440,
    NSF0441,
    NSF04112,
    NSF0412,
    NSF0510,
    NSF0511,
    NSF0560,
    NSF0561,
    NSF05412,
    NSF0542,
    NSF0630,
    NSF0631,
    NSF0632,
    NSF0633,
)

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
    "SF030": "Area count",
}

ORBCLK_BLOCK = {  # Orbital Block table 6.5 & Clock Block table 6.6
    "SF020R": "Orbit radial correction",
    "SF020A": "Orbit along-track correction",
    "SF020C": "Orbit cross-track correction",
    "SF021": "Satellite yaw",
    "SF027": "IODE continuity",
    "SF020": "Clock correction",
    "SF024": "User range error",
}

PHAS_BIAS_BLOCK = {  # table 6.12 Phase Bias Block
    "SF023": "Fix flag",
    "SF015": "Continuity indicator",
    "SF020": "Phase bias correction",
}

AREA_DATA_BLOCK = {  # table 6.15 Area Data Block
    "SF031": "Area ID",
    "SF039": "Number of grid points present",
    "SF040T": "Tropo blocks indicator",
    "SF040i": "Iono blocks indicator",
}

TROP_DATA_BLOCK = {  # table 6.16 Troposphere Data Block
    "optSF040T-12": (  # if SF040T = 1,2
        NTROP,
        {
            "SF041": "Troposhere equation type",
            "SF042": "Troposphere quality",
            "SF043": "Area average vertical hydrostatic delay",
            "SF044": "Troposphere polynomial coefficient size indicator",
            "optSF044-0": (  # if SF044 = 0
                NSF0440,  # table 6.17
                {
                    "SF045": "Troposphere coefficient T00",
                    "optSF041-12": (  # if SF041 = 1,2
                        NSF04112,
                        {
                            "SF046a": "Troposphere coefficient T01",
                            "SF046b": "Troposphere coefficient T10",
                        },
                    ),
                    "optSF041-2": (  # if SF041 = 2
                        NSF0412,
                        {
                            "SF047": "Troposphere coefficient T11",
                        },
                    ),
                },
            ),
            "optSF044-1": (  # if SF044 = 1
                NSF0441,  # table 6.18
                {
                    "SF048": "Troposphere coefficient T00",
                    "optSF041-12": (  # if SF041 = 1,2
                        NSF04112,
                        {
                            "SF049a": "Troposphere coefficient T01",
                            "SF049b": "Troposphere coefficient T10",
                        },
                    ),
                    "optSF041-2": (  # if SF041 = 2
                        NSF0412,
                        {
                            "SF050": "Troposphere coefficient T11",
                        },
                    ),
                },
            ),
        },
    ),
    "optSF040T-2": (  # if SF040T = 2
        NTROP2,
        {
            "SF051": "Troposphere residual field size",
            "optSF051-0": (  # if SF051 = 0
                NSF0510,
                {"SF052": "Troposphere grid residuals"},
            ),
            "optSF051-1": (  # if SF051 = 1
                NSF0511,
                {"SF053": "Troposphere grid residuals"},
            ),
        },
    ),
}

ION_SAT_BLOCK = {  # table 6.20 Ionosphere Satellite Block
    "optSF040I-12": (  # if SF041I = 1,2
        NIONO,
        {
            "SF055": "Ionosphere quality",
            "SF056": "Ionosphere polynomial coefficient size indicator",
            "optSF064-0": (  # if SF056 = 0
                NSF0560,  # table 6.21
                {
                    "SF057": "Ionosphere coefficient C00",
                    "optSF054-12": (  # if SF054 = 1,2
                        NSF05412,
                        {
                            "SF058a": "Ionosphere coefficient C01",
                            "SF058b": "Ionosphere coefficient C10",
                        },
                    ),
                    "optSF054-2": (  # if SF054 = 2
                        NSF0542,
                        {
                            "SF059": "Ionosphere coefficient C11",
                        },
                    ),
                },
            ),
            "optSF056-1": (  # if SF056 = 1
                NSF0561,  # table 6.22
                {
                    "SF060": "Ionosphere coefficient C00",
                    "optSF054-12": (  # if SF054 = 1,2
                        NSF05412,
                        {
                            "SF061a": "Ionosphere coefficient C01",
                            "SF061b": "Ionosphere coefficient C10",
                        },
                    ),
                    "optSF054-2": (  # if SF054 = 2
                        NSF0542,
                        {
                            "SF062": "Ionosphere coefficient C11",
                        },
                    ),
                },
            ),
        },
    ),
    "optSF040I-2": (  # if SF041I = 2
        NIONO2,
        {
            "SF063": "Ionosphere residual field size",
            "optSF063-0": (  # if SF063 = 0
                NSF0630,
                {"SF064": "Ionosphere grid residuals"},
            ),
            "optSF063-1": (  # if SF063 = 1
                NSF0631,
                {"SF065": "Ionosphere grid residuals"},
            ),
            "optSF063-2": (  # if SF063 = 2
                NSF0632,
                {"SF066": "Ionosphere grid residuals"},
            ),
            "optSF063-3": (  # if SF063 = 3
                NSF0633,
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
        NSATMASK: "Satellite mask length",
        "SF011": "GPS Satellite mask",
        "groupSat": (  # Satellite Block table 6.4
            NSAT,  # repeating group * num bits set in SF011
            {
                "SF013": "Do not use (DNU)",
                "SF014": "OCB present flags",
                "SF015": "Continuity indicator",
                "SF018": "GPS IODE",
                **ORBCLK_BLOCK,
                NPHABIASMASK: "Phase bias mask length",
                "SF025": "GPS phase bias mask",
                "groupSF025-BITS": (
                    NPHABIAS,  # repeating group * num bits set in SF025
                    {
                        **PHAS_BIAS_BLOCK,
                    },
                ),
                NCODBIASMASK: "Code bias mask length",
                "SF027": "GPS code bias mask",
                "groupSF027-BITS": (
                    NCODBIAS,  # repeating group * num bits set in SF027
                    {
                        "SF029": "Code bias correction",
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-OCB-GLO": {
        **OCB_HDR,
        "SF017": "GLO Ephemeris type",
        NSATMASK: "Satellite mask length",
        "SF012": "GLO Satellite mask",
        "groupSat": (  # Satellite Block table 6.4
            NSAT,  # repeating group * num bits set in SF012
            {
                "SF013": "Do not use (DNU)",
                "SF014": "OCB present flags",
                "SF015": "Continuity indicator",
                "SF019": "GLONASS IODE",
                **ORBCLK_BLOCK,
                NPHABIASMASK: "Phase bias mask length",
                "SF026": "GLONASS phase bias mask",
                "groupSF026-BITS": (
                    NPHABIAS,  # repeating group * num bits set in SF026
                    {
                        **PHAS_BIAS_BLOCK,
                    },
                ),
                NCODBIASMASK: "Code bias mask length",
                "SF028": "GLONASScode bias mask",
                "groupSF028-BITS": (
                    NCODBIAS,  # repeating group * num bits set in SF028
                    {
                        "SF029": "Code bias correction",
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-OCB-GAL": {
        **OCB_HDR,
        "SF096": "GALILEO Ephemeris type",
        NSATMASK: "Satellite mask length",
        "SF093": "GALILEO Satellite mask",
        "groupSat": (  # Satellite Block table 6.4
            NSAT,  # repeating group * num bits set in SF093
            {
                "SF013": "Do not use (DNU)",
                "SF014": "OCB present flags",
                "SF015": "Continuity indicator",
                "SF099": "GALILEO IODE",
                **ORBCLK_BLOCK,
                NPHABIASMASK: "Phase bias mask length",
                "SF0102": "GALILEO phase bias mask",
                "groupSF102-BITS": (
                    NPHABIAS,  # repeating group * num bits set in SF0102
                    {
                        **PHAS_BIAS_BLOCK,
                    },
                ),
                NCODBIASMASK: "Code bias mask length",
                "SF0105": "GALILEO code bias mask",
                "groupSF105-BITS": (
                    NCODBIAS,  # repeating group * num bits set in SF0105
                    {
                        "SF029": "Code bias correction",
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-OCB-BEI": {
        **OCB_HDR,
        "SF097": "BEIDOU Ephemeris type",
        NSATMASK: "Satellite mask length",
        "SF094": "BEIDOU Satellite mask",
        "groupSat": (  # Satellite Block table 6.4
            NSAT,  # repeating group * num bits set in SF094
            {
                "SF013": "Do not use (DNU)",
                "SF014": "OCB present flags",
                "SF015": "Continuity indicator",
                "SF0100": "BEIDOU IODE",
                **ORBCLK_BLOCK,
                NPHABIASMASK: "Phase bias mask length",
                "SF0103": "BEIDOU phase bias mask",
                "groupSF103-BITS": (
                    NPHABIAS,  # repeating group * num bits set in SF0103
                    {
                        **PHAS_BIAS_BLOCK,
                    },
                ),
                NCODBIASMASK: "Code bias mask length",
                "SF0106": "BEIDOU code bias mask",
                "groupSF106-BITS": (
                    NCODBIAS,  # repeating group * num bits set in SF0106
                    {
                        "SF029": "Code bias correction",
                    },
                ),
            },
        ),
    },
    "SPARTN-1X-OCB-QZS": {
        **OCB_HDR,
        "SF098": "QZSS Ephemeris type",
        NSATMASK: "Satellite mask length",
        "SF095": "QZSS Satellite mask",
        "groupSat": (  # Satellite Block table 6.4
            NSAT,  # repeating group * num bits set in SF095
            {
                "SF013": "Do not use (DNU)",
                "SF014": "OCB present flags",
                "SF015": "Continuity indicator",
                "SF0101": "QZSS IODE",
                **ORBCLK_BLOCK,
                NPHABIASMASK: "Phase bias mask length",
                "SF0104": "QZSS phase bias mask",
                "groupSF104-BITS": (
                    NPHABIAS,  # repeating group * num bits set in SF0104
                    {
                        **PHAS_BIAS_BLOCK,
                    },
                ),
                NCODBIASMASK: "Code bias mask length",
                "SF0107": "QZSS code bias mask",
                "groupSF107-BITS": (
                    NCODBIAS,  # repeating group * num bits set in SF0107
                    {
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
                    NIONO,  # if SF040I = 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        "SF011": "GPS Satellite mask",
                        "groupSF011": (  # repeating group * num bits set in SF011
                            NSAT,
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
                    NIONO,  # if SF040I = 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        "SF012": "GLONASS Satellite mask",
                        "groupSF012": (  # repeating group * num bits set in SF012
                            NSAT,
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
                    NIONO,  # if SF040I = 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        "SF093": "GALILEO Satellite mask",
                        "groupSF093": (  # repeating group * num bits set in SF093
                            NSAT,
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
                    NIONO,  # if SF040I = 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        "SF094": "BEIDOU Satellite mask",
                        "groupSF094": (  # repeating group * num bits set in SF094
                            NSAT,
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
                    NIONO,  # if SF040I = 1,2
                    {
                        "SF054": "Ionosphere equation type",
                        "SF095": "QZSS Satellite mask",
                        "groupSF095": (  # repeating group * num bits set in SF095
                            NSAT,
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
