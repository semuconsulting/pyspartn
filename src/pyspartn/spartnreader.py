"""
SPARTNReader class.

The SPARTNReader class will parse individual SPARTN messages
from any binary stream containing *solely* SPARTN data e.g. an
MQTT `/pp/ip` topic.

Information sourced from https://www.spartnformat.org/download/
(available in the public domain)
© 2021 u-blox AG. All rights reserved.

SPARTN 1X transport layer bit format:

+-----------+------------+-------------+-------------+------------+-----------+
| preamble  | framestart | payload     |  payload    | embedded   |   crc     |
|           |            | descriptor  |             | auth data  |           |
+===========+============+=============+=============+============+===========+
| 8 bits    |  24 bits   | 32-64 bits  | 8-8192 bits | 0-512 bits | 8-32 bits |
| 0x73 's'  |            |             |             |            |           |
+-----------+------------+-------------+-------------+------------+-----------+

Created on 10 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

# pylint: disable=invalid-name too-many-instance-attributes

from datetime import datetime
from os import getenv
from socket import socket

from pyspartn.exceptions import (
    ParameterError,
    SPARTNMessageError,
    SPARTNParseError,
    SPARTNTypeError,
)
from pyspartn.socket_stream import SocketStream
from pyspartn.spartnhelpers import bitsval, timetag2date, valid_crc
from pyspartn.spartnmessage import SPARTNMessage
from pyspartn.spartntypes_core import ERRLOG, ERRRAISE, SPARTN_PREB, VALCRC


class SPARTNReader:
    """
    SPARTNReader class.
    """

    def __init__(
        self,
        datastream,
        validate: int = VALCRC,
        quitonerror: int = ERRLOG,
        decode: bool = False,
        key: str = None,
        basedate: object = datetime.now(),
        bufsize: int = 4096,
        errorhandler: object = None,
    ):
        """Constructor.

        :param datastream stream: input data stream
        :param int validate: 0 = ignore invalid CRC, 1 = validate CRC (1)
        :param int quitonerror: 0 = ignore,  1 = log and continue, 2 = (re)raise (1)
        :param bool decode: decrypt and decode payload (False)
        :param str key: decryption key as hexadecimal string (None)
        :param object basedate: basedate as datetime or 32-bit gnssTimeTag as integer (now)
        :param int bufsize: socket recv buffer size (4096)
        :param int errorhandler: error handling object or function (None)
        :raises: SPARTNStreamError (if mode is invalid)
        """
        # pylint: disable=too-many-arguments

        if isinstance(datastream, socket):
            self._stream = SocketStream(datastream, bufsize=bufsize)
        else:
            self._stream = datastream
        self.key = getenv("MQTTKEY", None) if key is None else key
        self._validate = validate
        self._quitonerror = quitonerror
        self._errorhandler = errorhandler
        self._decode = decode
        self._key = key
        basedate = datetime.now() if basedate is None else basedate
        if isinstance(basedate, int):  # 32-bit gnssTimeTag
            self._basedate = timetag2date(basedate)
        else:  # datetime
            self._basedate = basedate
        self._basedate = (
            datetime.now() if basedate is None else basedate
        )  # basedate for 16-bit gnssTimeTag

        if self._decode and self._key is None:
            raise ParameterError("Key must be provided if decoding is enabled")

    def __iter__(self):
        """Iterator."""

        return self

    def __next__(self) -> tuple:
        """
        Return next item in iteration.

        :return: tuple of (raw_data as bytes, parsed_data as SPARTNessage or None if error)
        :rtype: tuple
        :raises: StopIteration
        """

        (raw_data, parsed_data) = self.read()
        if raw_data is None and parsed_data is None:
            raise StopIteration
        return (raw_data, parsed_data)

    def read(self) -> tuple:
        """
        Read a single SPARTN message from the stream buffer
        and return both raw and parsed data.

        The 'quitonerror' flag determines whether to raise, log or ignore
        parsing errors. If error and quitonerror = 1, the 'parsed' value
        will contain the error message.

        :return: tuple of (raw_data as bytes, parsed_data as SPARTNMessage)
        :rtype: tuple
        :raises: SPARTNParseError if error during parsing
        """

        parsing = True
        raw_data = parsed_data = None

        while parsing:  # loop until end of valid message or EOF
            try:
                raw_data = None
                parsed_data = None
                byte1 = self._read_bytes(1)  # read the first byte
                # if not SPARTN, discard and continue
                if byte1 != SPARTN_PREB:
                    raise SPARTNParseError(f"Unknown protocol {byte1}")
                (raw_data, parsed_data) = self._parse_spartn(byte1)
                parsing = False

            except EOFError:
                return (None, None)
            except (SPARTNParseError, SPARTNMessageError, SPARTNTypeError) as err:
                if self._quitonerror:
                    self._do_error(str(err))
                parsed_data = str(err)

        return (raw_data, parsed_data)

    def _parse_spartn(self, preamble: bytes) -> tuple:
        """
        Parse any SPARTN data in the stream. The structure of the transport layer
        depends on encryption type, GNSS timetag format and CRC format.

        :param preamble hdr: preamble of SPARTN message
        :return: tuple of (raw_data as bytes, parsed_stub as SPARTNMessage)
        :rtype: tuple
        :raises: SPARTN...Error if CRC invalid or other parsing error
        """
        # pylint: disable=unused-variable

        framestart = self._read_bytes(3)
        # msgType = bitsval(framestart, 0, 7)
        nData = bitsval(framestart, 7, 10)
        eaf = bitsval(framestart, 17, 1)
        crcType = bitsval(framestart, 18, 2)
        # frameCrc = bitsval(framestart, 20, 4)

        payDesc = self._read_bytes(4)
        # msgSubtype = bitsval(payDesc, 0, 4)
        timeTagtype = bitsval(payDesc, 4, 1)
        if timeTagtype:
            payDesc += self._read_bytes(2)
        gtlen = 32 if timeTagtype else 16
        # gnssTimeTag = bitsval(payDesc, 5, gtlen)
        # solutionId = bitsval(payDesc, gtlen + 5, 7)
        # solutionProcId = bitsval(payDesc, gtlen + 12, 4)
        authInd = 0
        if eaf:
            payDesc += self._read_bytes(2)
            # encryptionId = bitsval(payDesc, gtlen + 16, 4)
            # encryptionSeq = bitsval(payDesc, gtlen + 20, 6)
            authInd = bitsval(payDesc, gtlen + 26, 3)
            embAuthLen = bitsval(payDesc, gtlen + 29, 3)
        payload = self._read_bytes(nData)
        embAuth = b""
        if authInd > 1:
            if embAuthLen == 0:
                aln = 8
            elif embAuthLen == 1:
                aln = 12
            elif embAuthLen == 2:
                aln = 16
            elif embAuthLen == 3:
                aln = 32
            elif embAuthLen == 4:
                aln = 64
            else:
                aln = 0
            embAuth = self._read_bytes(aln)
        crcb = self._read_bytes(crcType + 1)
        crc = int.from_bytes(crcb, "big")

        # validate CRC
        core = framestart + payDesc + payload + embAuth
        raw_data = preamble + core + crcb
        if self._validate & VALCRC:
            if not valid_crc(core, crc, crcType):
                raise SPARTNParseError(f"Invalid CRC {crc}")

        parsed_data = self.parse(
            raw_data,
            validate=self._validate,
            decode=self._decode,
            key=self._key,
            basedate=self._basedate,
        )
        return (raw_data, parsed_data)

    def _read_bytes(self, size: int) -> bytes:
        """
        Read a specified number of bytes from stream.

        :param int size: number of bytes to read
        :return: bytes
        :rtype: bytes
        :raises: EOFError if stream ends prematurely
        """

        data = self._stream.read(size)
        if len(data) < size:  # EOF
            raise EOFError()
        return data

    def _do_error(self, err: str):
        """
        Handle error.

        :param str err: error message
        :raises: SPARTNParseError if quitonerror = 2
        """

        if self._quitonerror == ERRRAISE:
            raise SPARTNParseError(err)
        if self._quitonerror == ERRLOG:
            # pass to error handler if there is one
            if self._errorhandler is None:
                print(err)
            else:
                self._errorhandler(err)

    @property
    def datastream(self) -> object:
        """
        Getter for stream.

        :return: data stream
        :rtype: object
        """

        return self._stream

    @staticmethod
    def parse(
        message: bytes,
        validate: int = VALCRC,
        decode: bool = False,
        key: str = None,
        basedate: object = datetime.now(),
    ) -> SPARTNMessage:
        """
        Parse SPARTN message to SPARTNMessage object.

        :param bytes message: SPARTN raw message bytes
        :param int validate: 0 = ignore invalid CRC, 1 = validate CRC (1)
        :param int decode: decode payload True/False
        :param str key: decryption key (required if decode = 1)
        :param object basedate: basedate as datetime or 32-bit gnssTimeTag as integer (now)
        :return: SPARTNMessage object
        :rtype: SPARTNMessage
        :raises: SPARTN...Error (if data stream contains invalid data or unknown message type)
        """
        # pylint: disable=unused-argument

        if decode and key is None:
            raise ParameterError("Key must be provided if decoding is enabled")

        return SPARTNMessage(
            transport=message,
            decode=decode,
            key=key,
            basedate=basedate,
            validate=validate,
        )
