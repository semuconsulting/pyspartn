# pyspartn Release Notes

### RELEASE 0.1.8-alpha

FIXES:

1. `spartnhelpers.convert_timetag` routine updated - should now correctly convert 16-bit timetag to 32-bit. 
2. `pyspartn` can now successfully decode HPAC and GAD messages, but issues remain with decoding OCB payloads.

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
