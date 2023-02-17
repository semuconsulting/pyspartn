"""
Created on 10 Feb 2023
Stream tests for pygpsclient.spartnreader

@author: semuadmin
"""

import os
import unittest
from pyspartn.exceptions import SPARTNMessageError, SPARTNParseError
from pyspartn.spartnreader import SPARTNReader, SPARTNMessage


class StreamTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        dirname = os.path.dirname(__file__)
        self.streamSPARTN = open(os.path.join(dirname, "spartn_mqtt.log"), "rb")
        self.streamBADCRC = open(os.path.join(dirname, "spartn_badcrc.log"), "rb")
        self.spartntransport = b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad"
        self.spartnbadcrc = b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xa1"
        self.badpayload = b"x\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15"

    def tearDown(self):
        self.streamSPARTN.close()
        self.streamBADCRC.close()

    def testSerialize(self):  # test serialize()
        msg1 = SPARTNReader.parse(self.spartntransport)
        msg2 = SPARTNMessage(transport=self.spartntransport)
        res = msg1.serialize()
        self.assertEqual(res, self.spartntransport)
        res1 = msg2.serialize()
        self.assertEqual(res1, self.spartntransport)

    def testsetattr(self):  # test immutability
        EXPECTED_ERROR = (
            "Object is immutable. Updates to eaf not permitted after initialisation."
        )
        with self.assertRaisesRegex(SPARTNMessageError, EXPECTED_ERROR):
            msg = SPARTNReader.parse(self.spartntransport)
            msg.eaf = 0

    def testrepr(self):  # test repr, check eval recreates original object
        EXPECTED_RESULT = "SPARTNMessage(transport=b's\\x00\\x12\\xe2\\x00|\\x10[\\x12H\\xf5\\t\\xa0\\xb4+\\x99\\x02\\x15\\xe2\\x05\\x85\\xb7\\x83\\xc5\\xfd\\x0f\\xfe\\xdf\\x18\\xbe\\x7fv \\xc3`\\x82\\x98\\x10\\x07\\xdc\\xeb\\x82\\x7f\\xcf\\xf8\\x9e\\xa3ta\\xad')"
        msg1 = SPARTNReader.parse(self.spartntransport)
        self.assertEqual(repr(msg1), EXPECTED_RESULT)
        msg2 = eval(repr(msg1))
        self.assertEqual(str(msg1), str(msg2))

    def testpayload(self):  # test payload
        EXPECTED_RESULT = b"\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3"
        msg = SPARTNReader.parse(self.spartntransport)
        self.assertEqual(msg.payload, EXPECTED_RESULT)
        self.assertEqual(msg.nData, len(msg.payload))

    def testnopayload(self):  # test null payload
        EXPECTED_ERROR = "Transport must be provided"
        with self.assertRaisesRegex(SPARTNMessageError, EXPECTED_ERROR):
            msg = SPARTNMessage(transport=None)

    def testbadpayload2(self):  # test null payload
        EXPECTED_ERROR = "Unknown message preamble 120"
        with self.assertRaisesRegex(SPARTNParseError, EXPECTED_ERROR):
            msg = SPARTNMessage(transport=self.badpayload)

    def testbadpayload(self):  # test null payload
        EXPECTED_ERROR = "Unknown message preamble 120"
        with self.assertRaisesRegex(SPARTNParseError, EXPECTED_ERROR):
            msg = SPARTNReader.parse(self.badpayload)

    def testbadcrc(self):  # test bad CRC
        EXPECTED_ERROR = "Invalid CRC 7627169"
        with self.assertRaisesRegex(SPARTNMessageError, EXPECTED_ERROR):
            msg = SPARTNReader.parse(self.spartnbadcrc)

    def testbadcrc2(self):  # test stream of SPARTN messages
        EXPECTED_ERROR = "Invalid CRC 15632804"
        with self.assertRaisesRegex(SPARTNParseError, EXPECTED_ERROR):
            spr = SPARTNReader(self.streamBADCRC, quitonerror=2)
            for raw, parsed in spr.iterate():
                pass

    def testSPARTNLOG(
        self,
    ):  # test stream of SPARTN messages
        EXPECTED_RESULTS = (
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3940, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=3, authInd=1, embAuthLen=0, crc=7556915)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=33, eaf=1, crcType=2, frameCrc=3, msgSubtype=1, timeTagtype=0, gnssTimeTag=14722, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=42, authInd=1, embAuthLen=0, crc=13784453)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=34, eaf=1, crcType=2, frameCrc=3, msgSubtype=2, timeTagtype=0, gnssTimeTag=3940, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=63, authInd=1, embAuthLen=0, crc=15726580)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=1, gnssTimeTag=413903145, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=4, authInd=1, embAuthLen=0, crc=6997525)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=33, eaf=1, crcType=2, frameCrc=3, msgSubtype=1, timeTagtype=1, gnssTimeTag=413913927, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=43, authInd=1, embAuthLen=0, crc=11358619)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=34, eaf=1, crcType=2, frameCrc=3, msgSubtype=2, timeTagtype=1, gnssTimeTag=413903145, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=0, authInd=1, embAuthLen=0, crc=16183954)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3950, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=5, authInd=1, embAuthLen=0, crc=9417614)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=33, eaf=1, crcType=2, frameCrc=3, msgSubtype=1, timeTagtype=0, gnssTimeTag=14732, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=44, authInd=1, embAuthLen=0, crc=2885277)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=34, eaf=1, crcType=2, frameCrc=3, msgSubtype=2, timeTagtype=0, gnssTimeTag=3950, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=1, authInd=1, embAuthLen=0, crc=7937704)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3955, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=6, authInd=1, embAuthLen=0, crc=2323099)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=33, eaf=1, crcType=2, frameCrc=3, msgSubtype=1, timeTagtype=0, gnssTimeTag=14737, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=45, authInd=1, embAuthLen=0, crc=6930276)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=34, eaf=1, crcType=2, frameCrc=3, msgSubtype=2, timeTagtype=0, gnssTimeTag=3955, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=2, authInd=1, embAuthLen=0, crc=1602694)>",
            "<SPARTN(SPARTN-1X-GAD, msgType=2, nData=191, eaf=1, crcType=2, frameCrc=14, msgSubtype=0, timeTagtype=0, gnssTimeTag=3960, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=63, authInd=1, embAuthLen=0, crc=13757653)>",
            "<SPARTN(SPARTN-1X-GAD, msgType=2, nData=50, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3960, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=0, authInd=1, embAuthLen=0, crc=11582036)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, nData=590, eaf=1, crcType=2, frameCrc=12, msgSubtype=0, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=52, authInd=1, embAuthLen=0, crc=7879592)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, nData=584, eaf=1, crcType=2, frameCrc=4, msgSubtype=0, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=53, authInd=1, embAuthLen=0, crc=5046464)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, nData=554, eaf=1, crcType=2, frameCrc=6, msgSubtype=0, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=54, authInd=1, embAuthLen=0, crc=14377135)>",
            "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, nData=554, eaf=1, crcType=2, frameCrc=6, msgSubtype=0, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=55, authInd=1, embAuthLen=0, crc=5226642)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, nData=456, eaf=1, crcType=2, frameCrc=2, msgSubtype=1, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=11, authInd=1, embAuthLen=0, crc=4825390)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, nData=415, eaf=1, crcType=2, frameCrc=4, msgSubtype=1, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=12, authInd=1, embAuthLen=0, crc=2661822)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, nData=433, eaf=1, crcType=2, frameCrc=6, msgSubtype=1, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=13, authInd=1, embAuthLen=0, crc=4661009)>",
            "<SPARTN(SPARTN-1X-HPAC-GLO, msgType=1, nData=380, eaf=1, crcType=2, frameCrc=9, msgSubtype=1, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=14, authInd=1, embAuthLen=0, crc=6432064)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, nData=565, eaf=1, crcType=2, frameCrc=1, msgSubtype=2, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=15, authInd=1, embAuthLen=0, crc=9900363)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, nData=565, eaf=1, crcType=2, frameCrc=1, msgSubtype=2, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=16, authInd=1, embAuthLen=0, crc=3171880)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, nData=524, eaf=1, crcType=2, frameCrc=6, msgSubtype=2, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=17, authInd=1, embAuthLen=0, crc=3600973)>",
            "<SPARTN(SPARTN-1X-HPAC-GAL, msgType=1, nData=465, eaf=1, crcType=2, frameCrc=13, msgSubtype=2, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=18, authInd=1, embAuthLen=0, crc=11477640)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=218, eaf=1, crcType=2, frameCrc=8, msgSubtype=0, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=7, authInd=1, embAuthLen=0, crc=4538711)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=152, eaf=1, crcType=2, frameCrc=2, msgSubtype=1, timeTagtype=1, gnssTimeTag=413913942, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=46, authInd=1, embAuthLen=0, crc=8221523)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=191, eaf=1, crcType=2, frameCrc=11, msgSubtype=2, timeTagtype=1, gnssTimeTag=413903160, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=3, authInd=1, embAuthLen=0, crc=12340159)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3965, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=8, authInd=1, embAuthLen=0, crc=6970314)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=33, eaf=1, crcType=2, frameCrc=3, msgSubtype=1, timeTagtype=0, gnssTimeTag=14747, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=47, authInd=1, embAuthLen=0, crc=12368174)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=34, eaf=1, crcType=2, frameCrc=3, msgSubtype=2, timeTagtype=0, gnssTimeTag=3965, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=4, authInd=1, embAuthLen=0, crc=8851501)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=9, authInd=1, embAuthLen=0, crc=7627181)>",
            "<SPARTN(SPARTN-1X-OCB-GLO, msgType=0, nData=33, eaf=1, crcType=2, frameCrc=3, msgSubtype=1, timeTagtype=0, gnssTimeTag=14752, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=48, authInd=1, embAuthLen=0, crc=15490832)>",
            "<SPARTN(SPARTN-1X-OCB-GAL, msgType=0, nData=34, eaf=1, crcType=2, frameCrc=3, msgSubtype=2, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=5, authInd=1, embAuthLen=0, crc=15632803)>",
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
