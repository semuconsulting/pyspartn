"""
Helper, Property and Static method tests for pyspartn.SPARTNMessage

Created on 10 Feb 2023

*** NB: must be saved in UTF-8 format ***

@author: semuadmin
"""

import os
import unittest
from datetime import datetime, timezone

try:
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

    HASCRYPTO = True
except (ImportError, ModuleNotFoundError):
    HASCRYPTO = False
    
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
    naive2aware,
    timetag2date,
    valid_crc,
)
from pyspartn.spartntypes_core import SPARTN_DATA_FIELDS, FL
from pyspartn.spartntables import (
    SF015_ENUM,
    SF022_ENUM,
    SF024_ENUM,
    SF042_ENUM,
    SF044_ENUM,
    SF051_ENUM,
    SF055_ENUM,
    SF056_ENUM,
    SF063_ENUM,
    SF070_ENUM,
    SF077_ENUM,
    SF078_ENUM,
    SF081_ENUM,
    SF085_ENUM,
    SF087_ENUM,
    SF090_ENUM,
    SF091_ENUM,
    SF093_ENUM,
    SF094_ENUM,
    SF095_ENUM,
    SF096_ENUM,
    SF097_ENUM,
    SF098_ENUM,
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

    def testbitsval2(self):
        bits = [(7, 1), (8, 8), (22, 2), (24, 4)]
        EXPECTED_RESULT = [-0.5, 3.0, 0.5, 6.5]

        bm = b"\x01\x08\x03\xf0\xff"
        for i, (ps, ln) in enumerate(bits):
            res = bitsval(bm, ps, ln, "FL", 0.5, -1.0)
            # print(res)
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
        if not HASCRYPTO:
            return
        
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
        basedate_gps = datetime(2023, 6, 27, 23, 13, 0, tzinfo=timezone.utc)
        EXPECTED_RES_GPS = 425595780
        res = convert_timetag(32580, basedate_gps)
        self.assertEqual(res, EXPECTED_RES_GPS)

        basedate_glo = datetime(2024, 4, 25, 11, 37, 0, tzinfo=timezone.utc)
        EXPECTED_RES_GLO = 451751822
        res = convert_timetag(9422, basedate_glo)
        self.assertEqual(res, EXPECTED_RES_GLO)

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
        EXPECTED_RESULT = [4, 16, 101, 0, (3, 6), 0]
        atts = ["svid_04", "gnssId_16", "cno_101", "gmsLon", "gnod_03_06", "dodgy_xx"]
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
        res = datadesc("SF049a")
        self.assertEqual(res, "Large troposphere coefficient T01")

    def testenc2float(self):  # test enc2float
        res = enc2float(1332, 0.1, -90)
        self.assertAlmostEqual(res, 43.20000000000002, 6)
        res = enc2float(2033, 0.1, -180)
        self.assertAlmostEqual(res, 23.30000000000001, 6)

    def testtimetag2date(self):  # test timetag2date
        res = timetag2date(425595780)
        self.assertEqual(res, datetime(2023, 6, 27, 21, 3, 0, tzinfo=timezone.utc))

    def testdate2timetag(self):  # test date2timetag
        res = date2timetag(datetime(2023, 6, 27, 21, 3, 0, tzinfo=timezone.utc))
        self.assertEqual(res, 425595780)

    def testdatafields(self):  # check float datafields are correctly configured
        for _, value in SPARTN_DATA_FIELDS.items():
            if value[1] == FL:
                self.assertTrue(
                    isinstance(value[3], (int, float))
                    and isinstance(value[2], (int, float))
                )

    def testtables(self):  # sanity check on lookup tables
        i = 0
        for tbl in (
            SF015_ENUM,
            SF022_ENUM,
            SF024_ENUM,
            SF042_ENUM,
            SF044_ENUM,
            SF051_ENUM,
            SF055_ENUM,
            SF056_ENUM,
            SF063_ENUM,
            SF070_ENUM,
            SF077_ENUM,
            SF078_ENUM,
            SF081_ENUM,
            SF085_ENUM,
            SF087_ENUM,
            SF090_ENUM,
            SF091_ENUM,
            SF093_ENUM,
            SF094_ENUM,
            SF095_ENUM,
            SF096_ENUM,
            SF097_ENUM,
            SF098_ENUM,
        ):
            i += len(tbl)
        self.assertEqual(i, 115)

    def testnaive2aware(self):
        dt1 = datetime(2022, 3, 4, 12, 34, 54)
        dt2 = datetime(2020, 3, 4, 10, 34, 54, tzinfo=timezone.utc)
        dt3 = 452383965
        self.assertEqual(
            naive2aware(dt1), datetime(2022, 3, 4, 12, 34, 54, tzinfo=timezone.utc)
        )
        self.assertEqual(
            naive2aware(dt2), datetime(2020, 3, 4, 10, 34, 54, tzinfo=timezone.utc)
        )
        self.assertEqual(naive2aware(dt3), 452383965)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
