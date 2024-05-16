"""
parse_gad.py

Extracts geographic area definition coordinates from
SPARTN-1X-GAD messages in a binary SPARTN log file and saves them
to a CSV file in WKT POLYGON format. This WKT format can be imported
into a GIS desktop tool like QGIS (using the Add Layer...Delimited Text
Layer function) to display the areas on a map. 

See, for example, gad_plot_map.png.

Usage:

python3 gad_plot.py infile=""d9s_spartn_data.bin" outfile="spartnGAD.csv" key="bc75cdd919406d61c3df9e26c2f7e77a", basedate=431287200

Basedate must be in 32-bit gnssTimeTag integer format - use date2timetag() to convert datetime.

Run from /examples folder. Example is set up to use 'd9s_spartn_data.bin' file by default.

Output should look something like this:

areaid,area
"0","POLYGON ((12.500 71.500, 12.500 74.900, 31.700 74.900, 31.700 71.500, 12.500 71.500))"
"1","POLYGON ((10.200 68.200, 10.200 71.600, 21.700 71.600, 21.700 68.200, 10.200 68.200))"
"2","POLYGON ((21.700 68.300, 21.700 71.800, 30.200 71.800, 30.200 68.300, 21.700 68.300))"
etc.

Created on 20 May 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

# pylint: disable=too-many-locals

from datetime import datetime, timezone
from sys import argv

from pyspartn import ERRIGNORE, SPARTNMessage, SPARTNReader


def parsegad(parsed: SPARTNMessage) -> list:
    """
    Main routine.

    :param SPARTNMessage parsed: parsed and decoded GAD message
    :return: list of area coordinates in WKT format
    :rtype: list
    """

    def geta(att: str, i: int = None) -> object:
        """
        Get value of individual attribute within group
        """
        if i is not None:
            att += f"_{i+1:02d}"
        return getattr(parsed, att)

    data = []
    # NB: SF030 = (area count - 1), need to add 1 for range
    for i in range(parsed.SF030 + 1):
        areaid = geta("SF031", i)
        lat1 = geta("SF032", i)
        lon1 = geta("SF033", i)
        latnodes = geta("SF034", i)
        lonnodes = geta("SF035", i)
        latspacing = geta("SF036", i)
        lonspacing = geta("SF037", i)
        lat2 = lat1 - (latnodes * latspacing)
        lon2 = lon1 + (lonnodes * lonspacing)
        areapoly = (
            f'"{areaid}","POLYGON (({lon1:.3f} {lat1:.3f}, {lon1:.3f} {lat2:.3f},'
            + f"{lon2:.3f} {lat2:.3f}, {lon2:.3f} {lat1:.3f},"
            + f'{lon1:.3f} {lat1:.3f}))"\n'
        )
        data.append(areapoly)
    return data


def main(**kwargs):
    """
    Main Routine.
    """

    infile = kwargs.get("infile", "d9s_spartn_data.bin")
    outfile = kwargs.get("outfile", "spartnGAD.csv")
    key = kwargs.get("key", "bc75cdd919406d61c3df9e26c2f7e77a")
    basedate = int(kwargs.get("basedate", 431287200))
    if basedate == 0:  # default to now()
        basedate = datetime.now(tz=timezone.utc)

    print(f"Processing input file {infile}...")
    with open(outfile, "w", encoding="utf-8") as fileout:
        with open(infile, "rb") as stream:
            spr = SPARTNReader(
                stream,
                decode=True,
                key=key,
                basedate=basedate,
                quitonerror=ERRIGNORE,
            )
            count = 0
            fileout.write("areaid,area\n")  # header
            for _, parsed in spr:
                if parsed.identity == "SPARTN-1X-GAD":
                    data = parsegad(parsed)
                    for area in data:
                        fileout.write(area)
                    count += 1

    print(f"{count} GAD area definitions captured in {outfile}")


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
