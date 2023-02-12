"""
Collection of RTCM helper methods which can be used
outside the RTCMMessage or RTCMReader classes

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

    return int.from_bytes(bitfield) >> (lbb - position - length) & (pow(2, length) - 1)
