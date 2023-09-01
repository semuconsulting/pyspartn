"""
rxmpmp_extract_spartn.py

Extract SPARTN messages from RXM-PMP payloads output by NEO-D9S SPARTN
correction receiver and copy them to a binary output file.

Run from /examples folder.

Created on 18 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 203
:license: BSD 3-Clause
"""
# pylint: disable=unused-import, invalid-name

from io import BytesIO
from pyubx2 import UBXReader
from pyspartn import (
    SPARTNReader,
    SPARTNMessage,
    ERRIGNORE,
)

FILEIN = "d9s_rxmpmp_data.ubx"
FILEOUT = "d9s_spartn_data.log"

counts = {"PMP": 0, "HPAC": 0, "OCB": 0, "GAD": 0}
# Read each RXM-PMP message in the input file and
# accumulate userData into payload bytes
print(f"Consolidating data from NEO-D9S output log {FILEIN}...")
with open(FILEIN, "rb") as stream:
    ubr = UBXReader(stream, quitonerror=1)
    payload = b""
    for raw, parsed in ubr:
        if parsed.identity == "RXM-PMP":
            counts["PMP"] += 1
            # print(parsed)
            for i in range(parsed.numBytesUserData):
                val = getattr(parsed, f"userData_{i+1:02}")
                payload += val.to_bytes(1, "big")

# Parse the accumulated RXM-PMP payload bytes for SPARTN messages
print(f"\n\nParsing consolidated data from {counts['PMP']} RXM-PMP payloads...")

spn = 0
with open(FILEOUT, "wb") as outfile:
    try:
        spr = SPARTNReader(BytesIO(payload), quitonerror=ERRIGNORE)
        for raw, parsed in spr:
            if isinstance(parsed, SPARTNMessage):
                for key in counts:
                    if key in parsed.identity:
                        counts[key] += 1
                spn += 1
                print(f"{parsed.identity}, ", end="")
                outfile.write(raw)

    except AttributeError:  # truncated data
        pass

print(f"\n\nProcessing complete: {counts} messages written to {FILEOUT}")
