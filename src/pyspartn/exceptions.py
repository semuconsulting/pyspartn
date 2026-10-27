"""
SPARTN Custom Exception Types

Created on 10 Feb 2023

:author: semuadmin (Steve Smith)
:copyright: semuadmin © 2023
:license: BSD 3-Clause
"""


class ParameterError(Exception):
    """Parameter Error Class."""


class SPARTNError(Exception):
    """
    Generic SPARTN Error Class.
    """


class SPARTNParseError(SPARTNError):
    """
    SPARTN Parsing error.
    """


class SPARTNDecryptionError(SPARTNError):
    """
    SPARTN Decryption error.
    """


class SPARTNStreamError(SPARTNError):
    """
    SPATRTN Streaming error.
    """


class SPARTNMessageError(SPARTNError):
    """
    SPARTNUndefined message class/id.
    Essentially a prompt to add missing payload types to SPARTN_MGSIDS.
    """


class SPARTNTypeError(SPARTNError):
    """
    SPARTN Undefined payload attribute type.
    """
