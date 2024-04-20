"""
rxmpmp_extract_spartn.py

Extract SPARTN messages from RXM-PMP payloads output by NEO-D9S SPARTN
correction receiver and copy them to a binary output file.

Run from /examples folder.

Usage:

python3 rxmpmp_extract_spartn.py infile="d9s_rxmpmp_data.ubx" outfile="d9s_spartn_data.bin"

Created on 18 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 203
:license: BSD 3-Clause
"""

# pylint: disable=invalid-name

from sys import argv

from pyubx2 import UBXReader

from pyspartn import ERRIGNORE, ERRLOG, SPARTNMessage, SPARTNReader


def main(**kwargs):
    """
    Main routine.
    """

    infile = kwargs.get("infile", "d9s_rxmpmp_data.ubx")
    outfile = kwargs.get("outfile", "d9s_spartn_data.bin")

    counts = {"PMP": 0, "HPAC": 0, "OCB": 0, "GAD": 0}
    # Read each RXM-PMP message in the input file and
    # accumulate userData into output file
    print(f"Consolidating data from NEO-D9S output log {infile}...")
    with open(outfile, "wb") as out:
        with open(infile, "rb") as stream:
            ubr = UBXReader(stream, quitonerror=ERRLOG)
            for _, parsed in ubr:
                if parsed.identity == "RXM-PMP":
                    counts["PMP"] += 1
                    # print(parsed)
                    payload = b""
                    for i in range(parsed.numBytesUserData):
                        payload += getattr(parsed, f"userData_{i+1:02}").to_bytes(
                            1, "big"
                        )
                    out.write(payload)

    # Parse the output file for SPARTN messages
    print(f"\n\nParsing consolidated data from {counts['PMP']} RXM-PMP payloads...")

    with open(outfile, "rb") as stream:
        try:
            spr = SPARTNReader(stream, quitonerror=ERRIGNORE)
            for _, parsed in spr:
                if isinstance(parsed, SPARTNMessage):
                    for key in counts:
                        if key in parsed.identity:
                            counts[key] += 1
                    print(f"{parsed.identity}, ", end="")

        except AttributeError:  # truncated data
            pass

    print(f"\n\nProcessing complete: {counts} messages written to {outfile}")


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
