"""
SPARTNMessage class.

The MQTT key, required for payload decryption, can be passed as a keyword
or set up as environment variable MQTTKEY.

Created on 10 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

# pylint: disable=invalid-name too-many-instance-attributes

from datetime import datetime, timezone
from logging import getLogger
from os import getenv

from pyspartn.exceptions import (
    ParameterError,
    SPARTNDecryptionError,
    SPARTNMessageError,
    SPARTNParseError,
)
from pyspartn.spartnhelpers import (
    HASCRYPTO,
    bitsval,
    convert_timetag,
    decrypt,
    escapeall,
    naive2aware,
    timetag2date,
    valid_crc,
)
from pyspartn.spartntables import (
    CBBITMASKKEY,
    CBBITMASKLEN,
    PBBITMASKKEY,
    PBBITMASKLEN,
    SATBITMASKKEY,
    SATBITMASKLEN,
    SF087_ENUM,
)
from pyspartn.spartntypes_core import (
    CBBMLEN,
    CBS,
    DEFAULTKEY,
    FL,
    NA,
    NB,
    PBBMLEN,
    PBS,
    PRN,
    SPARTN_DATA_FIELDS,
    SPARTN_MSGIDS,
    SPARTN_PRE,
    STBMLEN,
    TIMEBASE,
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
        key: str = DEFAULTKEY,
        basedate: object = None,
        timetags: dict = None,
    ):
        """
        Constructor.

        :param bytes transport: SPARTN message transport (None)
        :param bool validate: validate CRC (True)
        :param bool decode: decrypt and decode payloads (False)
        :param str key: decryption key as hexadecimal string (Nominal)
        :param object basedate: decryption basedate as datetime or 32-bit gnssTimeTag as
           integer (None). If basedate = TIMEBASE, timetags argument will be used
        :param dict timetags: dict of decryption timetags in format {0: 442626332, 1: 449347321,
            2: 412947745} where key = msgSubtype (0=GPS, 1=GLO, etc) and value = gnssTimeTag (None)
        :raises: ParameterError if invalid parameters
        :raises: SPARTNDecryptionError if unable to decrypt message
            using key and basedate/timetags provided
        :raises: SPARTNMessageError if transport, payload or CRC invalid
        """
        # pylint: disable=too-many-arguments

        # object is mutable during initialisation only
        super().__setattr__("_immutable", False)

        self._logger = getLogger(__name__)
        self._transport = transport
        if self._transport is None:
            raise SPARTNMessageError("Transport must be provided")

        self._preamble = bitsval(self._transport, 0, 8)
        if self._preamble != SPARTN_PRE:  # not SPARTN
            raise SPARTNParseError(f"Unknown message preamble {self._preamble}")

        self._validate = validate
        self._decode = decode
        self._padding = 0
        self._timetags = {} if timetags is None else timetags
        self._prnmap = []  # maps group index to satellite PRN
        self._pbsmap = []  # maps group index to phase bias type
        self._cbsmap = []  # maps group index to code bias type
        if basedate is None:
            self._basedate = datetime.now(timezone.utc)
        else:
            if isinstance(basedate, int):  # 32-bit gnssTimeTag
                self._basedate = timetag2date(basedate)
            else:  # datetime
                self._basedate = naive2aware(basedate)

        key = getenv("MQTTKEY", None) if key is None else key
        self._key = None if key is None else bytes.fromhex(key)
        self._iv = None

        self._do_attributes()
        self._immutable = True  # once initialised, object is immutable

    def _do_attributes(self):
        """
        Populate SPARTNMessage attributes from transport.

        :param bytes self._transport: SPARTN message transport
        :raises: SPARTNMessageError, SPARTNDecryptionError
        """

        # start of framestart
        self.msgType = bitsval(self._transport, 8, 7)
        self.nData = bitsval(self._transport, 15, 10)
        self.eaf = bitsval(self._transport, 25, 1)  # 1 = encrypted
        self.crcType = bitsval(self._transport, 26, 2)
        self.frameCrc = bitsval(self._transport, 28, 4)

        # check if decryption available
        if self._decode and self.eaf:
            if self._key is None:
                raise ParameterError("Key must be provided if decryption is enabled")
            if not HASCRYPTO:
                raise ParameterError(
                    "Decryption not available - cryptography library is not installed"
                )

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

        # decrypt payload if encrypted
        if self.eaf and self._decode:
            iv = self._get_iv()
            self._payload = decrypt(payload, self._key, iv)
        else:
            self._payload = payload

        anam = ""
        try:
            if self._decode:
                self._paylenb = len(self._payload) * 8  # payload length in bits
                self._payloadi = int.from_bytes(self._payload, "big")  # payload as int
                pdict = (
                    self._get_dict()
                )  # get payload definition dict for this message identity
                if pdict is None:  # unknown (or not yet implemented) message identity
                    self._do_unknown()
                    return
                for anam in pdict:  # process each attribute in dict
                    (offset, index) = self._set_attribute(anam, pdict, offset, index)
                self._padding = self.nData * 8 - offset  # byte alignment padding
                if not 0 <= self._padding <= 8:
                    raise SPARTNDecryptionError()
        except Exception as err:
            raise SPARTNDecryptionError(
                (
                    f"Message type {self.identity} timetag {self.gnssTimeTag} not "
                    "successfully decrypted - check key and basedate"
                )
            ) from err

    def _get_iv(self) -> bytes:
        """
        Create 128-bit Encryption Initialisation Vector.

        NB: this requires a valid 32-bit timeTag value, which
        can either be:
        - a 32-bit gnssTimeTag from the message header.
        - a 16-bit gnssTimeTag from the message header,
          converted to 32-bit using an externally-supplied basedate.
        - a 32-bit gnssTimeTag value from a previous message of the
          same subtype in the same datastream (where available).

        :return: IV as bytes
        :rtype: bytes
        """

        if self.timeTagtype:  # 32-bit timetag
            timeTag = self.gnssTimeTag
        else:
            if self._basedate == TIMEBASE:  # use 32-bit timetag from data stream
                basedate = timetag2date(self._timetags.get(self.msgSubtype, 0))
            else:  # convert 16-bit timetag to 32-bit
                basedate = self._basedate
            timeTag = convert_timetag(self.gnssTimeTag, basedate)
        iv = (
            (self.msgType << 121)  # TF002 7 bits
            + (self.nData << 111)  # TF003 10 bits
            + (self.msgSubtype << 107)  # TF007 4 bits
            + (timeTag << 75)  # TF009 32 bits
            + (self.solutionId << 68)  # TF010 7 bits
            + (self.solutionProcId << 64)  # TF011 4 bits
            + (self.encryptionId << 60)  # TF012 4 bits
            + (self.encryptionSeq << 54)  # TF013 6 bits
            + 1  # padding to 128 bits
        )
        return iv.to_bytes(16, "big")

    def _set_attribute(self, anam: str, pdict: dict, offset: int, index: list) -> tuple:
        """
        Recursive routine to set individual, optional or grouped payload attributes.

        :param str anam: attribute name
        :param dict pdict: dict representing payload definition
        :param int offset: payload offset in bits
        :param list index: repeating group index array
        :return: (offset, index[])
        :rtype: tuple
        """

        adef = pdict[anam]  # get attribute definition
        if isinstance(adef, tuple):  # attribute group
            gsiz, _ = adef
            if isinstance(gsiz, tuple):  # conditional group of attributes
                (offset, index) = self._set_attribute_optional(adef, offset, index)
            else:  # repeating group of attributes
                (offset, index) = self._set_attribute_group(adef, offset, index)
        else:  # single attribute
            offset = self._set_attribute_single(anam, offset, index)

        return (offset, index)

    def _set_attribute_optional(self, adef: tuple, offset: int, index: list) -> tuple:
        """
        Process optional group of attributes, subject to condition being met:
        a) group is present if attribute value = specific value, otherwise absent
        b) group is present if attribute value is in specific range, otherwise absent

        :param tuple adef: attribute definition - tuple of ((attribute name, condition), group dict)
        :param int offset: payload offset in bits
        :param list index: repeating group index array
        :return: (offset, index[])
        :rtype: tuple
        """

        pres = False
        (anam, con), gdict = adef  # (attribute, condition), group dictionary
        # "+n" suffix signifies that one or more nested group indices
        # must be appended to name e.g. "DF379_01", "IDF023_03"
        if "+" in anam:
            anam, nestlevel = anam.split("+")
            for i in range(int(nestlevel)):
                anam += f"_{index[i]:02d}"
        if isinstance(con, int):  # present if attribute == value
            pres = getattr(self, anam) == con
        elif isinstance(con, list):  # present if attribute in range of values
            pres = getattr(self, anam) in con

        if pres:  # if the conditional element is present...
            # recursively process each group attribute,
            # incrementing the payload offset as we go
            for anami in gdict:
                (offset, index) = self._set_attribute(anami, gdict, offset, index)

        return (offset, index)

    def _set_attribute_group(self, adef: tuple, offset: int, index: list) -> tuple:
        """
        Process (nested) group of attributes. Group size (number of repeats)
        can be signified in a number of ways:
        a) size = fixed integer
        b) size = value of named attribute e.g. SF030
        c) size = number of bits set in named attribute e.g. SF011

        :param tuple adef: attribute definition - tuple of (attribute name, group dict)
        :param int offset: payload offset in bits
        :param list index: repeating group index array
        :return: (offset, index[])
        :rtype: tuple
        """

        index.append(0)
        anam, gdict = adef  # attribute signifying group size, group dictionary

        # derive or retrieve number of items in group
        if isinstance(anam, int):  # repeats = fixed integer
            gsiz = anam
        elif isinstance(anam, str):  # repeats defined in named attribute
            # "+n" suffix signifies that one or more nested group indices
            # must be appended to name e.g. "DF379_01", "IDF023_03"
            if "+" in anam:
                anam, nestlevel = anam.split("+")
                for i in range(int(nestlevel)):
                    anam += f"_{index[i]:02d}"
            if anam[0:3] == NB:  # repeats = num bits set
                gsiz = bin(getattr(self, anam[3:])).count("1")
            else:
                gsiz = getattr(self, anam)  # repeats = attribute value
                if anam in ("SF030", "SF071"):
                    gsiz += 1

        # recursively process each group attribute,
        # incrementing the payload offset and index as we go
        for i in range(gsiz):
            index[-1] = i + 1
            for anamg in gdict:
                (offset, index) = self._set_attribute(anamg, gdict, offset, index)

        index.pop()  # remove this (nested) group index

        return (offset, index)

    def _set_attribute_single(
        self,
        anam: str,
        offset: int,
        index: list,
    ) -> int:
        """
        Set individual attribute value.

        :param str anam: attribute keyword
        :param int offset: payload offset in bits
        :param list index: repeating group index array
        :return: offset
        :rtype: int
        """

        # if attribute is part of a (nested) repeating group, suffix name with index
        anami = anam
        for i in index:  # one index for each nested level
            if i > 0:
                anami += f"_{i:02d}"

        # get value of required number of bits at current payload offset
        # (attribute length, resolution, minimum, description)
        attinfo = SPARTN_DATA_FIELDS[anam]
        atttyp = attinfo[0]  # IN, EN, BM, FL
        attlen = attinfo[1]
        if isinstance(attlen, str):  # variable length attribute
            attlen = self._getvarlen(anam, index)
        try:
            if atttyp == PRN:
                val = self._prnmap[index[-1] - 1]
            elif atttyp == PBS:
                val = self._pbsmap[index[-1] - 1]
            elif atttyp == CBS:
                val = self._cbsmap[index[-1] - 1]
            else:
                # inline for performance...
                # fmt: off
                val = self._payloadi >> (self._paylenb - offset - attlen) & ((1 << attlen) - 1)
                # fmt: on
            if atttyp == FL:
                if len(attinfo) == 6:
                    val = (
                        (val * attinfo[2]) + attinfo[3] + attinfo[4]
                    )  # (val * res) + rngmin + offset
                else:
                    val = (val * attinfo[2]) + attinfo[3]  # (val * res) + rngmin

        except SPARTNMessageError as err:
            raise err

        setattr(self, anami, val)

        offset += attlen

        # if attribute represents bitmask, populate
        # corresponding map table
        if anam in SATBITMASKKEY.values():
            self._prnmap = self._getbitmask(
                index, STBMLEN, SATBITMASKKEY, SATBITMASKLEN
            )  # satellite PRN
        elif anam in PBBITMASKKEY.values():
            self._pbsmap = self._getbitmask(
                index, PBBMLEN, PBBITMASKKEY, PBBITMASKLEN
            )  # phase bias type
        elif anam in CBBITMASKKEY.values():
            self._cbsmap = self._getbitmask(
                index, CBBMLEN, CBBITMASKKEY, CBBITMASKLEN
            )  # code bias type

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

        # pylint: disable=no-member

        # if within repeating group, append nested index
        if len(index) > 0:
            sfx = f"_{index[-1]:02d}"
        else:
            sfx = ""
        attl = 0
        if key in SATBITMASKKEY.values():  # satellite bitmasks
            attl = SATBITMASKLEN[key][getattr(self, STBMLEN + sfx)]
        elif key in PBBITMASKKEY.values():  # phase bias bitmasks
            attl = PBBITMASKLEN[key][getattr(self, PBBMLEN + sfx)][0]
        elif key in CBBITMASKKEY.values():  # code bias bitmasks
            attl = CBBITMASKLEN[key][getattr(self, CBBMLEN + sfx)][0]
        elif key == "SF079":  # Grid node present mask
            attl = (getattr(self, f"SF075{sfx}") + 1) * (
                getattr(self, f"SF076{sfx}") + 1
            )
        elif key == "SF088":  # Cryptographic Key length
            attl = SF087_ENUM[self.SF087]
        elif key == "SF092":  # Computed Authentication Data (CAD)
            attl = self.SF091

        return attl

    def _getbitmask(self, index: list, bmlen: str, bmkeys: list, bmvals: list) -> list:
        """
        Map bitmask to values in repeating groups of satellite prn, phase bias
        and code bias.

        :param str index: group index
        :param str bmlen: name of attribute containing bitmask length
        :param list bmkeys: list of bitmask attribute names for each gnss
        :param list bmvals: list of bitmask lengths and values
        :return: list of values
        :rtype: list
        """

        mode = PRN if bmlen == STBMLEN else PBS
        bm = bmkeys[self.identity[-3:]]  # bitmask name for this gnss
        if mode == PRN and "OCB" in self.identity:
            # OCB PRN bitmasks are at root level
            idx = ""
        else:
            # HPAC PRN and OCB phase/code bias bitmasks are nested one level deep
            idx = f"_{index[0]:02d}"
        bmi = bm + idx  # name of attribute containing bitmask
        bml = bmlen + idx  # name of attribute containing bitmask length

        bmval = getattr(self, bmi)  # value of bitmask
        if mode == PRN:
            bmlval = bmvals[bm][getattr(self, bml)]  # length of bitmask
        else:
            bmlval = bmvals[bm][0][getattr(self, bml)]  # length of bitmask
        vals = []
        for i in range(bmlval):  # check set bits from left to right
            if bmval >> (bmlval - 1 - i) & 1:
                if mode == PRN:
                    val = i + 1
                else:
                    val = bmvals[bm][1].get(i, NA)
                vals.append(val)
        # print(f"\nDEBUG phase bias map = {bmval:0{bmlval}b} {vals}\n")
        return vals

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
        stg = stg.strip(" ,") + ")>"

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
