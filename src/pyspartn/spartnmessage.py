"""
Skeleton SPARTNMessage class.

TODO work in progress

The MQTT key, required for payload decryption, can be passed as a keyword
or set up as environment variable MQTTKEY.

Created on 10 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

# pylint: disable=invalid-name too-many-instance-attributes

from datetime import datetime
from os import getenv

from pyspartn.exceptions import (
    ParameterError,
    SPARTNMessageError,
    SPARTNParseError,
    SPARTNTypeError,
)
from pyspartn.spartnhelpers import (
    bitsval,
    convert_timetag,
    decrypt,
    escapeall,
    timetag2date,
    valid_crc,
)
from pyspartn.spartntypes_core import (
    CBBMLEN,
    NB,
    NESTED_DEPTH,
    PBBMLEN,
    SPARTN_DATA_FIELDS,
    SPARTN_MSGIDS,
    SPARTN_PRE,
    STBMLEN,
    VALCRC,
)
from pyspartn.spartntypes_get import SPARTN_PAYLOADS_GET


class SPARTNMessage:
    """
    SPARTNMessage class.
    """

    def __init__(
        self,
        transport: bytes = None,
        validate: int = VALCRC,
        decode: bool = False,
        key: str = None,
        basedate: object = None,
        scaling: bool = False,
    ):
        """
        Constructor.

        :param bytes transport: SPARTN message transport (None)
        :param bool validate: validate CRC (True)
        :param bool decode: decrypt and decode payloads (False)
        :param str key: decryption key as hexadecimal string (None)
        :param object basedate: basedate as datetime or 32-bit gnssTimeTag as integer (now)
        :param bool scaling: apply attribute scaling factors (False)
        :raises: ParameterError if invalid parameters
        """
        # pylint: disable=too-many-arguments

        # object is mutable during initialisation only
        super().__setattr__("_immutable", False)

        self._transport = transport
        if self._transport is None:
            raise SPARTNMessageError("Transport must be provided")

        self._preamble = bitsval(self._transport, 0, 8)
        if self._preamble != SPARTN_PRE:  # not SPARTN
            raise SPARTNParseError(f"Unknown message preamble {self._preamble}")

        self._validate = validate
        self._scaling = scaling
        self._decode = decode
        basedate = datetime.now() if basedate is None else basedate
        if isinstance(basedate, int):  # 32-bit gnssTimeTag
            self._basedate = timetag2date(basedate)
        else:  # datetime
            self._basedate = basedate
        key = getenv("MQTTKEY", None) if key is None else key
        if key is None:
            self._key = None
        else:
            self._key = bytes.fromhex(key)
        self._iv = None

        if self._decode and self._key is None:
            raise ParameterError("Key must be provided if decoding is enabled")

        self._do_attributes()

        self._immutable = True  # once initialised, object is immutable

    def _do_attributes(self):
        """
        Populate SPARTNMessage attributes from transport.

        :param bytes self._transport: SPARTN message transport
        :raises: SPARTNTypeError
        """

        # start of framestart
        self.msgType = bitsval(self._transport, 8, 7)
        self.nData = bitsval(self._transport, 15, 10)
        self.eaf = bitsval(self._transport, 25, 1)
        self.crcType = bitsval(self._transport, 26, 2)
        self.frameCrc = bitsval(self._transport, 28, 4)

        # start of payDesc
        self.msgSubtype = bitsval(self._transport, 32, 4)
        self.timeTagtype = bitsval(self._transport, 36, 1)
        gln = 32 if self.timeTagtype else 16
        self.gnssTimeTag = bitsval(self._transport, 37, gln)
        pos = 37 + gln
        self.solutionId = bitsval(self._transport, pos, 7)
        self.solutionProcId = bitsval(self._transport, pos + 7, 4)
        pos += 11
        if self.eaf:  # encrypted payload
            self.encryptionId = bitsval(self._transport, pos, 4)
            self.encryptionSeq = bitsval(self._transport, pos + 4, 6)
            self.authInd = bitsval(self._transport, pos + 10, 3)
            self.embAuthLen = bitsval(self._transport, pos + 13, 3)
            pos += 16

        # start of payload
        payload = self._transport[int(pos / 8) : int(pos / 8) + self.nData]

        # start of embAuth
        pos += self.nData * 8
        aln = 0
        if hasattr(self, "authInd"):
            if self.authInd > 1:
                if self.embAuthLen == 0:
                    aln = 64
                elif self.embAuthLen == 1:
                    aln = 94
                elif self.embAuthLen == 2:
                    aln = 128
                elif self.embAuthLen == 3:
                    aln = 256
                elif self.embAuthLen == 4:
                    aln = 512
                self.embAuth = bitsval(self._transport, pos, aln)

        # start of CRC
        pos += aln
        self.crc = bitsval(self._transport, pos, (self.crcType + 1) * 8)

        # validate CRC
        core = self._transport[1 : -(self.crcType + 1)]
        if self._validate & VALCRC:
            if not valid_crc(core, self.crc, self.crcType):
                raise SPARTNMessageError(f"Invalid CRC {self.crc}")

        offset = 0  # payload offset in bits
        index = []  # array of (nested) group indices

        # ***********************************************************************************
        # TODO temporary override of decode flag for message types that cannot yet be decoded
        if self.msgType not in (0, 1, 2) or self.msgType == 0 and self.nData < 35:
            self._decode = False
        # ***********************************************************************************

        # decrypt payload if encrypted
        if self.eaf and self._decode:
            iv = self._get_iv()
            self._payload = decrypt(payload, self._key, iv)
        else:
            self._payload = payload

        key = ""
        try:
            if self._decode:
                pdict = (
                    self._get_dict()
                )  # get payload definition dict for this message identity
                if pdict is None:  # unknown (or not yet implemented) message identity
                    self._do_unknown()
                    return
                for key in pdict:  # process each attribute in dict
                    (offset, index) = self._set_attribute(offset, pdict, key, index)

        except Exception as err:
            raise SPARTNTypeError(
                (
                    f"Error processing attribute '{key}' "
                    f"in message type {self.identity}"
                )
            ) from err

    def _get_iv(self) -> bytes:
        """
        Create 128-bit Encryption Initialisation Vector.

        :return: IV as bytes
        :rtype: bytes
        """

        if self.timeTagtype:  # 32-bits
            timeTag = self.gnssTimeTag
        else:  # Convert 16-bit timetag to 32 bits
            timeTag = convert_timetag(self.gnssTimeTag, self._basedate)

        iv = (
            (self.msgType << 121)  # TF002 7 bits
            + (self.nData << 111)  # TF003 10 bits
            + (self.msgSubtype << 107)  # TF007 4 bits
            + (timeTag << 75)  # TF009 32 bits
            + (self.solutionId << 68)  # TF010 7 bits
            + (self.solutionProcId << 64)  # TF011 4 bits
            + (self.encryptionId << 60)  # TF012 4 bits
            + (self.encryptionSeq << 54)  # TF012 6 bits
            + 1  # padding to 128 bits
        )
        return iv.to_bytes(16, "big")

    def _get_attr_sfx(self, key: str, index: list) -> str:
        """
        Append nested group attribute name with appropriate indices.

        :param str key: attribute keyword e.g. SF054
        :param list index: repeating group index array e.g. [3,4]
        :return: keyname with suffix e.g. SF054_03_04
        :rtype: str
        """

        keyr = key
        keyl = NESTED_DEPTH[key]
        for i in range(keyl + 1):
            n = index[i]
            keyr += f"_{n:02d}"
        return keyr

    def _set_attribute(self, offset: int, pdict: dict, key: str, index: list) -> tuple:
        """
        Recursive routine to set individual, optional or grouped payload attributes.

        :param int offset: payload offset in bits
        :param dict pdict: dict representing payload definition
        :param str key: attribute keyword
        :param list index: repeating group index array
        :return: (offset, index[])
        :rtype: tuple
        """

        att = pdict[key]  # get attribute type
        if isinstance(att, tuple):  # attribute group
            siz, _ = att
            if isinstance(siz, tuple):  # conditional group of attributes
                (offset, index) = self._set_attribute_optional(att, offset, index)
            else:  # repeating group of attributes
                (offset, index) = self._set_attribute_group(att, offset, index)
        else:  # single attribute
            offset = self._set_attribute_single(att, offset, key, index)

        return (offset, index)

    def _set_attribute_optional(self, attg: tuple, offset: int, index: list) -> tuple:
        """
        Process optional group of attributes, subject to condition being met:
        a) group is present if attribute value = specific value, otherwise absent
        b) group is present if attribute value is in specific range, otherwise absent

        :param tuple attg: attribute group - tuple of ((attribute name, condition), group dict)
        :param int offset: payload offset in bits
        :param list index: repeating group index array
        :return: (offset, index[])
        :rtype: tuple
        """

        pres = False
        (key, con), gdict = attg  # (attribute, condition), group dictionary
        keyr = self._get_attr_sfx(key, index)
        if isinstance(con, int):  # present if attribute == value
            pres = getattr(self, keyr) == con
        elif isinstance(con, list):  # present if attribute in range of values
            pres = getattr(self, keyr) in con

        # recursively process each group attribute,
        # incrementing the payload offset as we go
        if pres:
            for key1 in gdict:
                (offset, index) = self._set_attribute(offset, gdict, key1, index)

        return (offset, index)

    def _set_attribute_group(self, attg: tuple, offset: int, index: list) -> tuple:
        """
        Process (nested) group of attributes. Group size (number of repeats)
        can be signified in a number of ways:
        a) size = fixed integer
        b) size = value of named attribute e.g. SF030
        c) size = number of bits set in named attribute e.g. SF011

        :param tuple attg: attribute group - tuple of (size, group dict)
        :param int offset: payload offset in bits
        :param list index: repeating group index array
        :return: (offset, index[])
        :rtype: tuple
        """

        index.append(0)
        key, gdict = attg  # size, group dictionary

        # if attribute is part of a (nested) repeating group, suffix name with index
        keyr = key
        for i in index:  # one index for each nested level
            if i > 0:
                keyr += f"_{i:02d}"

        # derive or retrieve number of items in group
        if isinstance(keyr, int):  # repeats = fixed integer
            rng = keyr
        elif isinstance(keyr, str):  # repeats defined in named attribute
            if keyr[0:3] == NB:  # repeats = num bits set
                rng = bin(getattr(self, keyr[3:])).count("1")
            else:
                rng = getattr(self, keyr)  # repeats = attribute value

        # recursively process each group attribute,
        # incrementing the payload offset and index as we go
        for i in range(rng):
            index[-1] = i + 1
            for key1 in gdict:
                (offset, index) = self._set_attribute(offset, gdict, key1, index)

        index.pop()  # remove this (nested) group index

        return (offset, index)

    def _set_attribute_single(
        self,
        att: object,
        offset: int,
        key: str,
        index: list,
    ) -> int:
        """
        Set individual attribute value, applying scaling where appropriate.

        :param str att: attribute type string e.g. 'INT008'
        :param int offset: payload offset in bits
        :param str key: attribute keyword
        :param list index: repeating group index array
        :return: offset
        :rtype: int
        """
        # pylint: disable=no-member

        # if attribute is part of a (nested) repeating group, suffix name with index
        keyr = key
        for i in index:  # one index for each nested level
            if i > 0:
                keyr += f"_{i:02d}"

        # get value of required number of bits at current payload offset
        # (attribute length, resolution, description)
        attlen, res, _ = SPARTN_DATA_FIELDS[key]
        if isinstance(attlen, str):  # variable length attribute
            attlen = self._getvarlen(key, index)
        if not self._scaling:
            res = 0
        try:  # TODO temporary DEBUG of payload failure
            val = bitsval(self._payload, offset, attlen)
        except SPARTNMessageError as err:
            # print(self)
            raise (err)

        setattr(self, keyr, val)

        offset += attlen

        return offset

    def _get_dict(self) -> dict:
        """
        Get payload dictionary corresponding to message identity
        (or None if message type not defined)

        :return: dictionary representing payload definition
        :rtype: dict or None
        """

        pdict = SPARTN_PAYLOADS_GET.get(self.identity, None)
        if pdict == {}:
            pdict = None
        return pdict

    def _getvarlen(self, key: str, index: list) -> int:
        """
        Get length of bitmask attribute based on
        value of preceeding bits.

        :param str keyr: name of attribute
        :param list index: nested group index
        :return: length of attribute in bits
        :rtype: int
        """
        # pylint: disable=no-member, too-many-branches

        # if within repeating group, append nested index
        if len(index) > 0:
            sfx = f"_{index[-1]:02d}"
        else:
            sfx = ""
        attl = 0
        # satellite bitmasks
        if key in ("SF011", "SF012", "SF093", "SF094", "SF095"):
            sflen = getattr(self, STBMLEN + sfx)
            if key == "SF011":  # GPS satellite mask
                attl = [32, 44, 56, 64][sflen]
            elif key == "SF012":  # GLONASS Satellite mask
                attl = [24, 36, 48, 63][sflen]
            elif key == "SF093":  # Galileo satellite mask
                attl = [36, 45, 54, 64][sflen]
            elif key == "SF094":  # BDS satellite mask
                attl = [37, 46, 55, 64][sflen]
            elif key == "SF095":  # QZSS satellite mask
                attl = [10, 40, 48, 64][sflen]
        # phase bias bitmasks
        elif key in ("SF025", "SF026", "SF102", "SF103", "SF104"):
            sflen = getattr(self, PBBMLEN + sfx)
            if key == "SF025":  # GPS phase bias mask
                attl = [6, 11][sflen]
            elif key == "SF026":  # GLONASS phase bias mask
                attl = [5, 9][sflen]
            elif key == "SF102":  # Galileo phase bias mask
                attl = [8, 15][sflen]
            elif key == "SF103":  # BDS phase bias mask
                attl = [8, 15][sflen]
            elif key == "SF104":  # QZSS phase bias mask
                attl = [6, 11][sflen]
        # code bias bitmasks
        elif key in ("SF027", "SF028", "SF105", "SF106", "SF107"):
            sflen = getattr(self, CBBMLEN + sfx)
            if key == "SF027":  # GPS code bias mask
                attl = [6, 11][sflen]
            elif key == "SF028":  # GLONASS code bias mask
                attl = [5, 9][sflen]
            elif key == "SF105":  # Galileo code bias mask
                attl = [8, 15][sflen]
            elif key == "SF106":  # BDS code bias mask
                attl = [8, 15][sflen]
            elif key == "SF107":  # QZSS code bias mask
                attl = [6, 11][sflen]
        elif key == "SF079":  # Grid node present mask
            pass  # TODO used by BPAC
        elif key == "SF088":  # Cryptographic Key,
            attl = self.SF087
        elif key == "SF092":  # Computed Authentication Data (CAD),
            attl = self.SF091

        return attl

    def _do_unknown(self):
        """
        Handle unknown message type.
        """

    def __str__(self) -> str:
        """
        Human readable representation.

        :return: human readable representation
        :rtype: str
        """

        stg = f"<SPARTN({self.identity}, "
        for i, att in enumerate(self.__dict__):
            if att[0] != "_":  # only show public attributes
                val = self.__dict__[att]
                # escape all byte characters
                if isinstance(val, bytes):
                    val = escapeall(val)
                stg += att + "=" + str(val)
                if i < len(self.__dict__) - 1:
                    stg += ", "
        if self.identity == "UNKNOWN":
            stg += ", Not_Yet_Implemented"
        stg += ")>"

        return stg

    def __repr__(self) -> str:
        """
        Machine readable representation.
        eval(repr(obj)) = obj

        :return: machine readable representation
        :rtype: str
        """

        return f"SPARTNMessage(transport={self._transport})"

    def __setattr__(self, name, value):
        """
        Override setattr to make object immutable after instantiation.

        :param str name: attribute name
        :param object value: attribute value
        :raises: SPARTNMessageError
        """

        if self._immutable:
            raise SPARTNMessageError(
                f"Object is immutable. Updates to {name} not permitted after initialisation."
            )

        super().__setattr__(name, value)

    def serialize(self) -> bytes:
        """
        Serialize message.

        :return: serialized output
        :rtype: bytes
        """

        return self._transport

    @property
    def identity(self) -> str:
        """
        Return message identity.

        :return: message identity e.g. "SPARTN_1X_OCB_GPS"
        :rtype: str
        """

        return SPARTN_MSGIDS.get((self.msgType, self.msgSubtype), "UNKNOWN")

    @property
    def payload(self) -> bytes:
        """
        Return payload.

        :return: payload
        :rtype: bytes
        """

        return self._payload
