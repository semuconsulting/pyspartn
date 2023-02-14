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

[SPARTN Protocol](https://www.spartnformat.org/download/) (available in the public domain).
© 2021 u-blox AG. All rights reserved.

The `pyspartn` homepage is located at [https://github.com/semuconsulting/pyspartn](https://github.com/semuconsulting/pyspartn).

This is an independent project and we have no affiliation whatsoever with the u-blox.

**FYI** There are companion libraries which handle standard NMEA 0183 &copy;, UBX &copy; (u-blox) and RTCM3 &copy; GNSS/GPS messages:
- [pyubx2](http://github.com/semuconsulting/pyubx2) (**FYI** installing `pyubx2` via pip also installs `pynmeagps` and `pyrtcm`)
- [pynmeagps](http://github.com/semuconsulting/pynmeagps)
- [pyrtcm](http://github.com/semuconsulting/pyrtcm)

## <a name="currentstatus">Current Status</a>

**WORK IN PROGRESS - CURRENTLY IN PRE-ALPHA.**

<!--![Status](https://img.shields.io/pypi/status/pyspartn)-->
![Release](https://img.shields.io/github/v/release/semuconsulting/pyspartn?include_prereleases)
![Build](https://img.shields.io/github/actions/workflow/status/semuconsulting/pyspartn/main.yml?branch=main)
![Codecov](https://img.shields.io/codecov/c/github/semuconsulting/pyspartn)
![Release Date](https://img.shields.io/github/release-date-pre/semuconsulting/pyspartn)
![Last Commit](https://img.shields.io/github/last-commit/semuconsulting/pyspartn)
![Contributors](https://img.shields.io/github/contributors/semuconsulting/pyspartn.svg)
![Open Issues](https://img.shields.io/github/issues-raw/semuconsulting/pyspartn)

The `SPARTNReader` class is fully functional and is capable of parsing individual SPARTN messages from a binary data stream containing *solely* SPARTN data.

The `SPARTNMessage` class does not currently perform a full decode of SPARTN protocol messages or descrypt an encrypted payload; it decodes just enough information to identify message type/subtype, payload length and other key metadata. Full decode will be added in a later release as and when voluntary development time permits - contributions welcome!

Sphinx API Documentation in HTML format is available at [https://www.semuconsulting.com/pyspartn](https://www.semuconsulting.com/pyspartn).

Contributions welcome - please refer to [CONTRIBUTING.MD](https://github.com/semuconsulting/pyspartn/blob/master/CONTRIBUTING.md).

[Bug reports](https://github.com/semuconsulting/pyspartn/blob/master/.github/ISSUE_TEMPLATE/bug_report.md) and [Feature requests](https://github.com/semuconsulting/pyspartn/blob/master/.github/ISSUE_TEMPLATE/feature_request.md) - please use the templates provided.

---
## <a name="installation">Installation</a>

`pyspartn` is compatible with Python >=3.7 and has no third-party library dependencies.

In the following, `python` & `pip` refer to the Python 3 executables. You may need to type 
`python3` or `pip3`, depending on your particular environment.

![Python version](https://img.shields.io/pypi/pyversions/pyspartn.svg?style=flat)
[![PyPI version](https://img.shields.io/pypi/v/pyspartn)](https://pypi.org/project/pyspartn/)
![PyPI downloads](https://img.shields.io/pypi/dm/pyspartn.svg?style=flat)

The recommended way to install the latest version of `pyspartn` is with
[pip](http://pypi.python.org/pypi/pip/):

```shell
python -m pip install --upgrade pyspartn
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

---
## <a name="reading">Reading (Streaming)</a>

```
class pyspartn.spartnreader.SPARTNReader(stream, **kwargs)
```

You can create a `SPARTNReader` object by calling the constructor with an active stream object. 
The stream object can be any data stream which supports a `read(n) -> bytes` method (e.g. File or Serial, with 
or without a buffer wrapper). `pyspartn` implements an internal `SocketStream` class to allow sockets to be read in the same way as other streams (see example below).

Individual SPARTN messages can then be read using the `SPARTNReader.read()` function, which returns both the raw binary data (as bytes) and the parsed data (as a `SPARTNMMessage`, via the `parse()` method). The function is thread-safe in so far as the incoming data stream object is thread-safe. `SPARTNReader` also implements an iterator.

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

Example - Socket input (using enhanced iterator):
```python
>>> import socket
>>> from pyspartn import SPARTNReader
>>> stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM):
>>> stream.connect(("localhost", 50007))
>>> spr = SPARTNReader(stream)
>>> for (raw_data, parsed_data) in spr.iterate(): print(parsed_data)
```

---
## <a name="parsing">Parsing</a>

You can parse individual SPARTN messages using the static `SPARTNReader.parse(data)` function, which takes a bytes array containing a binary SPARTN message and returns a `SPARTNMessage` object.

**NB:** Once instantiated, a `SPARTNMMessage` object is immutable.

Example:
```python
>>> from pyspartn import SPARTNReader
>>> msg = SPARTNReader.parse(b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad")
>>> print(msg)
<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11)>
```

The `SPARTNMessage` object exposes different public attributes depending on its message type or 'identity':

```python
>>> print(msg)
<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11)>
>>> msg.identity
'SPARTN-1X-OCB-GPS'
>>> msg.gnssTimeTag
3970
```

The `payload` attribute always contains the raw payload as bytes.

---
## <a name="generating">Generating</a>

```
class pyspartn.spartnmessage.SPARTNMessage(**kwargs)
```

You can create an `SPARTNMessage` object by calling the constructor with the following keyword arguments:
1. payload as bytes

Example:

```python
>>> from pyspartn import SPARTNMessage
>>> msg = SPARTNMessage(payload=b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad")
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
>>> msg = SPARTNMessage(payload=b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad")
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

1. `sparnparser.py` - illustrates how to parse SPARTN messages from a binary input file.

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