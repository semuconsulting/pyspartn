"""
Helper, Property and Static method tests for pyspartn.SPARTNMessage

Created on 10 Feb 2023

*** NB: must be saved in UTF-8 format ***

@author: semuadmin
"""

import os
import unittest
from datetime import datetime

from pyspartn.exceptions import SPARTNMessageError
from pyspartn.spartnhelpers import (
    att2idx,
    att2name,
    bitsval,
    convert_timetag,
    datadesc,
    date2timetag,
    decrypt,
    enc2float,
    encrypt,
    escapeall,
    timetag2date,
    valid_crc,
)


class StaticTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        dirname = os.path.dirname(__file__)

    def tearDown(self):
        pass

    def testbitsval(self):
        bits = [(7, 1), (8, 8), (22, 2), (24, 4)]
        EXPECTED_RESULT = [1, 8, 3, 15]

        bm = b"\x01\x08\x03\xf0\xff"
        for i, (ps, ln) in enumerate(bits):
            res = bitsval(bm, ps, ln)
            self.assertEqual(res, EXPECTED_RESULT[i])

    def testbitsvalerr(self):
        EXPECTED_ERROR = "Attribute size 16 exceeds remaining payload length 2"
        bm = b"\x01\x08\x03\xf0\xff"
        # print(f"Length bitfield = {len(bm) * 8}")
        with self.assertRaisesRegex(SPARTNMessageError, EXPECTED_ERROR):
            res = bitsval(bm, 38, 16)

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
        basedate = datetime(2023, 6, 27, 23, 13, 0)
        EXPECTED_RES = 425595780
        res = convert_timetag(32580, basedate)
        self.assertEqual(res, EXPECTED_RES)

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

    def testdatadesc(self):  # test datadesc
        res = datadesc("SF054")
        self.assertEqual(res, "Ionosphere equation type")
        res = datadesc("SF043_01")
        self.assertEqual(res, "Area average vertical hydrostatic delay")

    def testenc2float(self):  # test enc2float
        res = enc2float(1332, 0.1, -90)
        self.assertAlmostEqual(res, 43.20000000000002, 6)
        res = enc2float(2033, 0.1, -180)
        self.assertAlmostEqual(res, 23.30000000000001, 6)

    def testtimetag2date(self):  # test timetag2date
        res = timetag2date(425595780)
        self.assertEqual(res, datetime(2023, 6, 27, 21, 3, 0))

    def testdate2timetag(self):  # test date2timetag
        res = date2timetag(datetime(2023, 6, 27, 21, 3, 0))
        self.assertEqual(res, 425595780)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
