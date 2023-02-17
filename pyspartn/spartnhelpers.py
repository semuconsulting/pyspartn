"""
Collection of SPARTN helper methods which can be used
outside the SPARTNMessage or SPARTNReader classes

Created on 10 Feb 2023

:author: semuadmin
:copyright: SEMU Consulting © 2023
:license: BSD 3-Clause
"""
# pylint: disable=invalid-name


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


def crc_poly(data, n, poly, crc=0, ref_out=False, xor_out=0):
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

    :param bytes msg: message to which CRC appliec
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
