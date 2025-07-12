# pyspartn

[Current Status](#currentstatus) |
[Installation](#installation) |
[Reading](#reading) |
[Parsing](#parsing) |
[Generating](#generating) |
[Serializing](#serializing) |
[Examples](#examples) |
[Troubleshooting](#troubleshooting) |
[Graphical Client](#gui) |
[Author & License](#author)

`pyspartn` is an original Python 3 parser for the SPARTN &copy; GPS/GNSS protocol. SPARTN is an open-source GPS/GNSS [differential correction or DGPS](https://en.wikipedia.org/wiki/Differential_GPS) protocol published by u-blox:

[SPARTN Protocol](https://www.spartnformat.org/download/) (available in the public domain).
© 2021 u-blox AG. All rights reserved.

The `pyspartn` homepage is located at [https://github.com/semuconsulting/pyspartn](https://github.com/semuconsulting/pyspartn).

This is an independent project and we have no affiliation whatsoever with u-blox.

**FYI** There are companion libraries which handle standard NMEA 0183 &copy;, UBX &copy; (u-blox) and RTCM3 &copy; GNSS/GPS messages:
- [pyubx2](http://github.com/semuconsulting/pyubx2)
- [pynmeagps](http://github.com/semuconsulting/pynmeagps)
- [pyrtcm](http://github.com/semuconsulting/pyrtcm)

## <a name="currentstatus">Current Status</a>

![Status](https://img.shields.io/pypi/status/pyspartn)
![Release](https://img.shields.io/github/v/release/semuconsulting/pyspartn?include_prereleases)
![Build](https://img.shields.io/github/actions/workflow/status/semuconsulting/pyspartn/main.yml?branch=main)
![Codecov](https://img.shields.io/codecov/c/github/semuconsulting/pyspartn)
![Release Date](https://img.shields.io/github/release-date-pre/semuconsulting/pyspartn)
![Last Commit](https://img.shields.io/github/last-commit/semuconsulting/pyspartn)
![Contributors](https://img.shields.io/github/contributors/semuconsulting/pyspartn.svg)
![Open Issues](https://img.shields.io/github/issues-raw/semuconsulting/pyspartn)

The `SPARTNReader` class is capable of parsing individual SPARTN transport-layer messages from a binary data stream containing *solely* SPARTN data, with their associated metadata (message type/subtype, payload length, encryption parameters, etc.).

The `SPARTNMessage` class implements optional decrypt and decode algorithms for individual OCB, HPAC, GAD, BPAC and EAS-DYN message types. Test coverage is currently limited by available SPARTN test data sources.

Sphinx API Documentation in HTML format is available at [https://www.semuconsulting.com/pyspartn](https://www.semuconsulting.com/pyspartn).

Contributions welcome - please refer to [CONTRIBUTING.MD](https://github.com/semuconsulting/pyspartn/blob/master/CONTRIBUTING.md).

[Bug reports](https://github.com/semuconsulting/pyspartn/blob/master/.github/ISSUE_TEMPLATE/bug_report.md) and [Feature requests](https://github.com/semuconsulting/pyspartn/blob/master/.github/ISSUE_TEMPLATE/feature_request.md) - please use the templates provided. For general queries and advice, please use the [Discussion](https://github.com/semuconsulting/pyspartn/discussions) Forum.

---
## <a name="installation">Installation</a>

![Python version](https://img.shields.io/pypi/pyversions/pyspartn.svg?style=flat)
[![PyPI version](https://img.shields.io/pypi/v/pyspartn)](https://pypi.org/project/pyspartn/)
![PyPI downloads](https://img.shields.io/pypi/dm/pyspartn.svg?style=flat)

`pyspartn` is compatible with Python 3.9 - 3.13. It utilises the Python `cryptography` package to decrypt SPARTN message payloads*¹*.

In the following, `python3` & `pip` refer to the Python 3 executables. You may need to substitute `python` for `python3`, depending on your particular environment (*on Windows it's generally `python`*). **It is strongly recommended that** the Python 3 binaries (\Scripts or /bin) and site_packages directories are included in your PATH (*most standard Python 3 installation packages will do this automatically if you select the 'Add to PATH' option during installation*).

The recommended way to install the latest version of `pyspartn` is with [pip](http://pypi.python.org/pypi/pip/):

```shell
python3 -m pip install --upgrade pyspartn
```

If required, `pyspartn` can also be installed into a virtual environment, e.g.:

```shell
python3 -m venv env
source env/bin/activate # (or env\Scripts\activate on Windows)
python3 -m pip install --upgrade pyspartn
```

**FYI** From `pyspartn` version 1.0.7 onwards, SPARTN decryption functionality is optional. To install without decryption support, use the `--no-deps` argument e.g. ```python3 -m pip install --upgrade pyspartn --no-deps```.

*¹* On some 32-bit Linux platforms (e.g. Raspberry Pi OS 32), it may be necessary to [install Rust compiler support](https://www.rust-lang.org/tools/install) in order to install the `cryptography` package which `pyspartn` depends on to decrypt SPARTN message payloads. See [cryptography install README](https://github.com/semuconsulting/pyspartn/blob/main/cryptography_installation/README.md).

For [Conda](https://docs.conda.io/en/latest/) users, `pyspartn` is also available from [conda-forge](https://github.com/conda-forge/pyspartn-feedstock):

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyspartn/badges/version.svg)](https://anaconda.org/conda-forge/pyspartn)
[![Anaconda-Server Badge](https://img.shields.io/conda/dn/conda-forge/pyspartn)](https://anaconda.org/conda-forge/pyspartn)

```shell
conda install -c conda-forge pyspartn
```

---
## <a name="reading">Reading (Streaming)</a>

```
class pyspartn.spartnreader.SPARTNReader(stream, **kwargs)
```

You can create a `SPARTNReader` object by calling the constructor with an active stream object. 
The stream object can be any data stream which supports a `read(n) -> bytes` method (e.g. File or Serial, with 
or without a buffer wrapper). `pyspartn` implements an internal `SocketWrapper` class to allow sockets to be read in the same way as other streams.

Individual SPARTN messages can then be read using the `SPARTNReader.read()` function, which returns both the raw binary data (as bytes) and the parsed data (as a `SPARTNMessage`, via the `parse()` method). The function is thread-safe in so far as the incoming data stream object is thread-safe. `SPARTNReader` also implements an iterator. See examples below.

Example -  Serial input:
```python
from serial import Serial
from pyspartn import SPARTNReader
with Serial('/dev/tty.usbmodem14101', 38400, timeout=3) as stream:
   spr = SPARTNReader(stream)
   raw_data, parsed_data = spr.read()
   if parsed_data is not None:
      print(parsed_data)
```

Example - File input (using iterator).
```python
from pyspartn import SPARTNReader
with open('spartndata.log', 'rb') as stream:
   spr = SPARTNReader(stream)
   for raw_data, parsed_data in spr:
      print(parsed_data)
```

Example - Socket input (using iterator):
```python
import socket
from pyspartn import SPARTNReader
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as stream:
   stream.connect(("localhost", 50007))
   spr = SPARTNReader(stream)
   for raw_data, parsed_data in spr:
      print(parsed_data)
```

### Encrypted Payloads

At time of writing, most proprietary SPARTN message sources (e.g. Thingstream PointPerfect © MQTT) use encrypted payloads (`eaf=1`). In order to decrypt and decode these payloads, a valid decryption `key` is required. Keys are typically 32-character hexadecimal strings valid for a 4 week period.

In addition to the key, the SPARTN decryption algorithm requires a 32-bit `gnssTimeTag` value. The provision of this 32-bit `gnssTimeTag` depends on the incoming data stream:
- Some SPARTN message types (*e.g. HPAC and a few OCB messages*) include the requisite 32-bit `gnssTimeTag` in the message header (denoted by `timeTagtype=1`). Others (*e.g. GAD and most OCB messages*) use an ambiguous 16-bit `gnssTimeTag` value for reasons of brevity (denoted by `timeTagtype=0`). In these circumstances, a nominal 'basedate' must be provided by the user, representing the UTC datetime on which the datastream was originally created to the nearest half day, in order to convert the 16-bit `gnssTimeTag` to an unambiguous 32-bit value.
- If you're parsing data in real time, this basedate can be left at the default `datetime.now(timezone.utc)`.
- If you're parsing historical data, you will need to provide a basedate representing the UTC datetime on which the data stream was originally created, to the nearest half day.
- If a nominal basedate of `TIMEBASE` (`datetime(2010, 1, 1, 0, 0, tzinfo=timezone.utc)`) is provided, `pyspartn.SPARTNReader` can *attempt* to derive the requisite `gnssTimeTag` value from any 32-bit `gnssTimetag` in a preceding message of the same subtype in the same data stream, but *unless and until this eventuality occurs (e.g. unless an HPAC message precedes an OCB message of the same subtype), decryption may fail*. Always set the `quitonerror` argument to `ERRLOG` or `ERRIGNORE` to log or ignore such initial failures.

The current decryption key can also be set via environment variable `MQTTKEY`, but bear in mind this will need updating every 4 weeks.

Example -  Real time serial input with decryption:
```python
from serial import Serial
from pyspartn import SPARTNReader
with Serial('/dev/tty.usbmodem14101', 9600, timeout=3) as stream:
   spr = SPARTNReader(stream, decode=1, key="930d847b779b126863c8b3b2766ae7cc")
   for raw_data, parsed_data in spr:
      print(parsed_data)
```

Example - Historical file input with decryption, using an known basedate:
```python
from datetime import datetime, timezone
from pyspartn import SPARTNReader

with open('spartndata.log', 'rb') as stream:
   spr = SPARTNReader(stream, decode=1, key="930d847b779b126863c8b3b2766ae7cc", basedate=datetime(2023, 4, 18, 20, 48, 29, 977255, tzinfo=timezone.utc))
   for raw_data, parsed_data in spr:
      print(parsed_data)

```

Example - Historical file input with decryption, using a nominal TIMEBASE basedate:
```python
from datetime import datetime, timezone
from pyspartn import SPARTNReader, TIMEBASE, ERRLOG

with open('spartndata.log', 'rb') as stream:
   spr = SPARTNReader(stream, decode=1, key="930d847b779b126863c8b3b2766ae7cc", basedate=TIMEBASE, quitonerror=ERRLOG)
   for raw_data, parsed_data in spr:
      print(parsed_data)

```
```
... (first few messages may fail decryption, until we find a usable 32-bit gnssTimeTag ...)
"Message type SPARTN-1X-OCB-GPS timetag 33190 not successfully decrypted - check key and basedate"
"Message type SPARTN-1X-OCB-GLO timetag 31234 not successfully decrypted - check key and basedate"
... (but the rest should be decrypted OK ...)
```

---
## <a name="parsing">Parsing</a>

You can parse individual SPARTN messages using the static `SPARTNReader.parse(data)` function, which takes a bytes array containing a binary SPARTN message and returns a `SPARTNMessage` object. If the message payload is encrypted (`eaf=1`), a decryption `key` and UTC `basedate` must be provided. See examples below.

**NB:** Once instantiated, a `SPARTNMMessage` object is immutable.

Example - without payload decryption or decoding:

```python
from pyspartn import SPARTNReader

transport = b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad"
msg = SPARTNReader.parse(transport, decode=0)
print(msg)
```
```
<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=9, authInd=1, embAuthLen=0, crc=7627181, )>
```

Example - with payload decryption and decoding (requires key and, for messages where `timeTagtype=0`, a nominal basedate):

```python
from datetime import datetime, timezone
from pyspartn import SPARTNReader

transport = b"\x73\x04\x19\x62\x03\xfa\x20\x5b\x1f\xc8\x31\x0b\x03\xd3\xa4\xb1\xdb\x79\x21\xcb\x5c\x27\x12\xa7\xa8\xc2\x52\xfd\x4a\xfb\x1a\x96\x3b\x64\x2a\x4e\xcd\x86\xbb\x31\x7c\x61\xde\xf5\xdb\x3d\xa3\x2c\x65\xd5\x05\x9f\x1c\xd9\x96\x47\x3b\xca\x13\x5e\x5e\x54\x80"
msg = SPARTNReader.parse(
    transport,
    decode=1,
    key="6b30302427df05b4d98911ebff3a4d95",
    basedate=datetime(2023, 6, 27, 22, 3, 0, tzinfo=timezone.utc),
)
print(msg)
```
```
<SPARTN(SPARTN-1X-GAD, msgType=2, nData=50, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=32580, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=63, authInd=1, embAuthLen=0, crc=6182016, SF005=37, SF068=1, SF069=0, SF030=7, SF031_01=32, SF032_01=43.20000000000002, SF033_01=18.700000000000017, SF034_01=6, SF035_01=2, SF036_01=0.6, SF037_01=2.3000000000000003, SF031_02=33, SF032_02=43.20000000000002, SF033_02=23.30000000000001, SF034_02=6, SF035_02=3, SF036_02=0.6, SF037_02=1.7000000000000002, SF031_03=34, SF032_03=40.099999999999994, SF033_03=12.100000000000023, SF034_03=2, SF035_03=6, SF036_03=1.9000000000000001, SF037_03=1.1, SF031_04=35, SF032_04=39.70000000000002, SF033_04=18.700000000000017, SF034_04=3, SF035_04=3, SF036_04=1.3000000000000003, SF037_04=2.3000000000000003, SF031_05=36, SF032_05=54.80000000000001, SF033_05=-3.1999999999999886, SF034_05=6, SF035_05=2, SF036_05=0.6, SF037_05=3.1, SF031_06=37, SF032_06=49.099999999999994, SF033_06=-5.5, SF034_06=4, SF035_06=7, SF036_06=0.8, SF037_06=1.1, SF031_07=38, SF032_07=46.0, SF033_07=10.600000000000023, SF034_07=3, SF035_07=2, SF036_07=0.9, SF037_07=2.3000000000000003, SF031_08=39, SF032_08=46.0, SF033_08=1.8000000000000114, SF034_08=7, SF035_08=2, SF036_08=0.7000000000000001, SF037_08=2.3000000000000003)>
```

The `SPARTNMessage` object exposes different public attributes depending on its message type or 'identity'. SPARTN data fields are denoted `SFnnn` - use the `datadesc()` helper method to obtain a more user-friendly text description of the data field.

```python
from datetime import datetime, timezone
from pyspartn import SPARTNReader, datadesc
msg = SPARTNReader.parse(b"s\x02\xf7\xeb\x08\xd7!\xef\x80[\x17\x88\xc2?\x0f\x ... \xc4#fFy\xb9\xd5", decode=True, key="930d847b779b126863c8b3b2766ae7cc", basedate=datetime(2024, 4, 18, 20, 48, 29, 977255, tzinfo=timezone.utc))
print(msg)
print(msg.identity)
print(msg.gnssTimeTag)
print(datadesc("SF005"), msg.SF005)
print(datadesc("SF061a"), msg.SF061a_10_05)
```
```
<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, nData=495, eaf=1, crcType=2, frameCrc=11, msgSubtype=0, timeTagtype=1, gnssTimeTag=451165680, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=30, authInd=1, embAuthLen=0, crc=7977429, SF005=152, SF068=1, SF069=0, SF030=9, SF031_01=0, SF039_01=0, SF040T_01=1, SF040I_01=1, SF041_01=1, SF042_01=1, SF043_01=0.0, SF044_01=1, SF048_01=-0.21199999999999997, SF049a_01=0.0, SF049b_01=0.0010000000000000009, SF054_01=1, SatBitmaskLen_01=0, SF011_01=880836738, SF055_01_01=1, SF056_01_01=1, SF060_01_01=-11.120000000000005, ..., SF061a_10_05=-0.27200000000000557, SF061b_10_05=0.1839999999999975, SF055_10_06=2, SF056_10_06=1, SF060_10_06=7.640000000000043, SF061a_10_06=-1.3840000000000003, SF061b_10_06=-0.7920000000000016)>
'SPARTN-1X-HPAC-GPS'
451165680
('Solution issue of update (SIOU)', 152)
('Large ionosphere coefficient C01', -0.27200000000000557)
```

Attributes in nested repeating groups are suffixed with a 2-digit index for each nested level e.g. `SF032_06`, `SF061a_10_05`. See [examples below](#iterating) for illustrations of how to iterate through grouped attributes.

Enumerations for coded values can be found in [spartntables.py](https://github.com/semuconsulting/pyspartn/blob/main/src/pyspartn/spartntables.py).

The `payload` attribute always contains the raw payload as bytes.

#### <a name="iterating">Iterating Through Group Attributes</a>

To iterate through nested grouped attributes, you can use a construct similar to the following (_this example iterates through SF032 Area reference latitude values in a SPARTN-1X-GAD message_):

```python
vals = []
for i in range(parsed_data.SF030 + 1):  # attribute or formula representing group size
    vals.append(getattr(parsed_data, f"SF032_{i+1:02d}"))
print(vals)
```

See examples `parse_ocb.py`, `parse_hpac.py` and `parse_gad.py` for illustrations of how to convert parsed and decoded OCB, HPAC and GAD payloads into iterable data structures.

---
## <a name="generating">Generating</a>

```
class pyspartn.spartnmessage.SPARTNMessage(**kwargs)
```

You can create an `SPARTNMessage` object by calling the constructor with the following keyword arguments:
1. transport as bytes

Example:

```python
from pyspartn import SPARTNMessage
msg = SPARTNMessage(transport=b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad")
print(msg)
```
```
<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=9, authInd=1, embAuthLen=0, crc=7627181, )>
```

---
## <a name="serializing">Serializing</a>

The `SPARTNMessage` class implements a `serialize()` method to convert a `SPARTNMMessage` object to a bytes array suitable for writing to an output stream.

e.g. to create and send a SPARTN-1X-OCB-GPS message type:

```python
from serial import Serial
serialOut = Serial('/dev/ttyACM1', 38400, timeout=5)
from pyspartn import SPARTNMessage
msg = SPARTNMessage(transport=b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad")
print(msg)
output = msg.serialize()
print(output)
serialOut.write(output)
```
```
<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=9, authInd=1, embAuthLen=0, crc=7627181, )>
b's\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad'
```

---
## <a name="examples">Examples</a>

The following examples are available in the /examples folder:

1. `spartnparser.py` - illustrates how to parse SPARTN transport layer data from a binary SPARTN datastream.
1. `spartn_decrypt.py` - illustrates how to decrypt and decode a binary SPARTN log file (e.g. from the `spartn_mqtt_client.py` or `spartn_ntrip_client.py` examples below).
1. `spartn_mqtt_client.py` - implements a simple SPARTN MQTT client using the [`pygnssutils.GNSSMQTTClient`](https://github.com/semuconsulting/pygnssutils?tab=readme-ov-file#gnssmqttclient) class. **NB**: requires a valid ClientID for a SPARTN MQTT service e.g. u-blox Thingstream PointPerfect MQTT.
1. `spartn_ntrip_client.py` - implements a simple SPARTN NTRIP client using the [`pygnssutils.GNSSNTRIPClient`](https://github.com/semuconsulting/pygnssutils?tab=readme-ov-file#gnssntripclient) class. **NB**: requires a valid user and password for a
SPARTN NTRIP service e.g. u-blox Thingstream PointPerfect NTRIP.
1. `rxmpmp_extract_spartn.py` - ilustrates how to extract individual SPARTN messages from the accumulated UBX-RXM-PMP data output by an NEO-D9S L-band correction receiver.
1. `parse_gad.py` - illustrates how to convert parsed GAD message types into WKT area polygon format for display on a map (see, for example, `gad_plot_map.png`).
1. `parse_hpac.py` and `parse_ocb.py` - illustrate how to convert parsed HPAC and OCB message types into iterable data structures.

---
## <a name="troubleshooting">Troubleshooting</a>

1. `SPARTNTypeError` or `SPARTNParseError` when parsing encrypted messages with 16-bit gnssTimetags (`timeTagtype=0`), e.g. GAD or some OCB messages:

   ```
   pyspartn.exceptions.SPARTNTypeError: Error processing attribute 'group' in message type SPARTN-1X-GAD
   ```

   This is almost certainly due to an invalid decryption key and/or basedate. Remember that keys are only valid for a 4 week period, and basedates are valid for no more than half a day. Note also that different GNSS constellations use different UTC datums e.g. GLONASS timestamps are based on UTC+3. Check with your SPARTN service provider for the latest decryption key(s), and check the original creation date of your SPARTN datasource.

1. `SSL: CERTIFICATE_VERIFY_FAILED` error when attempting to connect to SPARTN MQTT service using `gnssmqttclient` on MacOS:

   ```
   [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1000)
   ```

   This is because `gnssmqttclient` is unable to locate the RootCA certificate for the MQTT Broker. This can normally be resolved as follows:
   - Install the latest version of certifi: ```python3 -m pip install --upgrade certifi```
   - Run the following command from the terminal (_substituting your Python path and version as required_): ```/Applications/Python\ 3.12/Install\ Certificates.command```

1. Unable to install `crytography` library required by `pyspartn` on 32-bit Linux platforms:

   ```
   Building wheel for cryptography (PEP 517): started
   Building wheel for cryptography (PEP 517): finished with status 'error'
   ```

   Refer to [cryptography installation README.md](https://github.com/semuconsulting/pyspartn/blob/main/cryptography_installation/README.md).

1. Checking for successful decryption. `SPARTNMessage` objects implement a protected attribute `_padding`, which represents the number of redundant bits added to the payload content in order to byte-align the payload with the number of bytes specified in the transport layer payload length attribute `nData`. If the payload has been successfully decrypted and decoded, the value of `_padding` should always be between 0 and 8. Checking `0 <= msg._padding <= 8` provides an informal (_but not necessarily definitive_) check of successful decryption and decoding (see, for example, [spartn_decrypt.py](https://github.com/semuconsulting/pyspartn/blob/main/examples/spartn_decrypt.py)).

---
## <a name="gui">Graphical Client</a>

A python/tkinter graphical GPS client which supports NMEA, UBX, RTCM3 and SPARTN protocols is available at: 

[https://github.com/semuconsulting/PyGPSClient](https://github.com/semuconsulting/PyGPSClient)

---
## <a name="author">Author & License Information</a>

semuadmin@semuconsulting.com

![License](https://img.shields.io/github/license/semuconsulting/pyspartn.svg)

`pyspartn` is maintained entirely by unpaid volunteers. It receives no funding from advertising or corporate sponsorship. If you find the utility useful, please consider sponsoring the project with the price of a coffee...

[![Sponsor](https://github.com/semuconsulting/pyubx2/blob/master/images/sponsor.png?raw=true)](https://buymeacoffee.com/semuconsulting)

[![Freedom for Ukraine](https://github.com/semuadmin/sandpit/blob/main/src/sandpit/resources/ukraine200.jpg?raw=true)](https://u24.gov.ua/)
