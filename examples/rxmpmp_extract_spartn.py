"""
rxmpmp_extract_spartn.py

Extract SPARTN messages from RXM-PMP payloads
output by NEO-D9S SPARTN correction receiver.

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
    ERRRAISE,
    ERRLOG,
    ERRIGNORE,
)

FILENAME = "d9s_rxm_pmp.ubx"

# Read each RXM-PMP message in the input file and
# accumulate userData into payload bytes
print("Parsing output stream from D9S...")
rxm = 0
with open(FILENAME, "rb") as stream:
    ubr = UBXReader(stream, quitonerror=1)
    payload = b""
    for raw, parsed in ubr:
        if parsed.identity == "RXM-PMP":
            rxm += 1
            # print(parsed)
            for i in range(parsed.numBytesUserData):
                val = getattr(parsed, f"userData_{i+1:02}")
                payload += val.to_bytes(1, "big")

# Parse the accumulated RXM-PMP payload bytes for SPARTN messages
print(f"Parsing {rxm} RXM-PMP payloads...")
spn = 0
try:
    spr = SPARTNReader(BytesIO(payload), quitonerror=ERRIGNORE)
    for raw, parsed in spr:
        if isinstance(parsed, SPARTNMessage):
            spn += 1
            print(f"{parsed.identity}, ", end="")

except AttributeError:  # truncated data
    pass

print(f"\n\n{spn} SPARTN messages parsed from {rxm} RXM-PMP message payloads")
