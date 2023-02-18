"""
Skeleton SPARTNMessage class.

TODO WORK IN PROGRESS

The SPARTNMessage class does not currently perform a full decode
of SPARTN protocol messages or decrypt encyrpted payloads; it
basically decodes just enough information to identify message
type/subtype, payload length and other key metadata.

If anyone wants to contribute a full SPARTN message decode, be my guest :-)

Created on 10 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name too-many-instance-attributes


from pyspartn.exceptions import SPARTNMessageError, SPARTNParseError, SPARTNTypeError
from pyspartn.spartnhelpers import bitsval, valid_crc
from pyspartn.spartntypes_core import (
    SPARTN_PRE,
    SPARTN_MSGIDS,
    SPARTN_DATA_FIELDS,
    VALCRC,
)
from pyspartn.spartntypes_get import SPARTN_PAYLOADS_GET


class SPARTNMessage:
    """
    SPARTNMessage class.
    """

    def __init__(self, **kwargs):
        """
        Constructor.
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
        self._payload = self._transport[int(pos / 8) : int(pos / 8) + self.nData]

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

        # descrypt payload if encrypted
        if self.eaf:
            self._payload = self._decrypt_payload()

        key = ""
        try:
            pdict = (
                self._get_dict()
            )  # get payload definition dict for this message identity
            if pdict is None:  # unknown (or not yet implemented) message identity
                self._do_unknown()
                return
            for key in pdict:  # process each attribute in dict
                pass  # TODO can't do this until encryption sorted
                # (offset, index) = self._set_attribute(offset, pdict, key, index)

        except Exception as err:
            raise SPARTNTypeError(
                (
                    f"Error processing attribute '{key}' "
                    f"in message type {self.identity}"
                )
            ) from err

    def _decrypt_payload(self):
        """
        Decrypt encrypted payload.

        TODO  IF EAF IS SET, NEED TO DECRYPT PAYLOAD FIRST
        """

        # get keys from somewhere

        # where's Alan Turing when you need him?
        return self._payload

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
        if not self._scaling:
            res = 0
        val = bitsval(self._payload, offset, attlen)

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

    @property
    def payload(self) -> str:
        """
        Return message payload.
        """

        return self._payload
