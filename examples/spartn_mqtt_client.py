"""
spartn_mqtt_client.py

Illustration of SPARTN MQTT Client using GNSSMQTTClient
class from pygnssutils library. Can be used with the
u-blox Thingstream PointPerfect MQTT service.

NB: requires a valid ClientID and TLS cert (*.crt) and key (*.pem)
files - these can be downloaded from your Thingstream account.
ClientID can be set using environment variable MQTTCLIENTID or
passed as the keyword argument clientid. The cert and key files
should be stored in the user's home directory.

The contents of the binary output file can be parsed and decoded
using the spartn_decrypt.py example.

Usage:

python3 spartn_mqtt_client.py clientid="abcd1234-abcd-efgh-4321-1234567890ab" region="eu" outfile="spartnmqtt.log"

Run from /examples folder.

Created on 12 Feb 2023

:author: semuadmin (Steve Smith)
:copyright: semuadmin © 2023
:license: BSD 3-Clause
"""

from datetime import datetime, timezone
from os import path, getenv
from pathlib import Path
from sys import argv
from time import sleep

from pyspartn import date2timetag
from pygnssutils import GNSSMQTTClient


SERVER = "pp.services.u-blox.com"
PORT = 8883


def main(**kwargs):
    """
    Main routine.
    """

    clientid = kwargs.get("clientid", getenv("MQTTCLIENTID", ""))
    region = kwargs.get("region", "eu")
    outfile = kwargs.get("outfile", "spartnmqtt.log")

    with open(outfile, "wb") as out:
        gmc = GNSSMQTTClient()

        print(f"SPARTN MQTT Client started, writing output to {outfile}...")
        gmc.start(
            server=SERVER,
            port=PORT,
            clientid=clientid,
            tlscrt=path.join(Path.home(), f"device-{clientid}-pp-cert.crt"),
            tlskey=path.join(Path.home(), f"device-{clientid}-pp-key.pem"),
            region=region,
            mode=0,
            topic_ip=1,
            topic_mga=0,
            topic_key=0,
            output=out,  # comment out this line to output to terminal
        )

        try:
            while True:
                sleep(3)
        except KeyboardInterrupt:
            print("SPARTN MQTT Client terminated by User")
            print(
                f"The spartn_decrypt.py example can be used to decrypt and parse the contents of the output file {outfile}:\n",
                f"python3 spartn_decrypt.py infile=spartnmqtt.log key='<== your decryption key ===>' basedate={date2timetag(datetime.now(timezone.utc))}",
            )


if __name__ == "__main__":

    main(**dict(arg.split("=") for arg in argv[1:]))
