"""
spart_decrypt.py

Illustration of how to read, decrypt and parse the contents
of a binary SPARTN log file e.g. from an Thingstream PointPerfect
SPARTN MQTT or NTRIP service.

NB: decryption requires the key and basedate applicable at the
time the SPARTN log was originally captured.

Usage:

python3 spartn_decrypt.py infile="inputfilename.log" key="bc75cdd919406d61c3df9e26c2f7e77a", basedate=431287200

Basedate must be in 32-bit gnssTimeTag integer format - use date2timetag() to convert datetime.

Run from /examples folder. Example is set up to use 'd9s_spartn_data.bin' file by default.

FYI: SPARTNMessage objects implement a protected attribute `_padding`,
which represents the number of redundant bits added to the payload
content in order to byte-align the payload with the exact number of
bytes specified in the transport layer payload length nData. If the
payload has been successfully decrypted and decoded, the value of
_padding should always be between 0 and 8.

Created on 12 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from datetime import datetime, timezone
from sys import argv

from pyspartn import SPARTNReader


def main(**kwargs):
    """
    Read, decrypt and decode SPARTN log file.
    """

    infile = kwargs.get("infile", "d9s_spartn_data.bin")
    key = kwargs.get("key", "bc75cdd919406d61c3df9e26c2f7e77a")
    basedate = int(kwargs.get("basedate", 431287200))
    if basedate == 0:  # default to now()
        basedate = datetime.now(tz=timezone.utc)
    counts = {"OCB": 0, "HPAC": 0, "GAD": 0}

    with open(infile, "rb") as stream:
        spr = SPARTNReader(
            stream,
            decode=True,
            key=key,
            basedate=basedate,
            quitonerror=0,
        )
        for _, parsed in spr:
            for key in counts:
                if key in parsed.identity:
                    counts[key] += 1
            # print(parsed)
            # uncomment this line for an informal check on successful decryption...
            print(f"{parsed.identity} - Decrypted OK? {0 <= parsed._padding <= 8}")

    print(f"SPARTN messages read from {infile}: {str(counts).strip('{}')}")


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
