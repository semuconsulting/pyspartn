"""
Skeleton SPARTNMessage class.

The SPARTNMessage class does not currently perform a full decode
of SPARTN protocol messages; it basically decodes just enough
information to identify message type/subtype, payload length and
other key metadata.

Sourced from https://www.spartnformat.org/download/
(available in the public domain)
© 2021 u-blox AG. All rights reserved.

If anyone wants to contribute a full SPARTN message decode, be my guest :-)

Created on 10 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name too-many-instance-attributes


from pyspartn.exceptions import SPARTNMessageError, SPARTNParseError
from pyspartn.spartnhelpers import bitsval
from pyspartn.spartntypes_core import SPARTN_PRE, SPARTN_MSGIDS


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

        self._payload = kwargs.get("payload", None)
        if self._payload is None:
            raise SPARTNMessageError("Payload must be provided")

        self._preamble = bitsval(self._payload, 0, 8)
        if self._preamble != SPARTN_PRE:  # not SPARTN
            raise SPARTNParseError(f"Unknown message preamble {self._preamble}")

        self.msgType = bitsval(self._payload, 8, 7)
        self.msgSubtype = bitsval(self._payload, 32, 4)
        self.nData = bitsval(self._payload, 15, 10)
        self.eaf = bitsval(self._payload, 25, 1)
        self.crcType = bitsval(self._payload, 26, 2)
        self.frameCrc = bitsval(self._payload, 28, 4)
        self.timeTagtype = bitsval(self._payload, 36, 1)
        timl = 16 if self.timeTagtype == 0 else 32
        self.gnssTimeTag = bitsval(self._payload, 37, timl)
        self.solutionId = bitsval(self._payload, 37 + timl, 7)
        self.solutionProcId = bitsval(self._payload, 44 + timl, 4)

        self._do_attributes(**kwargs)

        self._immutable = True  # once initialised, object is immutable

    def _do_attributes(self, **kwargs):
        """
        TODO this is where to do a full decode of a SPARTN message...
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

        return f"SPARTNMessage(payload={self._payload})"

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

        return self._payload

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
