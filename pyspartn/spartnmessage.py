"""
Skeleton SPARTNMessage class.

TODO WORK IN PROGRESS

The SPARTNMessage class does not currently perform a full decrypt
and decode of SPARTN payloads; it decodes the transport layer to
identify message type/subtype, payload length and other key metadata.
Full payload decode will be added in due course as and when voluntary
development time permits.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
NB: Decryption of SPARTN payloads requires a 128-bit AES Initialisation
Vector (IV) derived from various fields in the message's transport layer.
This in turn requires a gnssTimeTag value in 32-bit format (representing
total seconds from the SPARTN time origin of 2010-01-01 00:00:00). If
timeTagtype = 1, this can be derived directly from the message's transport
layer. If timeTagtype = 0, however, it is necessary to convert an ambiguous
16-bit (half-days) timetag to 32-bit format. The SPARTN 2.01 protocol
specification provides no details on how to do this, but it appears to be
necessary to use the 32-bit timetag or GPS Timestamp from an external
concurrent SPARTN or UBX message from the same data source and stream.
In other words, it appears SPARTN messages with timeTagtype = 0 cannot be
reliably decrypted in isolation.

See https://portal.u-blox.com/s/question/0D52p0000CimfsOCQQ/spartn-initialization-vector-iv-details
for discussion.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

The MQTT key, required for payload decryption, can be passed as a keyword
or set up as environment variable MQTTKEY.

If anyone wants to contribute a full SPARTN message decode, be my guest :-)

Created on 10 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name too-many-instance-attributes

from os import getenv
from pyspartn.exceptions import (
    SPARTNMessageError,
    SPARTNParseError,
    SPARTNTypeError,
    ParameterError,
)
from pyspartn.spartnhelpers import (
    bitsval,
    numbitsset,
    valid_crc,
    escapeall,
    decrypt,
    convert_timetag,
    att2name,
)
from pyspartn.spartntypes_core import (
    SPARTN_PRE,
    SPARTN_MSGIDS,
    SPARTN_DATA_FIELDS,
    VALCRC,
    NSAT,
    NPHABIAS,
    NCODBIAS,
    NTROP,
    NTROP2,
    NIONO,
    NIONO2,
    NSF0440,
    NSF0441,
    NSF04112,
    NSF0412,
    NSF0510,
    NSF0511,
    NSF0560,
    NSF0561,
    NSF05412,
    NSF0542,
    NSF0630,
    NSF0631,
    NSF0632,
    NSF0633,
)
from pyspartn.spartntypes_get import SPARTN_PAYLOADS_GET


class SPARTNMessage:
    """
    SPARTNMessage class.
    """

    def __init__(self, **kwargs):
        """
        Constructor.

        :param bytes transport: (kwarg) SPARTN message transport (None)
        :param bool decrypt: (kwarg) decrypt encrypted payloads (False)
        :param str key: (kwarg) decryption key as hexadecimal string (or set env variable MQTTKEY) (None)
        :param bool validate: (kwarg) validate CRC (True)
        :param bool scaling: (kwarg) apply attribute scaling factors (True)
        :raises: ParameterError if invalid parameters
        """

        # object is mutable during initialisation only
        super().__setattr__("_immutable", False)

        self._transport = kwargs.get("transport", None)
        self._validate = int(kwargs.get("validate", VALCRC))
        if self._transport is None:
            raise SPARTNMessageError("Transport must be provided")

        self._preamble = bitsval(self._transport, 0, 8)
        if self._preamble != SPARTN_PRE:  # not SPARTN
            raise SPARTNParseError(f"Unknown message preamble {self._preamble}")

        self._scaling = kwargs.get("scaling", False)
        self._decrypt = kwargs.get("decrypt", False)
        key = kwargs.get("key", getenv("MQTTKEY", None))  # 128-bit key
        if key is None:
            self._key = None
        else:
            self._key = bytes.fromhex(key)
        self._iv = None

        if self._decrypt and self._key is None:
            raise ParameterError("Key must be provided if decryption is enabled")

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
        if self.eaf and self._decrypt:
            iv = self._get_iv()
            self.payload = decrypt(payload, self._key, iv)
        else:
            self.payload = payload

        key = ""
        try:
            pdict = (
                self._get_dict()
            )  # get payload definition dict for this message identity
            if pdict is None:  # unknown (or not yet implemented) message identity
                self._do_unknown()
                return
            for key in pdict:  # process each attribute in dict
                # TODO add payload definitions and verify decryption
                # (offset, index) = self._set_attribute(offset, pdict, key, index)
                pass

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
        else:  # Convert 16-bit timetag to 32 bits (WHY???!!!)
            timeTag = convert_timetag(self.gnssTimeTag)

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

    def _set_attribute(self, offset: int, pdict: dict, key: str, index: list) -> tuple:
        """
        Recursive routine to set individual or grouped payload attributes.

        :param int offset: payload offset in bits
        :param dict pdict: dict representing payload definition
        :param str key: attribute keyword
        :param list index: repeating group index array
        :return: (offset, index[])
        :rtype: tuple
        """

        att = pdict[key]  # get attribute type
        if isinstance(att, tuple):  # repeating group of attributes
            (offset, index) = self._set_attribute_group(att, offset, index)
        else:  # single attribute
            offset = self._set_attribute_single(att, offset, key, index)

        return (offset, index)

    def _set_attribute_group(self, att: tuple, offset: int, index: list) -> tuple:
        """
        Process (nested) group of attributes.

        :param tuple att: attribute group - tuple of (num repeats, attribute dict)
        :param int offset: payload offset in bits
        :param list index: repeating group index array
        :return: (offset, index[])
        :rtype: tuple
        """

        numr, attd = att  # number of repeats, attribute dictionary
        # derive or retrieve number of items in group
        if isinstance(numr, int):  # fixed number of repeats
            rng = numr
        else:  # number of repeats is defined in named attribute
            # if attribute is within a group
            # append group index to name e.g. "SF030"
            rng = getattr(self, numr)

        index.append(0)  # add a (nested) group index level
        # recursively process each group attribute,
        # incrementing the payload offset and index as we go
        for i in range(rng):
            index[-1] = i + 1
            for key1 in attd:
                (offset, index) = self._set_attribute(offset, attd, key1, index)

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
            attlen = self._getvarlen(key)
        if not self._scaling:
            res = 0
        val = bitsval(self.payload, offset, attlen)

        setattr(self, keyr, val)
        # set any variable length indicators based on this attribute
        self._setvarlen(keyr)

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

    def _getvarlen(self, key: str) -> int:
        """
        Get length of variable-length attribute based on
        value of preceeding length attribute.

        :param str keyr: name of attribute
        :return: length of attribute in bits
        :rtype: int
        """
        # pylint: disable=no-member

        attl = 0
        if key == "SF011":  # GPS satellite mask
            attl = [32, 44, 56, 64][self._SatMaskLen]
        elif key == "SF012":  # GLONASS Satellite mask
            attl = [24, 36, 48, 63][self._SatMaskLen]
        elif key == "SF093":  # Galileo satellite mask
            attl = [36, 45, 54, 64][self._SatMaskLen]
        elif key == "SF094":  # BDS satellite mask
            attl = [37, 46, 55, 64][self._SatMaskLen]
        elif key == "SF095":  # QZSS satellite mask
            attl = [10, 40, 48, 64][self._SatMaskLen]
        elif key == "SF025":  # GPS phase bias mask
            attl = [6, 11][self._PhaBiasMaskLen]
        elif key == "SF026":  # GLONASS phase bias mask
            attl = [5, 9][self._PhaBiasMaskLen]
        elif key == "SF102":  # Galileo phase bias mask
            attl = [8, 15][self._PhaBiasMaskLen]
        elif key == "SF103":  # BDS phase bias mask
            attl = [8, 15][self._PhaBiasMaskLen]
        elif key == "SF104":  # QZSS phase bias mask
            attl = [6, 11][self._PhaBiasMaskLen]
        elif key == "SF027":  # GPS code bias mask
            attl = [6, 11][self._CodBiasMaskLen]
        elif key == "SF028":  # GLONASS code bias mask
            attl = [5, 9][self._CodBiasMaskLen]
        elif key == "SF105":  # Galileo code bias mask
            attl = [8, 15][self._CodBiasMaskLen]
        elif key == "SF106":  # BDS code bias mask
            attl = [8, 15][self._CodBiasMaskLen]
        elif key == "SF107":  # QZSS code bias mask
            attl = [6, 11][self._CodBiasMaskLen]
        elif key == "SF079":  # Grid node present mask
            pass  # TODO used by BPAC
        elif key == "SF088":  # Cryptographic Key,
            attl = self.SF087
        elif key == "SF092":  # Computed Authentication Data (CAD),
            attl = self.SF091

        return attl

    def _setvarlen(self, keyr: str):
        """
        Set attributes representing presence and/or
        length of optional or repeating groups.

        :param str keyr: key name
        """
        # pylint: disable=no-member

        key = att2name(keyr)

        # satellite bitmasks
        if key in ("SF011", "SF012", "SF093", "SF094", "SF095"):
            setattr(self, NSAT, numbitsset(getattr(self, keyr)))
        # phase bias bitmasks
        elif key in ("SF025", "SF026", "SF102", "SF103", "SF104"):
            setattr(self, NPHABIAS, numbitsset(getattr(self, keyr)))
        # code bias bitmasks
        elif key in ("SF027", "SF028", "SF105", "SF106", "SF107"):
            setattr(self, NCODBIAS, numbitsset(getattr(self, keyr)))
        # troposphere blocks
        elif key == "SF040T":
            val = 1 if self.SF040T in (1, 2) else 0
            setattr(self, NTROP, val)
            val = 1 if self.SF040T == 2 else 0
            setattr(self, NTROP2, val)
        # ionosphere blocks
        elif key == "SF040I":
            val = 1 if self.SF040I in (1, 2) else 0
            setattr(self, NIONO, val)
            val = 1 if self.SF040I == 2 else 0
            setattr(self, NIONO2, val)
        # troposphere coefficients
        elif key == "SF044":
            setattr(self, NSF0440, not self.SF044)
            setattr(self, NSF0441, self.SF044)
        # troposphere coefficients small/large
        elif key == "SF041":
            val = 1 if self.SF044 in (1, 2) else 0
            setattr(self, NSF04112, val)
            val = 1 if self.SF044 == 2 else 0
            setattr(self, NSF0412, val)
        # troposphere residual size
        elif key == "SF051":
            setattr(self, NSF0510, not self.SF051)
            setattr(self, NSF0511, self.SF051)
        # ionosphere coefficients
        elif key == "SF056":
            setattr(self, NSF0560, not self.SF056)
            setattr(self, NSF0561, self.SF056)
        # ionosphere coefficients small/large
        elif key == "SF054":
            val = 1 if self.SF054 in (1, 2) else 0
            setattr(self, NSF05412, val)
            val = 1 if self.SF054 == 2 else 0
            setattr(self, NSF0542, val)
        # ionosphere residual size
        elif key == "SF063":
            setattr(self, NSF0630, 0)
            setattr(self, NSF0631, 0)
            setattr(self, NSF0632, 0)
            setattr(self, NSF0633, 0)
            if self.SF063 == 0:
                setattr(self, NSF0630, 1)
            elif self.SF063 == 1:
                setattr(self, NSF0631, 1)
            elif self.SF063 == 2:
                setattr(self, NSF0632, 1)
            elif self.SF063 == 3:
                setattr(self, NSF0633, 1)

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
        """

        return SPARTN_MSGIDS.get((self.msgType, self.msgSubtype), "UNKNOWN")
