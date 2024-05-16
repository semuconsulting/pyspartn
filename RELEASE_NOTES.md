# pyspartn Release Notes

### RELEASE 1.0.0

ENHANCEMENTS:

1. Add payload attributes for PRN, Phase Bias and Code Bias values, derived from the corresponding bitmasks for each constellation type. e.g. `PRN_01=3`, `PhaseBias_01_03=L2L`, `CodeBias_02_03=C2L`.
1. Add examples `parse_ocb.py` & `parse_hpac.py` illustrating how to convert parsed and decoded OCB and HPAC messages into iterable data structures.
1. Add `naive2aware(dt,tz)` helper method - convert naive basedates to aware with UTC timezone.
1. Internal enhancements to simplify basedate handling.

### RELEASE 0.4.0-beta

FIXES:

1. Fix `TypeError: can't subtract offset-naive and offset-aware datetimes` error when using default basedates. Basedates must always contain timezone information.
1. Use `timezone.utc` rather than `datetime.UTC` for compatibility with older Python versions.

### RELEASE 0.3.3-beta

ENHANCEMENTS:

1. Improved handling of half-day rollovers - thanks to @jonathanmuller for contribution.
1. Update SPARTN-1X-BPAC and SPARTN-1X-EAS-DYN handling (not tested).

### RELEASE 0.3.2-beta

ENHANCEMENTS:

1. attributes are now converted to type automatically e.g. float attributes will automatically be converted to floats via the `enc2float()` helper method using the documented resolution and range minimum values.
1. SPARTNReader will now store any 32-bit gnssTimeTags for each msgSubtype (GPS, GLO, GAL, etc.) from the incoming datastream for use as 'basedates' in the decryption of any encrypted messages with ambiguous 16-bit gnssTimetags (timeTagtype = 0). If no 32-bit gnssTimeTags are available for a given msgSubtype, the input argument 'basedate' will be used instead, adjusted for any UTC & leap second shift for that msgSubtype (e.g. GLONASS basedate = GPS + 3600*3-18).
1. Update test cases.
1. Other minor internal streamlining.

FIXES:

1. Fix `datadesc()` helper method with certain attribute names e.g. `SF049a`.

### RELEASE 0.3.1-beta

FIXES:

1. Fix Area count iterations - attribute SF030 represents (area count - 1). Affects GAD and HPAC payloads.

ENHANCEMENTS:

1. Add `SPARTNMessage._padding` attribute to allow informal checking of decryption (`0 <= msg._padding <= 8`).
1. Examples updated.

### RELEASE 0.3.0-beta

ENHANCEMENTS:

1. Streamline and simplify conditional group parsing.

FIXES:

1. Fix OCB IODE payload definition =- thanks to @jonathanmuller for contribution.

### RELEASE 0.2.1-alpha

FIXES:

1. Fix "no authInd attribute" error when parsing PointPerfect NTRIP SPARTN datastreams.

### RELEASE 0.2.0-alpha

FIXES:

1. OCB payload definitions and decoding updated.
1. pyspartn can now successfully decode all GAD and HPAC payloads and the majority of OCB payloads (*though further testing is required to validate decoded payload content*), but some small OCB payloads (`nData` < 35 bytes) cannot yet be successfully decoded. For the time being, a temporary override has been implemented in `spartnmessage.py` to suppress the `decode` flag for those payload types that cannot yet be successfully decoded. This will be removed once testing is completed.

### RELEASE 0.1.10-alpha

ENHANCEMENTS:

1. Add helper methods `timetag2date` and `date2timetag`.
1. Allow basedate decryption parameter to be passed as either datetime or an integer representing a 32-bit gnssTimeTag. See [/examples/gad_plot.py](https://github.com/semuconsulting/pyspartn/blob/main/examples/gad_plot.py) for usage.

CHANGES:

1. Update constructor arguments and docstrings to clarify API (no functional changes).

### RELEASE 0.1.9-alpha

ENHANCEMENTS:

1. Add `enc2float` helper method to convert SPARTN encoded floating point values to floats.

CHANGES:

1. Add temporary override of decode flag for message types that cannot yet be properly decoded (e.g. OCB)
1. Add `gad_plot.py` example to illustrate how to extract geographic area definitions from SPARTN-1X-GAD messages.

### RELEASE 0.1.8-alpha

FIXES:

1. `convert_timetag` routine updated - should now correctly convert 16-bit timetag to 32-bit for a given 'basedate'.
2. `basedate` keyword added to read and parse routines. Defaults to `datetime.now()`. This argument must be provided in order to decrypt messages where timeTagType = 0 (ambiguous 16-bit gnssTimeTag format), which typically includes GAD and some OCB message types but *not* HPAC message types.
3. As a result of the changes above, `pyspartn` can now successfully decode HPAC and GAD messages, but issues remain with decoding OCB payloads.

### RELEASE 0.1.7-alpha

CHANGES:

1. Remove Python 3.7 from workflows and documentation.

### RELEASE 0.1.6-alpha

CHANGES:

1. Further work on Alpha parsing and decoding functions.

### RELEASE 0.1.5-alpha

CHANGES:

1. Further work on Alpha parsing and decoding functions.

### RELEASE 0.1.4-alpha

CHANGES:

1. Further work on Alpha parsing and decoding functions. Code now includes complete field and payload definitions and provisional parsing and decryption (AES-CTR) routines for OCB, HPAC and GAD SPARTN message types.

2. NB: Message decrypt and decode not yet fully tested.

3. **NB:** Decryption of SPARTN payloads requires a 128-bit AES Initialisation Vector (IV) derived from various fields in the message's transport layer. This in turn requires a `gnssTimeTag` value in 32-bit format (representing total seconds from the SPARTN time origin of 2010-01-01 00:00:00). If `timeTagtype = 1`, this can be derived directly from the message's transport layer. If `timeTagtype = 0`, however, it is necessary to convert an ambiguous 16-bit (half-days) timetag to 32-bit format. The SPARTN 2.01 protocol specification provides *no details* on how to do this, but it appears to be necessary to use the 32-bit timetag or GPS Timestamp from an external concurrent SPARTN or UBX message from the same data source and stream. In other words, it appears SPARTN messages with `timeTagtype = 0` *cannot* be reliably decrypted in isolation.

See https://portal.u-blox.com/s/question/0D52p0000CimfsOCQQ/spartn-initialization-vector-iv-details for discussion.

### RELEASE 0.1.3-alpha

1. Byte attributes in parsed messages will be fully escaped e.g. b'/x61/x62/x63' rather than b'abc'

### RELEASE 0.1.2-alpha

1. Add CRC checking

### RELEASE 0.1.1-alpha

1. Enhance parsing

### RELEASE 0.1.0-alpha

1. Initial release
