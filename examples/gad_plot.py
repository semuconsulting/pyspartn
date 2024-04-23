"""
gad_plot.py

Extracts geographic area definition coordinates from
SPARTN-1X-GAD messages in a binary SPARTN log file and saves them
to a CSV file in WKT POLYGON format. This WKT format can be imported
into a GIS desktop tool like QGIS (using the Add Layer...Delimited Text
Layer function) to display the areas on a map. 

See, for example, gad_plot_map.png.

Usage:

python3 gad_plot.py infile=""d9s_spartn_data.bin" outfile="spartnGAD.csv"

Run from /examples folder.

This example illustrates how to decrypt SPARTN message payloads using the
SPARTNMessage class. A suitable input log file can be produced from a raw
NEO-D9S output data stream using the rxmpmp_extract_spartn.py example.

In order to decrypt the messages, you'll need:
- the SPARTN decryption key valid on the basedate.
- the 'basedate' (datetime the SPARTN data stream was originally
captured, to the nearest half day - or derive this from a 32-bit
gnssTimeTag in the same data stream)

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

from datetime import datetime
from sys import argv

from pyspartn import ERRIGNORE, SPARTNReader, enc2float

# substitute your values here...
# these are valid for the d9s_rxmpmp_data.ubx example file
KEY = "bc75cdd919406d61c3df9e26c2f7e77a"
BASEDATE = datetime(2023, 9, 1, 18, 0, 0)  # datetime(2023, 6, 27, 22, 3, 0)
# or, if you have a 32-bit gnssTimeTag rather than a date...
# BASEDATE = 425595780


def groupatt(msg, att, n):
    """
    Get value of individual attribute within group
    """
    return getattr(msg, f"{att}_{n+1:02}")


def main(**kwargs):
    """
    Main routine.
    """

    infile = kwargs.get("infile", "d9s_spartn_data.bin")
    outfile = kwargs.get("outfile", "spartnGAD.csv")

    with open(outfile, "w", encoding="utf-8") as fileout:
        with open(infile, "rb") as stream:
            spr = SPARTNReader(
                stream,
                decode=True,
                key=KEY,
                basedate=BASEDATE,
                quitonerror=ERRIGNORE,
            )
            count = 0
            fileout.write("areaid,area\n")  # header
            for _, parsed in spr:
                if parsed.identity == "SPARTN-1X-GAD":
                    # NB: SF030 = number of areas N - 1
                    for i in range(parsed.SF030 + 1):
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
                        print(
                            f"{areaid}: {lon1:.3f}, {lat1:.3f} - {lon2:.3f}, {lat2:.3f}"
                        )
                        fileout.write(areapoly)
                        count += 1

    print(f"{count} GAD area definitions captured in {outfile}")


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
