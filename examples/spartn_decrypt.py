"""
spart_decrypt.py

Illustration of how to read, decrypt and decode the contents
of a binary SPARTN log file e.g. from an Thingstream PointPerfect
SPARTN MQTT or NTRIP service.

NB: data stream must ONLY contain SPARTN protocol messages. If you're
capturing a log from a Thingstream PointPerfect SPARTN MQTT service,
disable the 'Key' and 'Assist' topics, as these return UBX protocol
messages.

At time of writing, the MQTT service uses encrypted payloads (`eaf=1`).
In order to decrypt and decode these payloads, a valid decryption `key`
is required. Keys are typically 32-character hexadecimal strings valid
for a 4 week period e.g. "bc75cdd919406d61c3df9e26c2f7e77a"

In addition to the key, the SPARTN decryption algorithm requires a 32-bit
`gnssTimeTag` value. The provision of this 32-bit `gnssTimeTag` depends on
the incoming data stream:
- Some SPARTN message types (*e.g. HPAC and a few OCB messages*) include
  the requisite 32-bit `gnssTimeTag` in the message header (denoted by
  `timeTagtype=1`). Others (*e.g. GAD and most OCB messages*) use an
  ambiguous 16-bit `gnssTimeTag` value for reasons of brevity (denoted by
  `timeTagtype=0`). In these circumstances, a nominal 'basedate' must be
  provided by the user, representing the UTC datetime on which the datastream
  was originally created to the nearest half day, in order to convert the
  16-bit `gnssTimeTag` to an unambiguous 32-bit value.
- If you're parsing data in real time, this basedate can be set to `None` and
  will default to the current UTC datetime `datetime.now(timezone.utc)`.
- If you're parsing historical data, you will need to provide a basedate
  representing the UTC datetime on which the data stream was originally
  created, to the nearest half day, or...
- If a nominal basedate of `TIMEBASE` (`datetime(2010, 1, 1, 0, 0, tzinfo=timezone.utc)`)
  is provided, `pyspartn.SPARTNReader` can *attempt* to derive the requisite `gnssTimeTag`
  value from any 32-bit `gnssTimetag` in a preceding message of the same subtype in the
  same data stream, but *unless and until this eventuality occurs (e.g. unless an HPAC
  message precedes an OCB message of the same subtype), decryption may fail*. Always set
  the `quitonerror` argument to `ERRLOG` or `ERRIGNORE` to log or ignore such initial
  failures.

Usage:

python3 spartn_decrypt.py infile="inputfilename.log" key="bc75cdd919406d61c3df9e26c2f7e77a", \
    basedate=431287200

Basedate must be in 32-bit gnssTimeTag integer format - use date2timetag() to convert datetime.

Run from /examples folder. Example is set up to use 'd9s_spartn_data.bin' file by default.

Created on 12 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from datetime import datetime, timezone
from sys import argv

from pyspartn import SPARTNDecryptionError, SPARTNReader, TIMEBASE

DEMO_DATASTREAM = "d9s_spartn_data.bin"
DEMO_KEY = "bc75cdd919406d61c3df9e26c2f7e77a"

# UNCOMMENT ONE OF THE FOLLOWING DEMO BASEDATES TO SEE THE
# EFFECTS OF USING DIFFERENT BASEDATE VALUES ...

# None (will default to current utc datetime)
# (this will fail for any messages where timeTagtype=0)
# DEMO_BASEDATE = None

# attempt to get 32-bit gnssTimeTag from data stream
# (this may fail for some early messages where timeTagtype=0,
# but should work for all messages thereafter)
DEMO_BASEDATE = TIMEBASE

# the actual original basedate for the demo d9s_spartn_data.bin data stream,
# equivalent to a 32-bit gnssTimeTag = 431287200
# (this should work for all incoming messages)
# DEMO_BASEDATE = datetime(2023, 9, 1, 18, 0, 0, 0, timezone.utc)


def main(**kwargs):
    """
    Read, decrypt and decode SPARTN log file.
    """

    infile = kwargs.get("infile", DEMO_DATASTREAM)
    key = kwargs.get("key", DEMO_KEY)
    basedate = kwargs.get("basedate", DEMO_BASEDATE)
    if basedate is not None and not isinstance(basedate, datetime):
        basedate = int(basedate)
    counts = {"OCB": 0, "HPAC": 0, "GAD": 0, "TOTAL": 0, "ERRORS": 0}

    with open(infile, "rb") as stream:
        spr = SPARTNReader(
            stream,
            decode=True,
            key=key,
            basedate=basedate,
            quitonerror=0,
        )
        eof = False
        while not eof:
            try:
                # not using iterator as we want to capture Exceptions...
                raw, parsed = spr.read()
                if parsed is not None:
                    for key in counts:
                        if key in parsed.identity:
                            counts[key] += 1
                    print(
                        (
                            f"{parsed.identity=}, {parsed.eaf=}, "
                            f"{parsed.timeTagtype=}, {parsed.gnssTimeTag=}"
                        )
                    )
                    counts["TOTAL"] += 1
                else:
                    eof = True

            except SPARTNDecryptionError as err:
                print(err)
                counts["ERRORS"] += 1
                continue

    print(
        f"\nSPARTN messages decrypted and decoded from {infile}:\n{str(counts).strip("{}")}"
    )


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
