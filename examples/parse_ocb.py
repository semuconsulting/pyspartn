"""
parse_ocb.py

Illustration of how convert a parsed and decoded OCB message into an iterable data structure,
with nested arrays for satellite, phase bias and code bias data blocks:

{header: {}, satblock: [satflags: {} orbitblock: {}, clockblock: {}, phasebiasblock: [{}], codebiasblock: [{}]]}

Usage:

python3 parse_ocb.py infile="ocb.log" key="930d847b779b126863c8b3b2766ae7cc", basedate=451169309

Basedate must be in 32-bit gnssTimeTag integer format - use date2timetag() to convert datetime.

Run from within /examples folder - example set up by default to use '/tests/spartnOCB.log' input file.

Created on 15 May 2024

:author: semuadmin (Steve Smith)
:copyright: semuadmin © 2024
:license: BSD 3-Clause
"""

from sys import argv

from pyspartn import (
    CBBITMASKKEY,
    PBBITMASKKEY,
    SATBITMASKKEY,
    SATIODEKEY,
    SPARTNMessage,
    SPARTNReader,
)
from pyspartn.spartntypes_get import PRN

ST = "satblock"
PB = "phasebiasblock"
CB = "codebiasblock"


def parseocb(parsed: SPARTNMessage) -> dict:
    """
    Iterate through parsed and decoded OCB message.

    :param SPARTNMessage parsed: parsed and decoded OCB message
    :return: OCB message as iterable data structure
    :rtype: dict
    """

    # pylint: disable=too-many-locals

    def geta(att: str, i: int = None, n: int = None) -> object:
        """
        Get value of individual attribute within nested group
        """
        for x in (i, n):
            if x is not None:
                att += f"_{x+1:02d}"
        return getattr(parsed, att)

    # get key attributes for this message subtype (i.e. gnss)
    gnss = parsed.identity[-3:]
    satkey = SATBITMASKKEY[gnss]
    pbkey = PBBITMASKKEY[gnss]
    cbkey = CBBITMASKKEY[gnss]
    iodekey = SATIODEKEY[gnss]

    data = {}

    # satellite header
    for attr in (
        "identity",
        "timeTagtype",
        "gnssTimeTag",
        "SF005",
        "SF010",
        "SF069",
        "SF008",
        "SF009",
    ):
        data[attr] = geta(attr)

    data[ST] = []
    # satellite block
    # number of sats = number of set bits in satkey attribute
    for i in range(bin(geta(satkey)).count("1")):
        sat = {}
        dnu = geta("SF013", i)
        if not dnu:
            # satellite flags
            for attr in (PRN, "SF013", "SF014O", "SF014C", "SF014B", "SF015"):
                sat[attr] = geta(attr, i)
            hasorb = geta("SF014O", i)
            hasbias = geta("SF014B", i)
            if hasorb:
                # orbit block
                for attr in (iodekey, "SF020R", "SF020A", "SF020C"):
                    sat[attr] = geta(attr, i)
            # clock block
            for attr in ("SF022", "SF020CK", "SF024"):
                sat[attr] = geta(attr, i)
            if hasbias:
                sat[PB] = []
                # phase bias block
                # number of phase bias entries = number of set bits in pbkey attribute
                for n in range(bin(geta(pbkey, i)).count("1")):
                    ndic = {}
                    for attr in ("PhaseBias", "SF023", "SF015", "SF020PB"):
                        ndic[attr] = geta(attr, i, n)
                    sat[PB].append(ndic)
                sat[CB] = []
                # code bias block
                # number of code bias entries = number of set bits in cbkey attribute
                for n in range(bin(geta(cbkey, i)).count("1")):
                    ndic = {}
                    for attr in ("CodeBias", "SF029"):
                        ndic[attr] = geta(attr, i, n)
                    sat[CB].append(ndic)
            data[ST].append(sat)

    return data


def main(**kwargs):
    """
    Main Routine.
    """

    infile = kwargs.get("filein", "../tests/spartnOCB.log")
    key = kwargs.get("key", "930d847b779b126863c8b3b2766ae7cc")
    basedate = int(kwargs.get("basedate", 451169309))

    with open(infile, "rb") as stream:
        spr = SPARTNReader(stream, decode=True, key=key, basedate=basedate)
        for _, parsed in spr:
            if "OCB" in parsed.identity:
                data = parseocb(parsed)
                print(data, "\n")


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
