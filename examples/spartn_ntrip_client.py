"""
spartn_ntrip_client.py

Illustration of SPARTN NTRIP Client using GNSSNTRIPClient
class from pygnssutils library. Can be used with the 
u-blox Thingstream PointPerfect NTRIP service.

NB: requires a valid userid and password. These can be set as
environment variables PYGPSCLIENT_USER and PYGPSCLIENT_PASSWORD,
or passed as keyword arguments user and password.

The contents of the binary output file can be parsed and decoded using
the spartn_decrypt.py example. At time of writing the PointPerfect
NTRIP service is unencrypted (eaf=0), so key and basedate can be set
to arbitrary values.

Usage:

python3 spartn_ntrip_client.py user="youruser" password="yourpassword" outfile="spartnntrip.log"

Run from /examples folder.

Created on 12 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

from os import getenv
from sys import argv
from time import sleep

from pygnssutils import GNSSNTRIPClient

SERVER = "ppntrip.services.u-blox.com"
PORT = 2102
HTTPS = 1
MOUNTPOINT = "EU"  # amend to your region


def main(**kwargs):
    """
    Main routine.
    """

    user = kwargs.get("user", getenv("PYGPSCLIENT_USER", "user"))
    password = kwargs.get("password", getenv("PYGPSCLIENT_PASSWORD", "password"))
    outfile = kwargs.get("outfile", "spartnntrip.log")

    with open(outfile, "wb") as out:
        gnc = GNSSNTRIPClient()

        print(f"SPARTN NTRIP Client started, writing output to {outfile}...")
        gnc.run(
            server=SERVER,
            port=PORT,
            https=HTTPS,
            mountpoint=MOUNTPOINT,
            datatype="SPARTN",
            ntripuser=user,
            ntrippassword=password,
            ggainterval=-1,
            output=out,
        )

        try:
            while True:
                sleep(3)
        except KeyboardInterrupt:
            print("SPARTN NTRIP Client terminated by User")
            print(
                f"The spartn_decrypt.py example can be used to parse the contents of the output file {outfile}:\n",
                f"python3 spartn_decrypt.py infile=spartnntrip.log",
            )


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
