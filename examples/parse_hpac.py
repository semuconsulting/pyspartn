"""
parse_hpac.py

Illustration of how convert a parsed and decoded HPAC message into an iterable data structure,
with nested arrays for atmospheric area and ionosphere data blocks:

{header: {}, atmareablock: [areablock: {} tropblock: {}, ionblock: [{}]]}

Usage:

python3 parse_hpac.py infile="hpac.log" key="930d847b779b126863c8b3b2766ae7cc", basedate=451169309

Basedate must be in 32-bit gnssTimeTag integer format - use date2timetag() to convert datetime.

Run from within \examples folder - example set up by default to use '/tests/spartnHPAC.log' input file.

Created on 15 May 2024

:author: semuadmin
:copyright: SEMU Consulting © 2024
:license: BSD 3-Clause
"""

from sys import argv

from pyspartn import (
    SATBITMASKKEY,
    SPARTNMessage,
    SPARTNReader,
)
from pyspartn.spartntypes_get import PRN

AT = "atmareablock"
TB = "troposphereblock"
IB = "ionosphereblock"


def parsehpac(parsed: SPARTNMessage) -> dict:
    """
    Iterate through parsed and decoded HPAC message.

    :param SPARTNMessage parsed: parsed and decoded HPAC message
    :return: HPAC message as iterable data structure
    :rtype: dict
    """

    # pylint: disable=too-many-locals

    def geta(att: str, idx: str = "") -> object:
        """
        Get value of individual attribute within group
        """
        return getattr(parsed, att + idx)

    # get key attributes for this message subtype (i.e. gnss)
    gnss = parsed.identity[-3:]
    satkey = SATBITMASKKEY[gnss]

    data = {}

    # header
    for attr in ("identity", "SF005", "SF068", "SF069", "SF030"):
        data[attr] = geta(attr)

    data[AT] = []
    # atmosphere area block
    # number of entries = SF030 + 1
    for i in range(parsed.SF030 + 1):
        dic = {}
        idx = f"_{i+1:02d}"
        # area data block
        for attr in ("SF031", "SF039", "SF040T", "SF040I"):
            dic[attr] = geta(attr, idx)
        # data[AT].append(dic)

        hastropa = geta("SF040T", idx) in (1, 2)
        hastropb = geta("SF040T", idx) == 2
        hasiona = geta("SF040I", idx) in (1, 2)
        hasionb = geta("SF040I", idx) == 2

        if hastropa:
            dic[TB] = {}
            # troposphere data block a
            for attr in ("SF041", "SF042", "SF043", "SF044"):
                dic[TB][attr] = geta(attr, idx)
            sf041 = dic[TB]["SF041"]
            sf044 = dic[TB]["SF044"]
            if sf044 == 0:
                dic[TB]["SF045"] = geta("SF045", idx)
                if sf041 in (1, 2):
                    for attr in ("SF046a", "SF046b"):
                        dic[TB][attr] = geta(attr, idx)
                if sf041 == 2:
                    for attr in "SF047":
                        dic[TB][attr] = geta(attr, idx)
            elif sf044 == 1:
                dic[TB]["SF048"] = geta("SF048", idx)
                if sf041 in (1, 2):
                    for attr in ("SF049a", "SF049b"):
                        dic[TB][attr] = geta(attr, idx)
                if sf041 == 2:
                    for attr in "SF050":
                        dic[TB][attr] = geta(attr, idx)
            if hastropb:
                # troposphere data block b
                sf051 = geta("SF051", idx)
                dic[TB]["SF051"] = sf051
                if sf051 == 0:
                    dic[TB]["SF052"] = geta("SF052", idx)
                elif sf051 == 1:
                    dic[TB]["SF053"] = geta("SF053", idx)
        # data[AT].append(dic)

        if hasiona:
            sf054 = geta("SF054", idx)
            dic["SF054"] = sf054
            dic[IB] = []
            # ionosphere data block a
            # number of entries = number of set bits in satkey attribute
            for n in range(bin(geta(satkey, idx)).count("1")):
                ndic = {}
                nidx = f"_{i+1:02d}_{n+1:02d}"
                for attr in (PRN, "SF055", "SF056"):
                    ndic[attr] = geta(attr, nidx)
                sf056 = ndic["SF056"]
                if sf056 == 0:
                    ndic["SF057"] = geta("SF057", nidx)
                    if sf054 in (1, 2):
                        for attr in ("SF058a", "SF058b"):
                            ndic[attr] = geta(attr, nidx)
                    if sf054 == 2:
                        for attr in "SF059":
                            ndic[attr] = geta(attr, nidx)
                elif sf056 == 1:
                    ndic["SF060"] = geta("SF060", nidx)
                    if sf054 in (1, 2):
                        for attr in ("SF061a", "SF061b"):
                            ndic[attr] = geta(attr, nidx)
                    if sf054 == 2:
                        for attr in "SF062":
                            ndic[attr] = geta(attr, nidx)
                if hasionb:
                    # ionosphere data block b
                    sf063 = geta("SF063", nidx)
                    ndic["SF063"] = sf063
                    attr = ["SF064", "SF065", "SF066", "SF067"][sf063]
                    ndic[attr] = geta(attr, nidx)
                dic[IB].append(ndic)
        data[AT].append(dic)

    return data


def main(**kwargs):
    """
    Main Routine.
    """

    infile = kwargs.get("filein", "../tests/spartnHPAC.log")
    key = kwargs.get("key", "930d847b779b126863c8b3b2766ae7cc")
    basedate = int(kwargs.get("basedate", 451169309))

    with open(infile, "rb") as stream:
        spr = SPARTNReader(stream, decode=True, key=key, basedate=basedate)
        for _, parsed in spr:
            if "HPAC" in parsed.identity:
                data = parsehpac(parsed)
                print(data, "\n")


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
