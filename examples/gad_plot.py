"""
gad_plot.py

Extracts geographic area definition coordinates from
SPARTN-1X-GAD messages and saves them to a CSV file in
WKT POLYGON format. You can import this format into a GIS desktop
tool like QGIS (using the Add Layer...Delimited Text Layer function)
to display the areas on a map.

In order to decode the messages, you'll need:
- the 'basedate' (datetime the SPARTN data stream was originally
captured, to the nearest half day - or derive this from a 32-bit
gnssTimeTag in the same data stream)
- the SPARTN decryption key valid on the basedate.

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
# pylint: disable=invalid-name, unused-import

from datetime import datetime, timedelta
from pyspartn import SPARTNReader, enc2float, timetag2date

INFILE = "spartn_ip.log"
OUTFILE = "spartnGAD.csv"
KEY = "6b30302427df05b4d98911ebff3a4d95"
BASEDATE = datetime(2023, 6, 27, 22, 3, 0)
# or, if you have a 32-bit gnssTimeTag rather than a date...
# BASEDATE = 425595780


def groupatt(msg, att, n):
    """
    Get value of individual attribute within group
    """
    return getattr(msg, f"{att}_{n+1:02}")


with open(OUTFILE, "w", encoding="utf-8") as outfile:
    with open(INFILE, "rb") as infile:
        spr = SPARTNReader(
            infile,
            decode=True,
            key=KEY,
            basedate=BASEDATE,
            quitonerror=2,
        )
        count = 0
        outfile.write("areaid,area\n")  # header
        for raw, parsed in spr:
            if parsed.identity == "SPARTN-1X-GAD":
                for i in range(parsed.SF030):
                    areaid = groupatt(parsed, "SF031", i)
                    lat1 = enc2float(groupatt(parsed, "SF032", i), 0.1, -90)
                    lon1 = enc2float(groupatt(parsed, "SF033", i), 0.1, -180)
                    latnodes = groupatt(parsed, "SF034", i)
                    lonnodes = groupatt(parsed, "SF035", i)
                    latspacing = enc2float(groupatt(parsed, "SF036", i), 0.1, 0.1)
                    lonspacing = enc2float(groupatt(parsed, "SF037", i), 0.1, 0.1)
                    lat2 = lat1 - (latnodes * latspacing)
                    lon2 = lon1 + (lonnodes * lonspacing)
                    areapoly = (
                        f'"{areaid}","POLYGON (({lon1:.3f} {lat1:.3f}, {lon1:.3f} {lat2:.3f},'
                        + f"{lon2:.3f} {lat2:.3f}, {lon2:.3f} {lat1:.3f},"
                        + f'{lon1:.3f} {lat1:.3f}))"\n'
                    )
                    print(f"{areaid}: {lon1:.3f}, {lat1:.3f} - {lon2:.3f}, {lat2:.3f}")
                    outfile.write(areapoly)
                    count += 1

print(f"{count} GAD area definitions captured in {OUTFILE}")
