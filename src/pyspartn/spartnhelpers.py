"""
Collection of SPARTN helper methods which can be used
outside the SPARTNMessage or SPARTNReader classes

Created on 10 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""

# pylint: disable=invalid-name

from datetime import datetime, timedelta

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

from pyspartn.exceptions import SPARTNMessageError
from pyspartn.spartntypes_core import SPARTN_DATA_FIELDS, TIMEBASE


def datadesc(datafield: str) -> str:
    """
    Get description of data field.

    :param str datafield: datafield e.g. 'SF054'
    :return: datafield description e.g. "Ionosphere equation type"
    :rtype: str
    """

    (_, _, desc) = SPARTN_DATA_FIELDS[datafield[0:5]]
    return desc


def att2idx(att: str) -> int:
    """
    Get integer index corresponding to grouped attribute.
    e.g. SF019_04 -> 4; SF019_23 -> 23

    :param str att: grouped attribute name e.g. SF019_01
    :return: index as integer, or 0 if not grouped
    :rtype: int
    """

    try:
        return int(att[att.rindex("_") - len(att) + 1 :])
    except ValueError:
        return 0


def att2name(att: str) -> str:
    """
    Get name of grouped attribute.
    e.g. SF019 -> SF019; SF019_23 -> SF019

    :param str att: grouped attribute name e.g. SF019_06
    :return: name without index e.g. SF019
    :rtype: str
    """

    try:
        return att[: att.rindex("_")]
    except ValueError:
        return att


def bitsval(bitfield: bytes, position: int, length: int) -> int:
    """
    Get unisgned integer value of masked bits in bytes.

    :param bytes bitfield: bytes
    :param int position: position in bitfield, from leftmost bit
    :param int length: length of masked bits
    :return: value
    :rtype: int
    :raises: SPARTNMessageError if end of bitfield
    """

    lbb = len(bitfield) * 8
    if position + length > lbb:
        raise SPARTNMessageError(
            f"Attribute size {length} exceeds remaining payload length {lbb - position}"
        )

    return int.from_bytes(bitfield, "big") >> (lbb - position - length) & 2**length - 1


def crc_poly(
    data: int, n: int, poly: int, crc: int = 0, ref_out: bool = False, xor_out: int = 0
) -> int:
    """
    Configurable CRC algorithm.

    :param int data: data
    :param int n: width
    :param int poly: polynomial feed value
    :param int crc: crc
    :param ref_out: reflection out
    :param xor_out: XOR out
    :return: CRC
    :rtype: int
    """
    # pylint: disable=unused-argument, too-many-arguments

    g = 1 << n | poly  # Generator polynomial

    # Loop over the data
    for d in data:
        # XOR the top byte in the CRC with the input byte
        crc ^= d << (n - 8)

        # Loop over all the bits in the byte
        for _ in range(8):
            # Start by shifting the CRC, so we can check for the top bit
            crc <<= 1

            # XOR the CRC if the top bit is 1
            if crc & (1 << n):
                crc ^= g

    # Return the CRC value
    return crc ^ xor_out


def valid_crc(msg: bytes, crc: int, crcType: int) -> bool:
    """
    Validate message CRC.

    :param bytes msg: message to which CRC applies
    :param int crc: message CRC
    :param int cycType: crc type (0-3)
    """

    if crcType == 0:
        crcchk = crc_poly(msg, 8, 0x07)
    elif crcType == 1:
        crcchk = crc_poly(msg, 16, 0x1021)
    elif crcType == 2:
        crcchk = crc_poly(msg, 24, 0x864CFB)
    elif crcType == 3:
        crcchk = crc_poly(msg, 32, 0x04C11DB7, crc=0xFFFFFFFF, xor_out=0xFFFFFFFF)
    else:
        raise ValueError(f"Invalid crcType: {crcType} - should be 0-3")
    return crc == crcchk


def encrypt(pt: bytes, key: bytes, iv: bytes, mode: str = "CTR") -> tuple:
    """
    Encrypt payload
    The length of the plaintext data must be a multiple of
    the cipher block length (16 bytes), so padding bytes are
    added as necessary.

    :param bytes data: plaintext data
    :param bytes key: key
    :param bytes iv: initialisation vector
    :param str mode: cipher mode e.g. CTR, CBC
    :return: tuple of (encrypted data, number of padding bytes)
    :rtype: tuple
    """

    if mode == "CTR":
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
    else:
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

    pad = 16 - len(pt) % 16
    PADDING_BYTE = pad.to_bytes(1, "big")

    encryptor = cipher.encryptor()
    ct = encryptor.update(pt + (pad * PADDING_BYTE)) + encryptor.finalize()
    return ct, pad


def decrypt(ct: bytes, key: bytes, iv: bytes, mode: str = "CTR") -> bytes:
    """
    Decrypt payload

    :param bytes ct: encrypted data (ciphertext)
    :param bytes key: key
    :param bytes iv: initialisation vector
    :param str mode: cipher mode e.g. CTR, CBC
    :return: decrypted data (plaintext)
    :rtype: bytes
    """

    if mode == "CTR":
        cipher = Cipher(algorithms.AES(key), modes.CTR(iv))
    else:
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))

    decryptor = cipher.decryptor()
    pt = decryptor.update(ct) + decryptor.finalize()
    return pt


def escapeall(val: bytes) -> str:
    """
    Escape all byte characters e.g. b'\\\\x73' rather than b`s`

    :param bytes val: bytes
    :return: string of escaped bytes
    :rtype: str
    """

    return "b'{}'".format("".join(f"\\x{b:02x}" for b in val))


def timetag2date(timetag32: int) -> datetime:
    """
    Convert 32-bit gnsstimetag to datetime.

    :param int timetag: 32-bit gnsstimetag
    :returns: date
    :rtype: datetime
    """

    return TIMEBASE + timedelta(seconds=timetag32)


def date2timetag(date: datetime) -> int:
    """
    Convert datetime to 32-bit gnsstimetag.

    :param datetime date: date
    :returns: 32-bit gnssTimeTag
    :rtype: int
    """

    return int((date - TIMEBASE).total_seconds())


def convert_timetag(timetag16: int, basedate: datetime = datetime.now()) -> int:
    """
    Convert 16-bit timetag to 32-bit format.

    32-bit timetag represents total seconds since 2010-01-01 00:00:00 (TIMEBASE).

    16-bit timetag represents seconds past 'base date' (the datetime the SPARTN
    message was originally sent, to the nearest half-day). It requires knowledge
    of this base date to convert unambiguously to a 32-bit timetag equlvalent, e.g.

    If base date to nearest half day was "2023-06-27 12:00:00", a timetag16 of
    32580 represents a datetime of:

    (2023-06-27 00:00:00 + 12 hours + 32580 seconds) = 2023-06-27 21:03:00

    To convert to a 32-bit timetag, calculate number of seconds since TIMEBASE:

    (2023-06-27 21:03:00 - 2010-01-01 00:00:00) = 425595780 seconds

    :param int timetag16: 16-bit gnssTimeTag
    :param datetime basedate: original processing datetime to nearest half day
    :return: 32-bit gnssTimeTag
    :rtype: int
    """

    base16 = datetime(basedate.year, basedate.month, basedate.day, 0, 0, 0)
    secs = timetag16
    if basedate.hour >= 12:
        secs += 43200
    time16 = base16 + timedelta(seconds=secs)
    return date2timetag(time16)


def enc2float(value: int, res: float, rngmin: float) -> float:
    """
    Convert encoded floating point value to float.

    SPARTN protocol stores floating point numbers in
    encoded integer format.

    :param int value: encoded value
    :param float res: resolution
    :param float rngmin: minimum range value
    :return: floating point value
    :rtype: float
    """

    return (value * res) + rngmin
