"""
spart_decrypt.py

Illustration of how to read, decrypt and decode the contents
of a binary SPARTN log file e.g. from an Thingstream PointPerfect
SPARTN MQTT service.

NB: decryption requires the key and basedate applicable at the
time the SPARTN log was originally captured.

Usage:

python3 spartn_decrypt.py infile="inputfilename.log"

Run from /examples folder. Can use output from mqtt_spartn_client.py
example.

Created on 12 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from datetime import datetime
from sys import argv

from pyspartn import SPARTNReader

# substitute your values here...
KEY = "930d847b779b126863c8b3b2766ae7cc"
BASEDATE = datetime(2024, 4, 18, 20, 48, 29, 977255)


def main(**kwargs):
    """
    Read, decrypt and decode SPARTN log file.
    """

    infile = kwargs.get("infile", "spartnmqtt.log")
    counts = {"OCB": 0, "HPAC": 0, "GAD": 0}

    with open(infile, "rb") as stream:
        spr = SPARTNReader(
            stream,
            decode=True,
            key=KEY,
            basedate=BASEDATE,
        )
        for _, parsed in spr:
            for key in counts:
                if key in parsed.identity:
                    counts[key] += 1
            print(parsed)

    print(f"SPARTN messages read from {infile}: {str(counts).strip('{}')}")


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
