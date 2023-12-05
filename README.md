# pyspartn

[Current Status](#currentstatus) |
[Installation](#installation) |
[Reading](#reading) |
[Parsing](#parsing) |
[Generating](#generating) |
[Serializing](#serializing) |
[Examples](#examples) |
[Graphical Client](#gui) |
[Author & License](#author)

`pyspartn` is an original Python 3 parser for the SPARTN &copy; GPS/GNSS protocol. SPARTN is an open-source GPS/GNSS [differential correction or DGPS](https://en.wikipedia.org/wiki/Differential_GPS) protocol published by u-blox.

[SPARTN Protocol 2.01](https://www.spartnformat.org/download/) (available in the public domain).
© 2021 u-blox AG. All rights reserved.

The `pyspartn` homepage is located at [https://github.com/semuconsulting/pyspartn](https://github.com/semuconsulting/pyspartn).

This is an independent project and we have no affiliation whatsoever with u-blox.

**FYI** There are companion libraries which handle standard NMEA 0183 &copy;, UBX &copy; (u-blox) and RTCM3 &copy; GNSS/GPS messages:
- [pyubx2](http://github.com/semuconsulting/pyubx2) (**FYI** installing `pyubx2` via pip also installs `pynmeagps` and `pyrtcm`)
- [pynmeagps](http://github.com/semuconsulting/pynmeagps)
- [pyrtcm](http://github.com/semuconsulting/pyrtcm)

## <a name="currentstatus">Current Status</a>

**WORK IN PROGRESS - CURRENTLY IN ALPHA.**

<!--![Status](https://img.shields.io/pypi/status/pyspartn)-->
![Release](https://img.shields.io/github/v/release/semuconsulting/pyspartn?include_prereleases)
![Build](https://img.shields.io/github/actions/workflow/status/semuconsulting/pyspartn/main.yml?branch=main)
![Codecov](https://img.shields.io/codecov/c/github/semuconsulting/pyspartn)
![Release Date](https://img.shields.io/github/release-date-pre/semuconsulting/pyspartn)
![Last Commit](https://img.shields.io/github/last-commit/semuconsulting/pyspartn)
![Contributors](https://img.shields.io/github/contributors/semuconsulting/pyspartn.svg)
![Open Issues](https://img.shields.io/github/issues-raw/semuconsulting/pyspartn)

The `SPARTNReader` class is fully functional and is capable of parsing individual SPARTN transport-layer messages from a binary data stream containing *solely* SPARTN data, with their associated metadata (message type/subtype, payload length, encryption parameters, etc.).

The `SPARTNMessage` class implements a provisional decrypt and decode for OCB, HPAC and GAD message types but it has not yet been fully tested (*appears to be working OK for GAD, HPAC and most OCB payloads, but some small OCB payloads (nData < 35) are still failing. For the time being, a temporary override has been implemented in `spartnmessage.py` to suppress the `decode` flag for those payload types that cannot yet be successfully decoded*).

Sphinx API Documentation in HTML format is available at [https://www.semuconsulting.com/pyspartn](https://www.semuconsulting.com/pyspartn).

Contributions welcome - please refer to [CONTRIBUTING.MD](https://github.com/semuconsulting/pyspartn/blob/master/CONTRIBUTING.md).

[Bug reports](https://github.com/semuconsulting/pyspartn/blob/master/.github/ISSUE_TEMPLATE/bug_report.md) and [Feature requests](https://github.com/semuconsulting/pyspartn/blob/master/.github/ISSUE_TEMPLATE/feature_request.md) - please use the templates provided.

---
## <a name="installation">Installation</a>

`pyspartn` is compatible with Python >=3.8 and is dependent on the `cryptography` library.

**NB:** If you're installing `pyspartn` on a 32-bit Linux platform, some additional installation steps may be required - see note *¹* below.

In the following, `python3` & `pip` refer to the Python 3 executables. You may need to type 
`python` or `pip3`, depending on your particular environment.

![Python version](https://img.shields.io/pypi/pyversions/pyspartn.svg?style=flat)
[![PyPI version](https://img.shields.io/pypi/v/pyspartn)](https://pypi.org/project/pyspartn/)
![PyPI downloads](https://img.shields.io/pypi/dm/pyspartn.svg?style=flat)

The recommended way to install the latest version of `pyspartn` is with
[pip](http://pypi.python.org/pypi/pip/):

```shell
python3 -m pip install --upgrade pyspartn
```

If required, `pyspartn` can also be installed into a virtual environment, e.g.:

```shell
python3 -m pip install --user --upgrade virtualenv
python3 -m virtualenv env
source env/bin/activate (or env\Scripts\activate on Windows)
(env) python3 -m pip install --upgrade pyspartn
...
deactivate
```

*¹* On some 32-bit Linux platforms (e.g. Raspberry Pi OS 32), it may be necessary to [install Rust compiler support](https://www.rust-lang.org/tools/install) in order to install the `cryptography` library which `pyspartn` depends on to decrypt SPARTN messages (see [Discussion](https://github.com/semuconsulting/PyGPSClient/discussions/83#discussioncomment-6635558)):

See [cryptography install README](https://github.com/semuconsulting/pyspartn/blob/main/cryptography_installation/README.md).


For [Conda](https://docs.conda.io/en/latest/) users, `pyspartn` is also available from [conda-forge](https://github.com/conda-forge/pyspartn-feedstock):

[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyspartn/badges/version.svg)](https://anaconda.org/conda-forge/pyspartn)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/pyspartn/badges/downloads.svg)](https://anaconda.org/conda-forge/pyspartn)

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
or without a buffer wrapper). `pyspartn` implements an internal `SocketStream` class to allow sockets to be read in the same way as other streams (see example below).

Individual SPARTN messages can then be read using the `SPARTNReader.read()` function, which returns both the raw binary data (as bytes) and the parsed data (as a `SPARTNMessage`, via the `parse()` method). The function is thread-safe in so far as the incoming data stream object is thread-safe. `SPARTNReader` also implements an iterator.

Example -  Serial input:
```python
>>> from serial import Serial
>>> from pyspartn import SPARTNReader
>>> stream = Serial('/dev/tty.usbmodem14101', 9600, timeout=3)
>>>spr = SPARTNReader(stream)
>>> (raw_data, parsed_data) = spr.read()
>>> print(parsed_data)

```

Example - File input (using iterator).
```python
>>> from pyspartn import SPARTNReader
>>> stream = open('spartndata.log', 'rb')
>>> spr = SPARTNReader(stream)
>>> for (raw_data, parsed_data) in spr: print(parsed_data)
...
```

Example - Socket input (using iterator):
```python
>>> import socket
>>> from pyspartn import SPARTNReader
>>> stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM):
>>> stream.connect(("localhost", 50007))
>>> spr = SPARTNReader(stream)
>>> for (raw_data, parsed_data) in spr: print(parsed_data)
```

---
## <a name="parsing">Parsing</a>

You can parse individual SPARTN messages using the static `SPARTNReader.parse(data)` function, which takes a bytes array containing a binary SPARTN message and returns a `SPARTNMessage` object. The optional `decode` keyword argument signifies whether to decrypt and decode the full payload (default = `False`). If `decode` is set to `True` and the message is encrypted (`eaf=1`), you *must* provide the following arguments:
- `key` - the SPARTN decryption key valid at the time the message was originally created, as provided by your SPARTN service (normally 32 hexadecimal characters). 
- `basedate` - a nominal datetime or 32-bit gnssTimeTag value, needed to convert an ambiguous 16-bit gnssTimeTag value to its unambiguous 32-bit equivalent. This is used by the decryption routine to determine the cryptographic Initialisation Vector (IV). If you're parsing messages in real time, this can default to `datetime.now()`. If you're parsing data from an older message stream, you will need to use the datetime the stream was originally created (*to the nearest half day*), or a 32-bit gnssTimeTag value from the same stream. See examples below.

**NB:** Once instantiated, a `SPARTNMMessage` object is immutable.

Example - without payload decryption:

```python
>>> from pyspartn import SPARTNReader
>>> msg = SPARTNReader.parse(b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad", decode=False)
>>> print(msg)
<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11)>
```

Example - with payload decryption (requires key and, for messages where timeTagtype = 0, a nominal basedate for IV calculation):

```python
>>> from pyspartn import SPARTNReader
>>> from datetime import datetime
>>> msg = SPARTNReader.parse(b'\x73\x04\x19\x62\x03\xfa\x20\x5b\x1f\xc8\x31\x0b\x03\xd3\xa4\xb1\xdb\x79\x21\xcb\x5c\x27\x12\xa7\xa8\xc2\x52\xfd\x4a\xfb\x1a\x96\x3b\x64\x2a\x4e\xcd\x86\xbb\x31\x7c\x61\xde\xf5\xdb\x3d\xa3\x2c\x65\xd5\x05\x9f\x1c\xd9\x96\x47\x3b\xca\x13\x5e\x5e\x54\x80', decode=True, key="6b30302427df05b4d98911ebff3a4d95", basedate=datetime(2023,6,27,22,3,0))
                                                                               
>>> print(msg)
<SPARTN(SPARTN-1X-GAD, msgType=2, nData=50, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=32580, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=63, authInd=1, embAuthLen=0, crc=6182016, SF005=37, SF068=1, SF069=0, SF030=7, SF031_01=32, SF032_01=1332, SF033_01=1987, SF034_01=6, SF035_01=2, SF036_01=5, SF037_01=22, SF031_02=33, SF032_02=1332, SF033_02=2033, SF034_02=6, SF035_02=3, SF036_02=5, SF037_02=16, SF031_03=34, SF032_03=1301, SF033_03=1921, SF034_03=2, SF035_03=6, SF036_03=18, SF037_03=10, SF031_04=35, SF032_04=1297, SF033_04=1987, SF034_04=3, SF035_04=3, SF036_04=12, SF037_04=22, SF031_05=36, SF032_05=1448, SF033_05=1768, SF034_05=6, SF035_05=2, SF036_05=5, SF037_05=30, SF031_06=37, SF032_06=1391, SF033_06=1745, SF034_06=4, SF035_06=7, SF036_06=7, SF037_06=10, SF031_07=38, SF032_07=1360, SF033_07=1906, SF034_07=3, SF035_07=2, SF036_07=8, SF037_07=22)>
```


The `SPARTNMessage` object exposes different public attributes depending on its message type or 'identity'. SPARTN data fields are denoted `SFnnn` - use the `datadesc()` helper method to obtain a more user-friendly text description of the data field.

```python
>>> from pyspartn import SPARTNReader, datadesc
>>> msg = SPARTNReader.parse(b'\x73\x03\x35\xec\x08\xc7\xd4\x20\x70\x5b\x1f\xc ... \x1e\xbe\x18\x43\x2d\x57\xe7\xa7', decode=True, key="00112233445566778899aabbccddeeff")
>>> print(msg)
<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, nData=619, eaf=1, crcType=2, frameCrc=12, msgSubtype=0, timeTagtype=1, gnssTimeTag=419070990, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=63, authInd=1, embAuthLen=0, crc=5760935, SF005=508, SF068=1, SF069=0, SF030=9, SF031_01=0, SF039_01=0, SF040T_01=1, SF040I_01=1, SF041_01=1, SF042_01=2, SF043_01=127, SF044_01=1, SF048_01=213, SF049a_01=257, SF049b_01=253, SF054_01=1, SatBitmaskLen_01=0, SF011_01=70263185, SF055_01_01=6, SF056_01_01=1, SF060_01_01=8944, ... SF061b_09_08=8287)>
>>> msg.identity
'SPARTN-1X-HPAC-GPS'
>>> msg.gnssTimeTag
419070990
>>> msg.SF005
508
datadesc("SF005")
'Solution issue of update (SIOU)'
```

The `payload` attribute always contains the raw payload as bytes.

---
## <a name="generating">Generating</a>

```
class pyspartn.spartnmessage.SPARTNMessage(**kwargs)
```

You can create an `SPARTNMessage` object by calling the constructor with the following keyword arguments:
1. transport as bytes

Example:

```python
>>> from pyspartn import SPARTNMessage
>>> msg = SPARTNMessage(transport=b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad")
>>> print(msg)
<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11)>
```

---
## <a name="serializing">Serializing</a>

The `SPARTNMessage` class implements a `serialize()` method to convert a `SPARTNMMessage` object to a bytes array suitable for writing to an output stream.

e.g. to create and send a `1005` message type:

```python
>>> from serial import Serial
>>> serialOut = Serial('COM7', 38400, timeout=5)
>>> from pyspartn import SPARTNMessage
>>> msg = SPARTNMessage(transport=b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad")
>>> print(msg)
<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11)>
>>> output = msg.serialize()
>>> output
b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad"
>>> serialOut.write(output)
```

---
## <a name="examples">Examples</a>

The following examples are available in the /examples folder:

1. `rxmpmp_extract_spartn.py` - ilustrates how to extract individual SPARTN messages from the accumulated UBX-RXM-PMP data output by an NEO-D9S L-band correction receiver.
1. `spartnparser.py` - illustrates how to parse SPARTN transport layer data from the binary SPARTN messages output by the example above.
1. `gad_plot.py` - illustrates how to extract geographic area definitions from a series of SPARTN-GAD-1X messages - the output file from the example above can be used as an input. This example also serves to illustrate how to decrypt SPARTN messages.

---
## <a name="gui">Graphical Client</a>

A python/tkinter graphical GPS client which supports NMEA, UBX, RTCM3 and SPARTN protocols is available at: 

[https://github.com/semuconsulting/PyGPSClient](https://github.com/semuconsulting/PyGPSClient)

---
## <a name="author">Author & License Information</a>

semuadmin@semuconsulting.com

![License](https://img.shields.io/github/license/semuconsulting/pyspartn.svg)

`pyspartn` is maintained entirely by unpaid volunteers. It receives no funding from advertising or corporate sponsorship. If you find the library useful, a small donation would be greatly appreciated!

[![Donations](https://www.paypalobjects.com/en_GB/i/btn/btn_donate_LG.gif)](https://www.paypal.com/donate/?business=UL24WUA4XHNRY&no_recurring=0&item_name=The+SEMU+GNSS+Python+libraries+are+maintained+entirely+by+unpaid+volunteers.+All+donations+are+greatly+appreciated.&currency_code=GBP)