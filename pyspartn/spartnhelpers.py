"""
Collection of SPARTN helper methods which can be used
outside the SPARTNMessage or SPARTNReader classes

Created on 10 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name

from datetime import datetime
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from pyspartn.spartntypes_core import TIMEBASE


def bitsval(bitfield: bytes, position: int, length: int) -> int:
    """
    Get unisgned integer value of masked bits in bitfield.

    :param bytes bitfield: bytes
    :param int position: position in bitfield, from leftmost bit
    :param int length: length of masked bits
    :return: value
    :rtype: int
    """

    lbb = len(bitfield) * 8
    if position + length > lbb:
        return None

    return (
        int.from_bytes(bitfield, "big") >> (lbb - position - length) & 2**length - 1
    )


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
    :return: encrypted data
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


def convert_timetag(timetag16: int) -> int:
    """
    Convert 16-bit timetag to 32-bit format.
    16-bit format = half days in seconds
    32-bit format = total seconds since 2010-01-01

    TODO it appears this may require the 32-bit timetag from an earlier SPARTN message

    :param int timetag16: 16-bit gnssTimeTag
    :return: 32-bit gnssTimeTag
    :rtype: int
    """

    # time32 = 32-bit timetag from another SPARTN message
    time32 = (datetime.now() - TIMEBASE).total_seconds()
    basis32 = time32 - (time32 % 43200)
    timetag32 = timetag16 + basis32
    return int(timetag32)
