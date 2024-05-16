"""
spartn_parser.py

Example use of the SPARTNReader class.

Reads binary file containing ONLY SPARTN messages and prints the
parsed transport layer data. It does NOT decrypt or parse the
message payloads - for that, see example spartn_decrypt.py.

Run from /examples folder.

Usage:

python3 spartn_parser.py infile="d9s_spartn_data.bin"

Created on 12 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from sys import argv

from pyspartn.spartnreader import SPARTNReader


def main(**kwargs):
    """
    Main routine.
    """

    infile = kwargs.get("infile", "d9s_spartn_data.bin")

    i = 0
    with open(infile, "rb") as stream:
        spr = SPARTNReader(stream)
        for _, parsed in spr:
            print(parsed)
            i += 1

    print(f"\n{i} SPARTN messages read from input file {infile}")


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
