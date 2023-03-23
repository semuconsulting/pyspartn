"""
Helper, Property and Static method tests for pyspartn.SPARTNMessage

Created on 10 Feb 2023

*** NB: must be saved in UTF-8 format ***

@author: semuadmin
"""

import os
import sys
import unittest
from datetime import datetime, timedelta

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.append(os.path.join(ROOT, "src"))

from pyspartn.spartnhelpers import (
    att2name,
    att2idx,
    bitsval,
    valid_crc,
    escapeall,
    encrypt,
    decrypt,
    convert_timetag,
    numbitsset,
)
from pyspartn.spartntypes_core import TIMEBASE


class StaticTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        dirname = os.path.dirname(__file__)

    def tearDown(self):
        pass

    def testbitsval(self):
        bits = [(7, 1), (8, 8), (22, 2), (24, 4), (40, 16)]
        EXPECTED_RESULT = [1, 8, 3, 15, None]

        bm = b"\x01\x08\x03\xf0\xff"
        for i, (ps, ln) in enumerate(bits):
            res = bitsval(bm, ps, ln)
            self.assertEqual(res, EXPECTED_RESULT[i])

    def testnumbitsset(self):
        vals = [7, 8, 22, 24, 4167, 234876]
        EXPECTED_RESULT = [3, 1, 3, 2, 5, 11]

        for i, val in enumerate(vals):
            res = numbitsset(val)
            self.assertEqual(res, EXPECTED_RESULT[i])

    def testCRC(self):
        msg = b"Hi!"
        self.assertTrue(valid_crc(msg, 0x78, 0))
        self.assertTrue(valid_crc(msg, 0x31FD, 1))
        self.assertTrue(valid_crc(msg, 0x33220F, 2))
        self.assertTrue(valid_crc(msg, 0x9523B4B4, 3))
        msg = b"Ho!"
        self.assertFalse(valid_crc(msg, 0x78, 0))
        self.assertFalse(valid_crc(msg, 0x31FD, 1))
        self.assertFalse(valid_crc(msg, 0x33220F, 2))
        self.assertFalse(valid_crc(msg, 0x9523B4B4, 3))

    def testCRCfail(self):  # test invalid crcType
        EXPECTED_ERROR = "Invalid crcType: 4 - should be 0-3"
        with self.assertRaisesRegex(ValueError, EXPECTED_ERROR):
            valid_crc("Hi!", 0x9523B4B4, 4)

    def testescapeall(self):
        EXPECTED_RESULT = "b'\\x68\\x65\\x72\\x65\\x61\\x72\\x65\\x73\\x6f\\x6d\\x65\\x63\\x68\\x61\\x72\\x73'"
        val = b"herearesomechars"
        res = escapeall(val)
        self.assertEqual(res, EXPECTED_RESULT)

    def testdecrypt(self):
        msg = b"your secret message"
        key = 0x395C12348D083E53AD0A5AA257C6A741.to_bytes(16, "big")
        iv = os.urandom(16)
        ct, pad = encrypt(msg, key, iv, "CTR")
        pt = decrypt(ct, key, iv, "CTR")
        self.assertEqual(msg, pt[0:-pad])
        ct, pad = encrypt(msg, key, iv, "CBC")
        pt = decrypt(ct, key, iv, "CBC")
        self.assertEqual(msg, pt[0:-pad])

    def testtimetag(self):
        timetag32 = (datetime(2023, 3, 14) - TIMEBASE).total_seconds()
        EXPECTED_SECS = 416451490
        EXPECTED_DATE = datetime(2023, 3, 14, 0, 58, 10)
        res = convert_timetag(3490, timetag32)
        self.assertEqual(res, EXPECTED_SECS)
        dat = TIMEBASE + timedelta(seconds=res)
        self.assertEqual(dat, EXPECTED_DATE)

    def testiv(self):
        IV32 = "031800c03cb4306c2b40000000000001"
        IV16 = "001400c03cb4586c2580000000000001"

        msgType = 0  # 1
        nData = 40  # 560
        msgSubtype = 0
        timeTag = 403150475  # 403150470
        solutionId = 6
        solutionProcId = 12
        encryptionId = 2
        encryptionSeq = 22  # 45

        iv = (
            (msgType << 121)  # TF002 7 bits
            + (nData << 111)  # TF003 10 bits
            + (msgSubtype << 107)  # TF007 4 bits
            + (timeTag << 75)  # TF009 32 bits
            + (solutionId << 68)  # TF010 7 bits
            + (solutionProcId << 64)  # TF011 4 bits
            + (encryptionId << 60)  # TF012 4 bits
            + (encryptionSeq << 54)  # TF012 6 bits
            + 1  # padding to 128 bits
        )
        iv16 = iv.to_bytes(16, "big")
        self.assertEqual(iv16.hex(), IV16)

        msgType = 1
        nData = 560
        msgSubtype = 0
        timeTag = 403150470
        solutionId = 6
        solutionProcId = 12
        encryptionId = 2
        encryptionSeq = 45

        iv = (
            (msgType << 121)  # TF002 7 bits
            + (nData << 111)  # TF003 10 bits
            + (msgSubtype << 107)  # TF007 4 bits
            + (timeTag << 75)  # TF009 32 bits
            + (solutionId << 68)  # TF010 7 bits
            + (solutionProcId << 64)  # TF011 4 bits
            + (encryptionId << 60)  # TF012 4 bits
            + (encryptionSeq << 54)  # TF012 6 bits
            + 1  # padding to 128 bits
        )
        iv32 = iv.to_bytes(16, "big")
        self.assertEqual(iv32.hex(), IV32)

    def testatt2idx(self):  # test att2idx
        EXPECTED_RESULT = [4, 16, 101, 0]
        atts = ["svid_04", "gnssId_16", "cno_101", "gmsLon"]
        for i, att in enumerate(atts):
            res = att2idx(att)
            # print(res)
            self.assertEqual(res, EXPECTED_RESULT[i])

    def testatt2name(self):  # test att2name
        EXPECTED_RESULT = ["svid", "gnssId", "cno", "gmsLon"]
        atts = ["svid_04", "gnssId_16", "cno_101", "gmsLon"]
        for i, att in enumerate(atts):
            res = att2name(att)
            # print(res)
            self.assertEqual(res, EXPECTED_RESULT[i])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
