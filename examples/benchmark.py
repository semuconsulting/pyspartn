"""
pyspartn Performance benchmarking utility

Usage (kwargs optional): python3 benchmark.py cycles=10000

Created on 18 Feb 2022

:author: semuadmin
:copyright: SEMU Consulting © 2022
:license: BSD 3-Clause
"""
# pylint: disable=line-too-long

from datetime import datetime
from platform import python_version
from platform import version as osver
from sys import argv
from time import process_time_ns

from pyspartn import SPARTNReader
from pyspartn import _version as spartnver

KEY = "930d847b779b126863c8b3b2766ae7cc"
BASEDATE = (datetime(2024, 4, 12, 9, 17, 0),)

SPARTNMESSAGES = [
    b's\x00\x12\xe2\x08\xd6\xde\x07\xe8[\x11\x88CO\xe7Z\x9e\x91\x85\xd1\x9a\x14t\x7f,\xe1\x0e\xaa\xc9OX\xa5\xf1\x12\xb3\x02\xc0`F\xf8H\xba\xfa\x0c\xda\xee=q\xcd\x00\x057',
    b's\x00\x10\xe3\x18\xd6\xdfX\xd8[\x10H\xa8\xff;\xec\xe7>;\x91\xbe\xa4\xa0p0\x1b~\xf3\x8a;N\xb6\xc5b\x9eQ\xbb.>\x98O\x0f\x18\xd7\xc6\xa6\xa0~',
    b's\x00\x16i(\xd6\xde\x07\xe8[\x12\xc8\xa8\x94)\xa6)7\xd2\xe5\xdb\x06\xe0\xfaQ\xd0\xc958 \xacw\x14I\x92q\x98\xe2\xe2\xa2\xe0-X\x01Xe\xd1\x14\x18Z8\xae<\xad\x83\xdd\xbe`\xeb',
    b's\x00\x12\xe2\x08\xd6\xde\x07\xe8[\x11\x88CO\xe7Z\x9e\x91\x85\xd1\x9a\x14t\x7f,\xe1\x0e\xaa\xc9OX\xa5\xf1\x12\xb3\x02\xc0`F\xf8H\xba\xfa\x0c\xda\xee=q\xcd\x00\x057',
    b's\x00\x10\xe3\x18\xd6\xdfX\xd8[\x10H\xa8\xff;\xec\xe7>;\x91\xbe\xa4\xa0p0\x1b~\xf3\x8a;N\xb6\xc5b\x9eQ\xbb.>\x98O\x0f\x18\xd7\xc6\xa6\xa0~',
    b's\x00\x16i(\xd6\xde\x07\xe8[\x12\xc8\xa8\x94)\xa6)7\xd2\xe5\xdb\x06\xe0\xfaQ\xd0\xc958 \xacw\x14I\x92q\x98\xe2\xe2\xa2\xe0-X\x01Xe\xd1\x14\x18Z8\xae<\xad\x83\xdd\xbe`\xeb'
]

def progbar(i: int, lim: int, inc: int = 20):
    """
    Display progress bar on console.

    :param int i: iteration
    :param int lim: max iterations
    :param int inc: bar increments (20)
    """

    i = min(i, lim)
    pct = int(i * inc / lim)
    if not i % int(lim / inc):
        print(
            f"{int(pct*100/inc):02}% " + "\u2593" * pct + "\u2591" * (inc - pct),
            end="\r",
        )


def benchmark(**kwargs) -> float:
    """
    pyrtcm Performance benchmark test.

    :param int cycles: (kwarg) number of test cycles (10,000)
    :returns: benchmark as transactions/second
    :rtype: float
    :raises: UBXStreamError
    """

    cyc = int(kwargs.get("cycles", 10000))
    txnc = len(SPARTNMESSAGES)
    txnt = txnc * cyc

    print(
        f"\nOperating system: {osver()}",
        f"\nPython version: {python_version()}",
        f"\npyrtcm version: {spartnver}",
        f"\nTest cycles: {cyc:,}",
        f"\nTxn per cycle: {txnc:,}",
    )

    start = process_time_ns()
    print(f"\nBenchmark (no decrypt) test started at {start}")
    for i in range(cyc):
        progbar(i, cyc)
        for msg in SPARTNMESSAGES:
            _ = SPARTNReader.parse(msg, decode=False)
    end = process_time_ns()
    print(f"Benchmark (no decrypt) test ended at {end}.")
    duration = end - start
    rate = round(txnt * 1e9 / duration, 2)

    print(
        f"\n{txnt:,} undecrypted messages processed in {duration/1e9:,.3f} seconds = {rate:,.2f} txns/second.\n"
    )

    start = process_time_ns()
    print(f"\nBenchmark (decrypt) test started at {start}")
    for i in range(cyc):
        progbar(i, cyc)
        for msg in SPARTNMESSAGES:
            _ = SPARTNReader.parse(msg, decode=True, key=KEY, basedate=BASEDATE)
    end = process_time_ns()
    print(f"Benchmark (decrypt) test ended at {end}.")
    duration = end - start
    rate = round(txnt * 1e9 / duration, 2)

    print(
        f"\n{txnt:,} decrypted messages processed in {duration/1e9:,.3f} seconds = {rate:,.2f} txns/second.\n"
    )

    return rate


def main():
    """
    CLI Entry point.

    args as benchmark() method
    """

    benchmark(**dict(arg.split("=") for arg in argv[1:]))


if __name__ == "__main__":
    main()
