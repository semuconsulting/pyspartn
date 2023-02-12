"""
Created on 10 Feb 2023
Stream tests for pygpsclient.spartnreader

@author: semuadmin
"""

import os
import unittest
from pyspartn.exceptions import SPARTNMessageError, SPARTNParseError
from pyspartn.spartnreader import SPARTNReader, SPARTNMessage


class StaticTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        dirname = os.path.dirname(__file__)
        self.streamSPARTN = open(os.path.join(dirname, "spartn_mqtt.log"), "rb")
        self.spartnpayload = b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad"
        self.badpayload = b"x\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15"

    def tearDown(self):
        self.streamSPARTN.close()

    def testSerialize(self):  # test serialize()
        msg1 = SPARTNReader.parse(self.spartnpayload)
        msg2 = SPARTNMessage(payload=self.spartnpayload)
        res = msg1.serialize()
        self.assertEqual(res, self.spartnpayload)
        res1 = msg2.serialize()
        self.assertEqual(res1, self.spartnpayload)

    def testsetattr(self):  # test immutability
        EXPECTED_ERROR = (
            "Object is immutable. Updates to eaf not permitted after initialisation."
        )
        with self.assertRaisesRegex(SPARTNMessageError, EXPECTED_ERROR):
            msg = SPARTNReader.parse(self.spartnpayload)
            msg.eaf = 0

    def testrepr(self):  # test repr, check eval recreates original object
        EXPECTED_RESULT = "SPARTNMessage(payload=b's\\x00\\x12\\xe2\\x00|\\x10[\\x12H\\xf5\\t\\xa0\\xb4+\\x99\\x02\\x15\\xe2\\x05\\x85\\xb7\\x83\\xc5\\xfd\\x0f\\xfe\\xdf\\x18\\xbe\\x7fv \\xc3`\\x82\\x98\\x10\\x07\\xdc\\xeb\\x82\\x7f\\xcf\\xf8\\x9e\\xa3ta\\xad')"
        msg1 = SPARTNReader.parse(self.spartnpayload)
        self.assertEqual(repr(msg1), EXPECTED_RESULT)
        msg2 = eval(repr(msg1))
        self.assertEqual(str(msg1), str(msg2))

    def testpayload(self):  # test payload getter
        msg = SPARTNReader.parse(self.spartnpayload)
        payload = self.spartnpayload
        self.assertEqual(msg.payload, payload)

    def testnopayload(self):  # test null payload
        EXPECTED_ERROR = "Payload must be provided"
        with self.assertRaisesRegex(SPARTNMessageError, EXPECTED_ERROR):
            msg = SPARTNMessage(payload=None)

    def testbadpayload2(self):  # test null payload
        EXPECTED_ERROR = "Unknown message preamble 120"
        with self.assertRaisesRegex(SPARTNParseError, EXPECTED_ERROR):
            msg = SPARTNMessage(payload=self.badpayload)

    def testbadpayload(self):  # test null payload
        EXPECTED_ERROR = "Unknown message preamble 120"
        with self.assertRaisesRegex(SPARTNParseError, EXPECTED_ERROR):
            msg = SPARTNReader.parse(self.badpayload)

    def testSPARTNLOG(
        self,
    ):  # test stream of SPARTN messages
        EXPECTED_RESULTS = (
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3940, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=33, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=14722, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=34, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=3940, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=1, gnssTimeTag=413903145, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=33, eaf=1, crcType=2, frameCrc=3, timeTagtype=1, gnssTimeTag=413913927, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=34, eaf=1, crcType=2, frameCrc=3, timeTagtype=1, gnssTimeTag=413903145, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3950, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=33, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=14732, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=34, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=3950, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3955, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=33, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=14737, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=34, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=3955, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-GAD, msgType=2, msgSubtype=0, nData=191, eaf=1, crcType=2, frameCrc=14, timeTagtype=0, gnssTimeTag=3960, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-GAD, msgType=2, msgSubtype=0, nData=50, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3960, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, msgSubtype=0, nData=590, eaf=1, crcType=2, frameCrc=12, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, msgSubtype=0, nData=584, eaf=1, crcType=2, frameCrc=4, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, msgSubtype=0, nData=554, eaf=1, crcType=2, frameCrc=6, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, msgSubtype=0, nData=554, eaf=1, crcType=2, frameCrc=6, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, msgSubtype=1, nData=456, eaf=1, crcType=2, frameCrc=2, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, msgSubtype=1, nData=415, eaf=1, crcType=2, frameCrc=4, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, msgSubtype=1, nData=433, eaf=1, crcType=2, frameCrc=6, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, msgSubtype=1, nData=380, eaf=1, crcType=2, frameCrc=9, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, msgSubtype=2, nData=565, eaf=1, crcType=2, frameCrc=1, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, msgSubtype=2, nData=565, eaf=1, crcType=2, frameCrc=1, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, msgSubtype=2, nData=524, eaf=1, crcType=2, frameCrc=6, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, msgSubtype=2, nData=465, eaf=1, crcType=2, frameCrc=13, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=218, eaf=1, crcType=2, frameCrc=8, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=152, eaf=1, crcType=2, frameCrc=2, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=191, eaf=1, crcType=2, frameCrc=11, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3965, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=33, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=14747, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=34, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=3965, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, msgSubtype=0, nData=37, eaf=1, crcType=2, frameCrc=2, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, msgSubtype=1, nData=33, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=14752, solutionId=5, solutionProcId=11)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, msgSubtype=2, nData=34, eaf=1, crcType=2, frameCrc=3, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11)>",
        )

        i = 0
        raw = 0
        spr = SPARTNReader(self.streamSPARTN)
        for raw, parsed in spr.iterate():
            if raw is not None:
                self.assertEqual(str(parsed), EXPECTED_RESULTS[i])
                i += 1

    def testdatastream(self):  # test serialize()
        spr = SPARTNReader(self.streamSPARTN)
        res = str(spr.datastream)
        print(res[-17:])
        self.assertEqual(
            res[-17:],
            "spartn_mqtt.log'>",
        )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
