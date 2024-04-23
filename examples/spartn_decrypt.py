"""
spart_decrypt.py

Illustration of how to read, decrypt and decode the contents
of a binary SPARTN log file e.g. from an Thingstream PointPerfect
SPARTN MQTT or NTRIP service.

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
# these are valid for the d9s_rxmpmp_data.ubx example file
KEY = "bc75cdd919406d61c3df9e26c2f7e77a"
BASEDATE = datetime(2023, 9, 1, 18, 0, 0)  # datetime(2023, 6, 27, 22, 3, 0)


def main(**kwargs):
    """
    Read, decrypt and decode SPARTN log file.
    """

    infile = kwargs.get("infile", "d9s_rxmpmp_data.ubx")
    counts = {"OCB": 0, "HPAC": 0, "GAD": 0}

    with open(infile, "rb") as stream:
        spr = SPARTNReader(
            stream,
            decode=True,
            key=KEY,
            basedate=BASEDATE,
            quitonerror=0,
        )
        for _, parsed in spr:
            for key in counts:
                if key in parsed.identity:
                    counts[key] += 1
            print(parsed.identity, parsed._padding)

    print(f"SPARTN messages read from {infile}: {str(counts).strip('{}')}")


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
