"""
spartn_parser.py

Example use of the SPARTNReader class.

Reads binary file containing ONLY SPARTN messages
(e.g. from MQTT /pp/ip topic or L-band RXM-PMP data stream)
and prints the parsed transport layer data.

Run from /examples folder.

Created on 12 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from pyspartn.spartnreader import SPARTNReader

INFILE = "d9s_spartn_data.log"

i = 0
with open(INFILE, "rb") as stream:
    spr = SPARTNReader(stream)
    for raw_data, parsed_data in spr:
        print(parsed_data)
        i += 1

print(f"\n{i} SPARTN messages read from input file")
