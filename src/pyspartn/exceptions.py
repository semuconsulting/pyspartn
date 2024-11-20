"""
SPARTN Custom Exception Types

Created on 10 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""


class ParameterError(Exception):
    """Parameter Error Class."""


class SPARTNParseError(Exception):
    """
    SPARTN Parsing error.
    """


class SPARTNDecryptionError(Exception):
    """
    SPARTN Decryption error.
    """


class SPARTNStreamError(Exception):
    """
    SPATRTN Streaming error.
    """


class SPARTNMessageError(Exception):
    """
    SPARTNUndefined message class/id.
    Essentially a prompt to add missing payload types to SPARTN_MGSIDS.
    """


class SPARTNTypeError(Exception):
    """
    SPARTN Undefined payload attribute type.
    """
