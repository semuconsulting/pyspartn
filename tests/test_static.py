"""
Helper, Property and Static method tests for pyspartn.SPARTNMessage

Created on 10 Feb 2023

*** NB: must be saved in UTF-8 format ***

@author: semuadmin
"""

import os
import unittest

from pyspartn.spartnhelpers import bitsval, valid_crc


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


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
