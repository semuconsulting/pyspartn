"""
rxmpmp_extract_spartn.py

Extract SPARTN messages from RXM-PMP payloads output by NEO-D9S SPARTN
correction receiver and copy them to a binary output file.

Run from /examples folder.

Usage:

python3 rxmpmp_extract_spartn.py infile=d9s_rxmpmp_data.ubx outfile=d9s_spartn_data.bin

Created on 18 Feb 2023

:author: semuadmin (Steve Smith)
:copyright: semuadmin © 203
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

    counts = {}
    def count(key: str):
        counts[key] = counts.get(key, 0) + 1

    # Read each RXM-PMP message in the input file and
    # accumulate userData into output file
    print(f"Consolidating data from NEO-D9S output log {infile}...")
    with open(outfile, "wb") as out:
        with open(infile, "rb") as stream:
            ubr = UBXReader(stream, quitonerror=ERRLOG)
            for _, parsed in ubr:
                if parsed.identity == "RXM-PMP":
                    count(parsed.identity)
                    if hasattr(parsed, "numBytesUserData"):  # V1
                        datalen = parsed.numBytesUserData
                    else:
                        datalen = 504  # V0
                    out.write(int.to_bytes(parsed.userData, datalen, "little"))

    # Parse the output file for SPARTN messages
    print(f"Parsing consolidated data from {sum(counts.values())} RXM-PMP payloads...")

    counts = {}
    with open(outfile, "rb") as stream:
        try:
            spr = SPARTNReader(stream, quitonerror=ERRIGNORE)
            for _, parsed in spr:
                if isinstance(parsed, SPARTNMessage):
                    count(parsed.identity)

        except AttributeError:  # truncated data
            pass

    print(
        (
            f"Processing complete: {sum(counts.values())} "
            f"messages written to {outfile}:\n{counts}"
        )
    )


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
