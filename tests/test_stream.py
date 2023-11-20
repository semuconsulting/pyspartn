"""
Created on 10 Feb 2023
Stream tests for pygpsclient.spartnreader

@author: semuadmin
"""

import os
import sys
import unittest
from io import StringIO
from datetime import datetime

from pyspartn.exceptions import SPARTNMessageError, SPARTNParseError, ParameterError
from pyspartn.spartnreader import SPARTNReader, SPARTNMessage
from pyspartn.spartntypes_core import ERRRAISE, ERRIGNORE, ERRLOG

SPARTNKEY_HPAC = "0d1472ea83e351d8b24632ed42f0cee2"
SPARTN_KEY_GAD = "6b30302427df05b4d98911ebff3a4d95"
SPARTN_BASEDATE_GAD = datetime(2023, 6, 27, 22, 3, 0)
SPARTN_KEY_OCB = "bc75cdd919406d61c3df9e26c2f7e77a"
SPARTN_BASEDATE_OCB = datetime(2023, 9, 1, 18, 0, 0)


class StreamTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.dirname = os.path.dirname(__file__)
        self.streamSPARTN = open(os.path.join(self.dirname, "spartn_mqtt.log"), "rb")
        self.streamBADCRC = open(os.path.join(self.dirname, "spartn_badcrc.log"), "rb")
        self.streamBADPRE = open(
            os.path.join(self.dirname, "spartn_badpreamble.log"), "rb"
        )
        self.spartntransport = b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad"
        self.spartnbadcrc = b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xa1"
        self.badpayload = b"x\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15"

    def tearDown(self):
        self.streamSPARTN.close()
        self.streamBADCRC.close()
        self.streamBADPRE.close()

    def catchio(self):
        """
        Capture stdout as string.
        """

        self._saved_stdout = sys.stdout
        self._strout = StringIO()
        sys.stdout = self._strout

    def restoreio(self) -> str:
        """
        Return captured output and restore stdout.
        """

        sys.stdout = self._saved_stdout
        return self._strout.getvalue().strip()

    def testSerialize(self):  # test serialize()
        msg1 = SPARTNReader.parse(self.spartntransport, decode=False)
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
        msg1 = SPARTNReader.parse(self.spartntransport, decode=False)
        self.assertEqual(repr(msg1), EXPECTED_RESULT)
        msg2 = eval(repr(msg1))
        self.assertEqual(str(msg1), str(msg2))

    def testpayload(self):  # test payload
        EXPECTED_RESULT = b"\xf5\x09\xa0\xb4\x2b\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7f\x76\x20\xc3\x60\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3"
        msg = SPARTNReader.parse(self.spartntransport)
        # print(msg)
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

    def testERRRAISE(self):  # test stream of SPARTN messages with quitonerror = 2
        EXPECTED_ERROR = "Invalid CRC 15632804"
        with self.assertRaisesRegex(SPARTNParseError, EXPECTED_ERROR):
            spr = SPARTNReader(self.streamBADCRC, quitonerror=ERRRAISE)
            for raw, parsed in spr:
                pass

    def testERRRAISE2(self):  # test stream of SPARTN messages with quitonerror = 2
        EXPECTED_ERROR = "Unknown protocol b'\xaa'"
        with self.assertRaises(SPARTNParseError):
            spr = SPARTNReader(self.streamBADPRE, quitonerror=ERRRAISE)
            for raw, parsed in spr:
                pass

    def testERRLOG(self):  # test stream of SPARTN messages with quitonerror = 1
        EXPECTED_OUTPUT = "Invalid CRC 15632804"
        self.catchio()
        spr = SPARTNReader(self.streamBADCRC, quitonerror=ERRLOG)
        for raw, parsed in spr:
            pass
        output = self.restoreio()
        self.assertEqual(output, EXPECTED_OUTPUT)

    def testERRIGNORE(self):  # test stream of SPARTN messages with quitonerror = 1
        EXPECTED_OUTPUT = ""
        self.catchio()
        spr = SPARTNReader(self.streamBADCRC, quitonerror=ERRIGNORE)
        for raw, parsed in spr:
            pass
        output = self.restoreio()
        self.assertEqual(output, EXPECTED_OUTPUT)

    def testERRHandler(self):  # test stream of SPARTN messages with quitonerror = 1
        def igor(err):
            print(f"The error was ({err})")

        EXPECTED_OUTPUT = "The error was (Invalid CRC 15632804)"
        self.catchio()
        spr = SPARTNReader(self.streamBADCRC, quitonerror=ERRLOG, errorhandler=igor)
        for raw, parsed in spr:
            pass
        output = self.restoreio()
        self.assertEqual(output, EXPECTED_OUTPUT)

    def testpayloadgetter(self):  # test decrypted payload property
        EXPECTED_RESULT = b"\xfe\x09\x20\x00\x14\xa7\xfb\x56\x02\xfd\x20\x21\x81\x0c\x8b\x62\xf0\x82\xaa\x00\xf5\xc9\x49\x06\x3c\x00\x2b\x85\xea\x0e\xa8\x07\xdb\x20\x94\x03\xef\xfb\x36\x61\x08\x77\x20\x43\x5c\x35\x70\x76\x40\x68\x98\xb5\x20\x78\x81\x71\x31\x79\x41\x69\x03\x08\x08\x05\x29\xfe\xd9\x7e\xbf\x48\x08\x60\x43\x22\xd8\xa0\x20\x82\x7f\xf9\xf2\x13\xc2\x1a\xff\x23\x60\xc0\x83\x12\x01\xb5\xc7\xef\x02\x73\xfe\xab\x92\xf6\x15\x68\x0a\x97\x06\xd4\x19\xd0\x16\xa6\x1f\xd8\x29\xe0\x5b\x5c\x3e\x70\x74\x40\xbe\x04\x01\x49\x7f\xb4\x60\x2f\xf2\x02\x18\x10\xc8\x8e\x29\x68\x2c\x60\x0d\x2c\x80\xf0\x87\x40\x0e\x58\x43\xa0\xa6\x80\xc9\x31\xf7\x40\x6d\x00\x29\xe5\x31\x85\xf2\x02\x83\xc2\x87\x05\xf4\x07\xa5\x8b\x16\x09\xa8\x1a\x8f\x15\xb4\x1a\xd0\x38\x01\x80\x52\x5f\xed\x88\x0c\x08\x80\x86\x04\x32\x29\x89\xb9\xf7\x98\x05\x93\x1e\x3c\x02\x70\x06\x1e\x07\xf7\xf6\xe0\x21\x4c\x80\xef\xa7\x40\x18\xb9\x0e\x60\x77\x80\x84\x70\x3e\x3f\x9f\x01\xf1\x61\x82\x7f\x96\x06\x52\xc2\xfc\xfd\x7c\x0c\x60\x80\x14\x97\xfb\x51\xf8\xfc\x20\x21\x81\x0c\x88\xe2\x94\x7e\xd1\xff\xb3\xc7\x43\x02\xc3\xfe\x23\x83\xb5\xfd\xa8\x09\xd3\x21\x2b\xe5\xcf\xf6\x1e\x48\x58\x27\x20\x1f\x2c\x26\x0f\xe6\x40\x84\x38\xac\x9f\x8d\x81\xc4\xb1\x5a\xbe\xf7\x03\xb0\x28\x05\x26\x02\xd2\x80\x40\xc8\x08\x60\x43\x32\x98\xc1\xde\xfe\x81\x01\x72\x04\x3e\xd3\x00\x30\xe0\xc1\x7d\x7e\x05\x14\xc9\xa4\xf1\xa4\x06\x45\x90\xb5\xff\x78\x0d\x07\x05\x4b\xec\x50\x3c\x1e\x1a\x77\xcd\x20\x93\x3c\x7c\xcf\xf5\x41\x46\x58\x69\x5f\x41\x82\x70\x18\x02\x93\x01\x6b\x41\x60\x04\x04\x30\x21\x99\x1c\x69\x6f\x7f\x40\x78\xb9\x11\x5f\xbb\x80\x2c\xb0\x9c\x3e\xaf\x02\x49\xe5\x4b\x79\x5a\x04\xa4\xc8\xda\xfe\xcc\x0a\xc3\x85\x51\xf4\xa8\x1b\x07\x14\xd3\xda\x30\x56\x1e\x4c\x77\xf2\x20\xa6\x1c\x52\x6f\x84\xc1\x54\x0e\x01\x49\x80\xb6\x20\x2f\xf2\x02\x18\x10\xcc\x96\x30\xb7\xe5\xdf\xf7\x4c\x76\x2f\xf4\xbf\xcc\x38\x4b\xdf\xb8\x80\xa8\xb2\x74\x3d\xfe\xff\xca\x64\x63\x81\xfa\x02\x81\xc3\x02\xfc\xc4\x0a\x65\x8d\x15\xf1\x38\x22\x8f\x2a\xcc\x0e\x50\x48\x8e\x33\x17\xda\xa0\x84\x08\x00\xa5\x40\x59\x4f\xe8\x01\x01\x0c\x00\x66\x5b\x1c\x0b\xd1\xd0\x00\x2e\x4f\x77\xca\x9f\x94\x1c\x18\x2f\x93\x40\x32\x99\x06\xdf\xf8\x80\x3c\xb0\x3d\xbe\x85\x01\xa9\x61\x14\x7b\x92\x06\xe4\xc6\x03\x02\x0c\x08\x65\x84\x9d\xf3\xb8\x17\xc2\x40\x29\x50\x16\x6b\xf6\x08\x40\x43\x02\x19\x94\xc6\x7a\xfb\x03\xf9\x29\x8f\x3e\x03\x17\xf2\x07\x06\xdb\xf9\x4f\xf9\xa6\x59\x27\xbe\x1f\xec\x4c\x74\x30\x2c\x3f\xe2\x38\x3b\x9f\xce\x80\x7c\x71\x3a\x3e\x79\x03\x2a\xe3\xbc\x82\x46\x04\x11\xc4\x6e\xfd\x7c\x0a\x40"
        with open(os.path.join(self.dirname, "spartnHPAC.log"), "rb") as stream:
            spr = SPARTNReader(
                stream,
                quitonerror=ERRRAISE,
                decode=True,
                key=SPARTNKEY_HPAC,
            )
            for raw, parsed in spr:
                if raw is not None:
                    # print(parsed.payload)
                    self.assertEqual(parsed.payload, EXPECTED_RESULT)

    def testHPACLOG(
        self,
    ):  # test decoding of SPARTN HPAC message
        EXPECTED_RESULT = "<SPARTN(SPARTN-1X-HPAC-GPS, msgType=1, nData=619, eaf=1, crcType=2, frameCrc=12, msgSubtype=0, timeTagtype=1, gnssTimeTag=419070990, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=63, authInd=1, embAuthLen=0, crc=5760935, SF005=508, SF068=1, SF069=0, SF030=9, SF031_01=0, SF039_01=0, SF040T_01=1, SF040I_01=1, SF041_01=1, SF042_01=2, SF043_01=127, SF044_01=1, SF048_01=213, SF049a_01=257, SF049b_01=253, SF054_01=1, SatBitmaskLen_01=0, SF011_01=70263185, SF055_01_01=6, SF056_01_01=1, SF060_01_01=8944, SF061a_01_01=8362, SF061b_01_01=8207, SF055_01_02=5, SF056_01_02=1, SF060_01_02=9380, SF061a_01_02=8391, SF061b_01_02=8193, SF055_01_03=5, SF056_01_03=1, SF060_01_03=8570, SF061a_01_03=8426, SF061b_01_03=8223, SF055_01_04=6, SF056_01_04=1, SF060_01_04=9234, SF061a_01_04=8223, SF061b_01_04=8182, SF055_01_05=6, SF056_01_05=1, SF060_01_05=9744, SF061a_01_05=8668, SF061b_01_05=8259, SF055_01_06=5, SF056_01_06=1, SF060_01_06=8619, SF061a_01_06=8428, SF061b_01_06=8244, SF055_01_07=4, SF056_01_07=1, SF060_01_07=8916, SF061a_01_07=8312, SF061b_01_07=8284, SF055_01_08=4, SF056_01_08=1, SF060_01_08=8946, SF061a_01_08=8372, SF061b_01_08=8289, SF031_02=1, SF039_02=0, SF040T_02=1, SF040I_02=1, SF041_02=1, SF042_02=2, SF043_02=127, SF044_02=1, SF048_02=217, SF049a_02=253, SF049b_02=253, SF054_02=1, SatBitmaskLen_02=0, SF011_02=70263185, SF055_02_01=6, SF056_02_01=1, SF060_02_01=8832, SF061a_02_01=8322, SF061b_02_01=8190, SF055_02_02=7, SF056_02_02=1, SF060_02_02=9255, SF061a_02_02=8461, SF061b_02_02=8164, SF055_02_03=6, SF056_02_03=1, SF060_02_03=8384, SF061a_02_03=8388, SF061b_02_03=8219, SF055_02_04=5, SF056_02_04=1, SF060_02_04=9207, SF061a_02_04=8270, SF061b_02_04=8181, SF055_02_05=5, SF056_02_05=1, SF060_02_05=9405, SF061a_02_05=8534, SF061b_02_05=8234, SF055_02_06=5, SF056_02_06=1, SF060_02_06=8410, SF061a_02_06=8398, SF061b_02_06=8237, SF055_02_07=4, SF056_02_07=1, SF060_02_07=8701, SF061a_02_07=8359, SF061b_02_07=8283, SF055_02_08=5, SF056_02_08=1, SF060_02_08=8691, SF061a_02_08=8424, SF061b_02_08=8287, SF031_03=2, SF039_03=0, SF040T_03=1, SF040I_03=1, SF041_03=1, SF042_03=1, SF043_03=127, SF044_03=1, SF048_03=209, SF049a_03=257, SF049b_03=255, SF054_03=1, SatBitmaskLen_03=0, SF011_03=70263185, SF055_03_01=1, SF056_03_01=1, SF060_03_01=8854, SF061a_03_01=8369, SF061b_03_01=8205, SF055_03_02=2, SF056_03_02=1, SF060_03_02=9223, SF061a_03_02=8462, SF061b_03_02=8199, SF055_03_03=2, SF056_03_03=1, SF060_03_03=8462, SF061a_03_03=8358, SF061b_03_03=8242, SF055_03_04=4, SF056_03_04=1, SF060_03_04=9198, SF061a_03_04=8246, SF061b_03_04=8197, SF055_03_05=3, SF056_03_05=1, SF060_03_05=9521, SF061a_03_05=8572, SF061b_03_05=8232, SF055_03_06=3, SF056_03_06=1, SF060_03_06=8515, SF061a_03_06=8382, SF061b_03_06=8253, SF055_03_07=2, SF056_03_07=1, SF060_03_07=8901, SF061a_03_07=8346, SF061b_03_07=8298, SF055_03_08=3, SF056_03_08=1, SF060_03_08=8886, SF061a_03_08=8406, SF061b_03_08=8304, SF031_04=3, SF039_04=0, SF040T_04=1, SF040I_04=1, SF041_04=1, SF042_04=1, SF043_04=127, SF044_04=1, SF048_04=216, SF049a_04=257, SF049b_04=258, SF054_04=1, SatBitmaskLen_04=0, SF011_04=70263185, SF055_04_01=4, SF056_04_01=1, SF060_04_01=8814, SF061a_04_01=8057, SF061b_04_01=8214, SF055_04_02=4, SF056_04_02=1, SF060_04_02=9159, SF061a_04_02=8211, SF061b_04_02=8204, SF055_04_03=3, SF056_04_03=1, SF060_04_03=8319, SF061a_04_03=8155, SF061b_04_03=8225, SF055_04_04=4, SF056_04_04=1, SF060_04_04=9223, SF061a_04_04=8014, SF061b_04_04=8204, SF055_04_05=5, SF056_04_05=1, SF060_04_05=9273, SF061a_04_05=8311, SF061b_04_05=8225, SF055_04_06=1, SF056_04_06=1, SF060_04_06=8316, SF061a_04_06=8143, SF061b_04_06=8254, SF055_04_07=2, SF056_04_07=1, SF060_04_07=8578, SF061a_04_07=8165, SF061b_04_07=8293, SF055_04_08=2, SF056_04_08=1, SF060_04_08=8574, SF061a_04_08=8111, SF061b_04_08=8291, SF031_05=4, SF039_05=0, SF040T_05=1, SF040I_05=1, SF041_05=1, SF042_05=1, SF043_05=127, SF044_05=1, SF048_05=212, SF049a_05=252, SF049b_05=252, SF054_05=1, SatBitmaskLen_05=0, SF011_05=70263185, SF055_05_01=1, SF056_05_01=1, SF060_05_01=8852, SF061a_05_01=8116, SF061b_05_01=8187, SF055_05_02=3, SF056_05_02=1, SF060_05_02=9121, SF061a_05_02=8280, SF061b_05_02=8177, SF055_05_03=1, SF056_05_03=1, SF060_05_03=8429, SF061a_05_03=8154, SF061b_05_03=8231, SF055_05_04=4, SF056_05_04=1, SF060_05_04=9253, SF061a_05_04=7982, SF061b_05_04=8172, SF055_05_05=3, SF056_05_05=1, SF060_05_05=9349, SF061a_05_05=8348, SF061b_05_05=8223, SF055_05_06=2, SF056_05_06=1, SF060_05_06=8496, SF061a_05_06=8140, SF061b_05_06=8258, SF055_05_07=1, SF056_05_07=1, SF060_05_07=8882, SF061a_05_07=8077, SF061b_05_07=8305, SF055_05_08=2, SF056_05_08=1, SF060_05_08=8885, SF061a_05_08=8059, SF061b_05_08=8310, SF031_06=5, SF039_06=0, SF040T_06=1, SF040I_06=1, SF041_06=1, SF042_06=1, SF043_06=128, SF044_06=1, SF048_06=210, SF049a_06=256, SF049b_06=259, SF054_06=1, SatBitmaskLen_06=0, SF011_06=70263193, SF055_06_01=4, SF056_06_01=1, SF060_06_01=8967, SF061a_06_01=7934, SF061b_06_01=8256, SF055_06_02=5, SF056_06_02=1, SF060_06_02=9224, SF061a_06_02=8041, SF061b_06_02=8198, SF055_06_03=1, SF056_06_03=1, SF060_06_03=8385, SF061a_06_03=8031, SF061b_06_03=8273, SF055_06_04=4, SF056_06_04=1, SF060_06_04=9426, SF061a_06_04=7732, SF061b_06_04=8242, SF055_06_05=2, SF056_06_05=1, SF060_06_05=9261, SF061a_06_05=8183, SF061b_06_05=8244, SF055_06_06=1, SF056_06_06=1, SF060_06_06=8361, SF061a_06_06=8034, SF061b_06_06=8312, SF055_06_07=3, SF056_06_07=1, SF060_06_07=8615, SF061a_06_07=7988, SF061b_06_07=8339, SF055_06_08=3, SF056_06_08=1, SF060_06_08=9190, SF061a_06_08=8170, SF061b_06_08=8355, SF055_06_09=2, SF056_06_09=1, SF060_06_09=8613, SF061a_06_09=8001, SF061b_06_09=8348, SF031_07=6, SF039_07=0, SF040T_07=1, SF040I_07=1, SF041_07=1, SF042_07=1, SF043_07=128, SF044_07=1, SF048_07=214, SF049a_07=261, SF049b_07=256, SF054_07=1, SatBitmaskLen_07=0, SF011_07=70263193, SF055_07_01=1, SF056_07_01=1, SF060_07_01=9035, SF061a_07_01=7934, SF061b_07_01=8252, SF055_07_02=5, SF056_07_02=1, SF060_07_02=9285, SF061a_07_02=8123, SF061b_07_02=8203, SF055_07_03=2, SF056_07_03=1, SF060_07_03=8504, SF061a_07_03=8023, SF061b_07_03=8265, SF055_07_04=3, SF056_07_04=1, SF060_07_04=9547, SF061a_07_04=7766, SF061b_07_04=8266, SF055_07_05=4, SF056_07_05=1, SF060_07_05=9325, SF061a_07_05=8153, SF061b_07_05=8278, SF055_07_06=1, SF056_07_06=1, SF060_07_06=8532, SF061a_07_06=8010, SF061b_07_06=8300, SF055_07_07=1, SF056_07_07=1, SF060_07_07=8858, SF061a_07_07=7889, SF061b_07_07=8364, SF055_07_08=3, SF056_07_08=1, SF060_07_08=9415, SF061a_07_08=8136, SF061b_07_08=8358, SF055_07_09=1, SF056_07_09=1, SF060_07_09=8851, SF061a_07_09=7945, SF061b_07_09=8362, SF031_08=7, SF039_08=0, SF040T_08=1, SF040I_08=1, SF041_08=1, SF042_08=1, SF043_08=128, SF044_08=1, SF048_08=216, SF049a_08=257, SF049b_08=255, SF054_08=1, SatBitmaskLen_08=0, SF011_08=70263193, SF055_08_01=2, SF056_08_01=1, SF060_08_01=8971, SF061a_08_01=8087, SF061b_08_01=8183, SF055_08_02=4, SF056_08_02=1, SF060_08_02=9137, SF061a_08_02=8169, SF061b_08_02=8166, SF055_08_03=1, SF056_08_03=1, SF060_08_03=8495, SF061a_08_03=8120, SF061b_08_03=8234, SF055_08_04=2, SF056_08_04=1, SF060_08_04=9448, SF061a_08_04=7935, SF061b_08_04=8185, SF055_08_05=4, SF056_08_05=1, SF060_08_05=9315, SF061a_08_05=8318, SF061b_08_05=8232, SF055_08_06=1, SF056_08_06=1, SF060_08_06=8577, SF061a_08_06=8088, SF061b_08_06=8275, SF055_08_07=2, SF056_08_07=1, SF060_08_07=9029, SF061a_08_07=7955, SF061b_08_07=8330, SF055_08_08=3, SF056_08_08=1, SF060_08_08=9561, SF061a_08_08=8306, SF061b_08_08=8337, SF055_08_09=1, SF056_08_09=1, SF060_08_09=9009, SF061a_08_09=8042, SF061b_08_09=8324, SF031_09=8, SF039_09=0, SF040T_09=1, SF040I_09=1, SF041_09=1, SF042_09=2, SF043_09=128, SF044_09=1, SF048_09=202, SF049a_09=254, SF049b_09=256, SF054_09=1, SatBitmaskLen_09=0, SF011_09=70255001, SF055_09_01=6, SF056_09_01=1, SF060_09_01=9089, SF061a_09_01=7822, SF061b_09_01=8192, SF055_09_02=5, SF056_09_02=1, SF060_09_02=9463, SF061a_09_02=7978, SF061b_09_02=8084, SF055_09_03=1, SF056_09_03=1, SF060_09_03=8385, SF061a_09_03=7974, SF061b_09_03=8217, SF055_09_04=4, SF056_09_04=1, SF060_09_04=9243, SF061a_09_04=8184, SF061b_09_04=8207, SF055_09_05=2, SF056_09_05=1, SF060_09_05=8315, SF061a_09_05=8002, SF061b_09_05=8245, SF055_09_06=2, SF056_09_06=1, SF060_09_06=8468, SF061a_09_06=7908, SF061b_09_06=8302, SF055_09_07=4, SF056_09_07=1, SF060_09_07=8961, SF061a_09_07=8257, SF061b_09_07=8259, SF055_09_08=2, SF056_09_08=1, SF060_09_08=8487, SF061a_09_08=7995, SF061b_09_08=8287)>"
        with open(os.path.join(self.dirname, "spartnHPAC.log"), "rb") as stream:
            spr = SPARTNReader(
                stream,
                quitonerror=ERRRAISE,
                decode=True,
                key=SPARTNKEY_HPAC,
            )
            for raw, parsed in spr:
                if raw is not None:
                    # print(parsed)
                    self.assertEqual(str(parsed), EXPECTED_RESULT)

    def testGADLOG(
        self,
    ):  # test decoding of SPARTN GAD message
        EXPECTED_RESULT = "<SPARTN(SPARTN-1X-GAD, msgType=2, nData=50, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=32580, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=63, authInd=1, embAuthLen=0, crc=6182016, SF005=37, SF068=1, SF069=0, SF030=7, SF031_01=32, SF032_01=1332, SF033_01=1987, SF034_01=6, SF035_01=2, SF036_01=5, SF037_01=22, SF031_02=33, SF032_02=1332, SF033_02=2033, SF034_02=6, SF035_02=3, SF036_02=5, SF037_02=16, SF031_03=34, SF032_03=1301, SF033_03=1921, SF034_03=2, SF035_03=6, SF036_03=18, SF037_03=10, SF031_04=35, SF032_04=1297, SF033_04=1987, SF034_04=3, SF035_04=3, SF036_04=12, SF037_04=22, SF031_05=36, SF032_05=1448, SF033_05=1768, SF034_05=6, SF035_05=2, SF036_05=5, SF037_05=30, SF031_06=37, SF032_06=1391, SF033_06=1745, SF034_06=4, SF035_06=7, SF036_06=7, SF037_06=10, SF031_07=38, SF032_07=1360, SF033_07=1906, SF034_07=3, SF035_07=2, SF036_07=8, SF037_07=22)>"
        with open(os.path.join(self.dirname, "spartnGAD.log"), "rb") as stream:
            spr = SPARTNReader(
                stream,
                quitonerror=ERRRAISE,
                decode=True,
                key=SPARTN_KEY_GAD,
                basedate=SPARTN_BASEDATE_GAD,
            )
            for raw, parsed in spr:
                if raw is not None:
                    # print(parsed)
                    self.assertEqual(str(parsed), EXPECTED_RESULT)

    def testOCBLOG(
        self,
    ):  # test decoding of SPARTN OCB GPS message
        EXPECTED_RESULT = (
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=113, eaf=1, crcType=2, frameCrc=4, msgSubtype=0, timeTagtype=0, gnssTimeTag=15160, solutionId=5, solutionProcId=12, encryptionId=2, encryptionSeq=30, authInd=1, embAuthLen=0, crc=12883976, SF005=32, SF010=0, SF069=0, SF008=0, SF009=0, SF016=0, SatBitmaskLen=0, SF011=179065892, SF013_01=0, SF014O_01=1, SF014C_01=1, SF014B_01=0, SF015_01=7, SF018_01=8, SF020R_01=8115, SF020A_01=8680, SF020C_01=8337, SF022_01=7, SF020CK_01=7375, SF024_01=1, SF013_02=0, SF014O_02=1, SF014C_02=1, SF014B_02=0, SF015_02=7, SF018_02=42, SF020R_02=8197, SF020A_02=8493, SF020C_02=8051, SF022_02=7, SF020CK_02=8116, SF024_02=3, SF013_03=0, SF014O_03=1, SF014C_03=1, SF014B_03=0, SF015_03=7, SF018_03=88, SF020R_03=8308, SF020A_03=7615, SF020C_03=7620, SF022_03=7, SF020CK_03=11752, SF024_03=1, SF013_04=0, SF014O_04=1, SF014C_04=1, SF014B_04=0, SF015_04=7, SF018_04=86, SF020R_04=8215, SF020A_04=8026, SF020C_04=8255, SF022_04=7, SF020CK_04=8492, SF024_04=2, SF013_05=0, SF014O_05=1, SF014C_05=1, SF014B_05=0, SF015_05=7, SF018_05=11, SF020R_05=8290, SF020A_05=8074, SF020C_05=8325, SF022_05=7, SF020CK_05=7893, SF024_05=1, SF013_06=0, SF014O_06=1, SF014C_06=1, SF014B_06=0, SF015_06=7, SF018_06=239, SF020R_06=8212, SF020A_06=8926, SF020C_06=7940, SF022_06=7, SF020CK_06=7729, SF024_06=1, SF013_07=0, SF014O_07=1, SF014C_07=1, SF014B_07=0, SF015_07=7, SF018_07=59, SF020R_07=8277, SF020A_07=7902, SF020C_07=8819, SF022_07=7, SF020CK_07=7589, SF024_07=1, SF013_08=0, SF014O_08=1, SF014C_08=1, SF014B_08=0, SF015_08=7, SF018_08=76, SF020R_08=8136, SF020A_08=9025, SF020C_08=8644, SF022_08=7, SF020CK_08=8129, SF024_08=1, SF013_09=0, SF014O_09=1, SF014C_09=1, SF014B_09=0, SF015_09=6, SF018_09=57, SF020R_09=8320, SF020A_09=8725, SF020C_09=8124, SF022_09=7, SF020CK_09=10142, SF024_09=1, SF013_10=0, SF014O_10=1, SF014C_10=1, SF014B_10=0, SF015_10=7, SF018_10=44, SF020R_10=8239, SF020A_10=8278, SF020C_10=8504, SF022_10=7, SF020CK_10=9323, SF024_10=1, SF013_11=0, SF014O_11=1, SF014C_11=1, SF014B_11=0, SF015_11=7, SF018_11=17, SF020R_11=8198, SF020A_11=8335, SF020C_11=8394, SF022_11=7, SF020CK_11=10917, SF024_11=1)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=113, eaf=1, crcType=2, frameCrc=4, msgSubtype=0, timeTagtype=1, gnssTimeTag=431280765, solutionId=5, solutionProcId=12, encryptionId=2, encryptionSeq=31, authInd=1, embAuthLen=0, crc=10830249, SF005=32, SF010=0, SF069=0, SF008=0, SF009=0, SF016=0, SatBitmaskLen=0, SF011=179065892, SF013_01=0, SF014O_01=1, SF014C_01=1, SF014B_01=0, SF015_01=7, SF018_01=8, SF020R_01=8115, SF020A_01=8680, SF020C_01=8337, SF022_01=7, SF020CK_01=7375, SF024_01=1, SF013_02=0, SF014O_02=1, SF014C_02=1, SF014B_02=0, SF015_02=7, SF018_02=42, SF020R_02=8197, SF020A_02=8493, SF020C_02=8051, SF022_02=7, SF020CK_02=8111, SF024_02=3, SF013_03=0, SF014O_03=1, SF014C_03=1, SF014B_03=0, SF015_03=7, SF018_03=88, SF020R_03=8308, SF020A_03=7615, SF020C_03=7620, SF022_03=7, SF020CK_03=11751, SF024_03=1, SF013_04=0, SF014O_04=1, SF014C_04=1, SF014B_04=0, SF015_04=7, SF018_04=86, SF020R_04=8215, SF020A_04=8026, SF020C_04=8255, SF022_04=7, SF020CK_04=8492, SF024_04=2, SF013_05=0, SF014O_05=1, SF014C_05=1, SF014B_05=0, SF015_05=7, SF018_05=11, SF020R_05=8290, SF020A_05=8074, SF020C_05=8325, SF022_05=7, SF020CK_05=7893, SF024_05=1, SF013_06=0, SF014O_06=1, SF014C_06=1, SF014B_06=0, SF015_06=7, SF018_06=239, SF020R_06=8212, SF020A_06=8926, SF020C_06=7940, SF022_06=7, SF020CK_06=7729, SF024_06=1, SF013_07=0, SF014O_07=1, SF014C_07=1, SF014B_07=0, SF015_07=7, SF018_07=59, SF020R_07=8277, SF020A_07=7902, SF020C_07=8819, SF022_07=7, SF020CK_07=7589, SF024_07=1, SF013_08=0, SF014O_08=1, SF014C_08=1, SF014B_08=0, SF015_08=7, SF018_08=76, SF020R_08=8136, SF020A_08=9025, SF020C_08=8644, SF022_08=7, SF020CK_08=8127, SF024_08=1, SF013_09=0, SF014O_09=1, SF014C_09=1, SF014B_09=0, SF015_09=6, SF018_09=57, SF020R_09=8320, SF020A_09=8725, SF020C_09=8124, SF022_09=7, SF020CK_09=10138, SF024_09=1, SF013_10=0, SF014O_10=1, SF014C_10=1, SF014B_10=0, SF015_10=7, SF018_10=44, SF020R_10=8239, SF020A_10=8278, SF020C_10=8504, SF022_10=7, SF020CK_10=9322, SF024_10=1, SF013_11=0, SF014O_11=1, SF014C_11=1, SF014B_11=0, SF015_11=7, SF018_11=17, SF020R_11=8198, SF020A_11=8335, SF020C_11=8394, SF022_11=7, SF020CK_11=10916, SF024_11=1)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=113, eaf=1, crcType=2, frameCrc=4, msgSubtype=0, timeTagtype=0, gnssTimeTag=15170, solutionId=5, solutionProcId=12, encryptionId=2, encryptionSeq=32, authInd=1, embAuthLen=0, crc=6767176, SF005=32, SF010=0, SF069=0, SF008=0, SF009=0, SF016=0, SatBitmaskLen=0, SF011=179065892, SF013_01=0, SF014O_01=1, SF014C_01=1, SF014B_01=0, SF015_01=7, SF018_01=8, SF020R_01=8115, SF020A_01=8680, SF020C_01=8337, SF022_01=7, SF020CK_01=7385, SF024_01=1, SF013_02=0, SF014O_02=1, SF014C_02=1, SF014B_02=0, SF015_02=7, SF018_02=42, SF020R_02=8197, SF020A_02=8493, SF020C_02=8051, SF022_02=7, SF020CK_02=8113, SF024_02=3, SF013_03=0, SF014O_03=1, SF014C_03=1, SF014B_03=0, SF015_03=7, SF018_03=88, SF020R_03=8308, SF020A_03=7615, SF020C_03=7620, SF022_03=7, SF020CK_03=11758, SF024_03=1, SF013_04=0, SF014O_04=1, SF014C_04=1, SF014B_04=0, SF015_04=7, SF018_04=86, SF020R_04=8215, SF020A_04=8026, SF020C_04=8255, SF022_04=7, SF020CK_04=8498, SF024_04=2, SF013_05=0, SF014O_05=1, SF014C_05=1, SF014B_05=0, SF015_05=7, SF018_05=11, SF020R_05=8290, SF020A_05=8074, SF020C_05=8325, SF022_05=7, SF020CK_05=7898, SF024_05=1, SF013_06=0, SF014O_06=1, SF014C_06=1, SF014B_06=0, SF015_06=7, SF018_06=239, SF020R_06=8212, SF020A_06=8926, SF020C_06=7940, SF022_06=7, SF020CK_06=7735, SF024_06=1, SF013_07=0, SF014O_07=1, SF014C_07=1, SF014B_07=0, SF015_07=7, SF018_07=59, SF020R_07=8277, SF020A_07=7902, SF020C_07=8819, SF022_07=7, SF020CK_07=7596, SF024_07=1, SF013_08=0, SF014O_08=1, SF014C_08=1, SF014B_08=0, SF015_08=7, SF018_08=76, SF020R_08=8136, SF020A_08=9025, SF020C_08=8644, SF022_08=7, SF020CK_08=8135, SF024_08=1, SF013_09=0, SF014O_09=1, SF014C_09=1, SF014B_09=0, SF015_09=6, SF018_09=57, SF020R_09=8320, SF020A_09=8725, SF020C_09=8124, SF022_09=7, SF020CK_09=10141, SF024_09=1, SF013_10=0, SF014O_10=1, SF014C_10=1, SF014B_10=0, SF015_10=7, SF018_10=44, SF020R_10=8239, SF020A_10=8278, SF020C_10=8504, SF022_10=7, SF020CK_10=9329, SF024_10=1, SF013_11=0, SF014O_11=1, SF014C_11=1, SF014B_11=0, SF015_11=7, SF018_11=17, SF020R_11=8198, SF020A_11=8335, SF020C_11=8394, SF022_11=7, SF020CK_11=10923, SF024_11=1)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=113, eaf=1, crcType=2, frameCrc=4, msgSubtype=0, timeTagtype=0, gnssTimeTag=15175, solutionId=5, solutionProcId=12, encryptionId=2, encryptionSeq=33, authInd=1, embAuthLen=0, crc=4747921, SF005=32, SF010=0, SF069=0, SF008=0, SF009=0, SF016=0, SatBitmaskLen=0, SF011=179065892, SF013_01=0, SF014O_01=1, SF014C_01=1, SF014B_01=0, SF015_01=7, SF018_01=8, SF020R_01=8115, SF020A_01=8680, SF020C_01=8337, SF022_01=7, SF020CK_01=7382, SF024_01=1, SF013_02=0, SF014O_02=1, SF014C_02=1, SF014B_02=0, SF015_02=7, SF018_02=42, SF020R_02=8197, SF020A_02=8493, SF020C_02=8051, SF022_02=7, SF020CK_02=8108, SF024_02=3, SF013_03=0, SF014O_03=1, SF014C_03=1, SF014B_03=0, SF015_03=7, SF018_03=88, SF020R_03=8308, SF020A_03=7615, SF020C_03=7620, SF022_03=7, SF020CK_03=11755, SF024_03=1, SF013_04=0, SF014O_04=1, SF014C_04=1, SF014B_04=0, SF015_04=7, SF018_04=86, SF020R_04=8215, SF020A_04=8026, SF020C_04=8255, SF022_04=7, SF020CK_04=8496, SF024_04=2, SF013_05=0, SF014O_05=1, SF014C_05=1, SF014B_05=0, SF015_05=7, SF018_05=11, SF020R_05=8290, SF020A_05=8074, SF020C_05=8325, SF022_05=7, SF020CK_05=7896, SF024_05=1, SF013_06=0, SF014O_06=1, SF014C_06=1, SF014B_06=0, SF015_06=7, SF018_06=239, SF020R_06=8212, SF020A_06=8926, SF020C_06=7940, SF022_06=7, SF020CK_06=7733, SF024_06=1, SF013_07=0, SF014O_07=1, SF014C_07=1, SF014B_07=0, SF015_07=7, SF018_07=59, SF020R_07=8277, SF020A_07=7902, SF020C_07=8819, SF022_07=7, SF020CK_07=7596, SF024_07=1, SF013_08=0, SF014O_08=1, SF014C_08=1, SF014B_08=0, SF015_08=7, SF018_08=76, SF020R_08=8136, SF020A_08=9025, SF020C_08=8644, SF022_08=7, SF020CK_08=8135, SF024_08=1, SF013_09=0, SF014O_09=1, SF014C_09=1, SF014B_09=0, SF015_09=6, SF018_09=57, SF020R_09=8320, SF020A_09=8725, SF020C_09=8124, SF022_09=7, SF020CK_09=10134, SF024_09=1, SF013_10=0, SF014O_10=1, SF014C_10=1, SF014B_10=0, SF015_10=7, SF018_10=44, SF020R_10=8239, SF020A_10=8278, SF020C_10=8504, SF022_10=7, SF020CK_10=9327, SF024_10=1, SF013_11=0, SF014O_11=1, SF014C_11=1, SF014B_11=0, SF015_11=7, SF018_11=17, SF020R_11=8198, SF020A_11=8335, SF020C_11=8394, SF022_11=7, SF020CK_11=10921, SF024_11=1)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=262, eaf=1, crcType=2, frameCrc=6, msgSubtype=0, timeTagtype=1, gnssTimeTag=431280780, solutionId=5, solutionProcId=12, encryptionId=2, encryptionSeq=34, authInd=1, embAuthLen=0, crc=1547142, SF005=33, SF010=0, SF069=0, SF008=0, SF009=0, SF016=0, SatBitmaskLen=0, SF011=179065892, SF013_01=0, SF014O_01=1, SF014C_01=1, SF014B_01=1, SF015_01=7, SF018_01=8, SF020R_01=8116, SF020A_01=8679, SF020C_01=8335, SF022_01=7, SF020CK_01=7390, SF024_01=1, PhaseBiasBitmaskLen_01=0, SF025_01=56, SF023_01_01=1, SF015_01_01=7, SF020PB_01_01=8191, SF023_01_02=1, SF015_01_02=7, SF020PB_01_02=8290, SF023_01_03=1, SF015_01_03=7, SF020PB_01_03=8290, CodeBiasBitmaskLen_01=0, SF027_01=56, SF029_01_01=992, SF029_01_02=945, SF029_01_03=960, SF013_02=0, SF014O_02=1, SF014C_02=1, SF014B_02=1, SF015_02=7, SF018_02=42, SF020R_02=8200, SF020A_02=8480, SF020C_02=8051, SF022_02=7, SF020CK_02=8102, SF024_02=2, PhaseBiasBitmaskLen_02=0, SF025_02=56, SF023_02_01=1, SF015_02_01=7, SF020PB_02_01=8191, SF023_02_02=1, SF015_02_02=7, SF020PB_02_02=8539, SF023_02_03=1, SF015_02_03=7, SF020PB_02_03=8539, CodeBiasBitmaskLen_02=0, SF027_02=56, SF029_02_01=900, SF029_02_02=845, SF029_02_03=839, SF013_03=0, SF014O_03=1, SF014C_03=1, SF014B_03=1, SF015_03=7, SF018_03=88, SF020R_03=8308, SF020A_03=7620, SF020C_03=7618, SF022_03=7, SF020CK_03=11757, SF024_03=1, PhaseBiasBitmaskLen_03=0, SF025_03=60, SF023_03_01=1, SF015_03_01=7, SF020PB_03_01=8191, SF023_03_02=1, SF015_03_02=7, SF020PB_03_02=8869, SF023_03_03=1, SF015_03_03=7, SF020PB_03_03=8869, SF023_03_04=1, SF015_03_04=7, SF020PB_03_04=8978, CodeBiasBitmaskLen_03=0, SF027_03=60, SF029_03_01=784, SF029_03_02=841, SF029_03_03=833, SF029_03_04=757, SF013_04=0, SF014O_04=1, SF014C_04=1, SF014B_04=1, SF015_04=7, SF018_04=86, SF020R_04=8216, SF020A_04=8021, SF020C_04=8249, SF022_04=7, SF020CK_04=8505, SF024_04=2, PhaseBiasBitmaskLen_04=0, SF025_04=60, SF023_04_01=1, SF015_04_01=7, SF020PB_04_01=8191, SF023_04_02=1, SF015_04_02=7, SF020PB_04_02=8627, SF023_04_03=1, SF015_04_03=7, SF020PB_04_03=8627, SF023_04_04=1, SF015_04_04=7, SF020PB_04_04=8681, CodeBiasBitmaskLen_04=0, SF027_04=60, SF029_04_01=925, SF029_04_02=923, SF029_04_03=918, SF029_04_04=1016, SF013_05=0, SF014O_05=1, SF014C_05=1, SF014B_05=1, SF015_05=7, SF018_05=11, SF020R_05=8288, SF020A_05=8076, SF020C_05=8323, SF022_05=7, SF020CK_05=7902, SF024_05=1, PhaseBiasBitmaskLen_05=0, SF025_05=48, SF023_05_01=1, SF015_05_01=7, SF020PB_05_01=8191, SF023_05_02=1, SF015_05_02=7, SF020PB_05_02=8463, CodeBiasBitmaskLen_05=0, SF027_05=48, SF029_05_01=931, SF029_05_02=868, SF013_06=0, SF014O_06=1, SF014C_06=1, SF014B_06=1, SF015_06=7, SF018_06=239, SF020R_06=8211, SF020A_06=8923, SF020C_06=7939, SF022_06=7, SF020CK_06=7729, SF024_06=1, PhaseBiasBitmaskLen_06=0, SF025_06=60, SF023_06_01=1, SF015_06_01=7, SF020PB_06_01=8191, SF023_06_02=1, SF015_06_02=7, SF020PB_06_02=8479, SF023_06_03=1, SF015_06_03=7, SF020PB_06_03=8479, SF023_06_04=1, SF015_06_04=7, SF020PB_06_04=8370, CodeBiasBitmaskLen_06=0, SF027_06=60, SF029_06_01=1026, SF029_06_02=1028, SF029_06_03=1026, SF029_06_04=1125, SF013_07=0, SF014O_07=1, SF014C_07=1, SF014B_07=1, SF015_07=7, SF018_07=59, SF020R_07=8277, SF020A_07=7905, SF020C_07=8818, SF022_07=7, SF020CK_07=7596, SF024_07=1, PhaseBiasBitmaskLen_07=0, SF025_07=60, SF023_07_01=1, SF015_07_01=7, SF020PB_07_01=8191, SF023_07_02=1, SF015_07_02=7, SF020PB_07_02=8453, SF023_07_03=1, SF015_07_03=7, SF020PB_07_03=8453, SF023_07_04=1, SF015_07_04=7, SF020PB_07_04=8353, CodeBiasBitmaskLen_07=0, SF027_07=60, SF029_07_01=1027, SF029_07_02=1029, SF029_07_03=1027, SF029_07_04=1119, SF013_08=0, SF014O_08=1, SF014C_08=1, SF014B_08=1, SF015_08=7, SF018_08=76, SF020R_08=8138, SF020A_08=9013, SF020C_08=8637, SF022_08=7, SF020CK_08=8137, SF024_08=1, PhaseBiasBitmaskLen_08=0, SF025_08=48, SF023_08_01=1, SF015_08_01=7, SF020PB_08_01=8191, SF023_08_02=1, SF015_08_02=7, SF020PB_08_02=8190, CodeBiasBitmaskLen_08=0, SF027_08=48, SF029_08_01=1019, SF029_08_02=947, SF013_09=0, SF014O_09=1, SF014C_09=1, SF014B_09=1, SF015_09=6, SF018_09=57, SF020R_09=8320, SF020A_09=8735, SF020C_09=8124, SF022_09=7, SF020CK_09=10139, SF024_09=1, PhaseBiasBitmaskLen_09=0, SF025_09=48, SF023_09_01=1, SF015_09_01=6, SF020PB_09_01=8191, SF023_09_02=1, SF015_09_02=6, SF020PB_09_02=8219, CodeBiasBitmaskLen_09=0, SF027_09=48, SF029_09_01=974, SF029_09_02=1043, SF013_10=0, SF014O_10=1, SF014C_10=1, SF014B_10=1, SF015_10=7, SF018_10=44, SF020R_10=8242, SF020A_10=8271, SF020C_10=8512, SF022_10=7, SF020CK_10=9327, SF024_10=1, PhaseBiasBitmaskLen_10=0, SF025_10=60, SF023_10_01=1, SF015_10_01=7, SF020PB_10_01=8191, SF023_10_02=1, SF015_10_02=7, SF020PB_10_02=8159, SF023_10_03=1, SF015_10_03=7, SF020PB_10_03=8159, SF023_10_04=1, SF015_10_04=7, SF020PB_10_04=8205, CodeBiasBitmaskLen_10=0, SF027_10=60, SF029_10_01=1029, SF029_10_02=1099, SF029_10_03=1099, SF029_10_04=980, SF013_11=0, SF014O_11=1, SF014C_11=1, SF014B_11=1, SF015_11=7, SF018_11=17, SF020R_11=8198, SF020A_11=8338, SF020C_11=8394, SF022_11=7, SF020CK_11=10922, SF024_11=1, PhaseBiasBitmaskLen_11=0, SF025_11=60, SF023_11_01=1, SF015_11_01=7, SF020PB_11_01=8191, SF023_11_02=1, SF015_11_02=7, SF020PB_11_02=8654, SF023_11_03=1, SF015_11_03=7, SF020PB_11_03=8654, SF023_11_04=1, SF015_11_04=7, SF020PB_11_04=8775, CodeBiasBitmaskLen_11=0, SF027_11=60, SF029_11_01=891, SF029_11_02=971, SF029_11_03=974, SF029_11_04=866)>",
        )
        i = 0
        with open(os.path.join(self.dirname, "spartnOCBGPS.log"), "rb") as stream:
            spr = SPARTNReader(
                stream,
                quitonerror=ERRRAISE,
                decode=True,
                key=SPARTN_KEY_OCB,
                basedate=SPARTN_BASEDATE_OCB,
            )

            for raw, parsed in spr:
                if raw is not None:
                    # print(parsed)
                    self.assertEqual(str(parsed), EXPECTED_RESULT[i])
                    i += 1
        self.assertEqual(i, 5)

    def testnullkeyread(
        self,
    ):  # test null decryption key
        EXPECTED_ERROR = "Key must be provided if decoding is enabled"
        with self.assertRaisesRegex(ParameterError, EXPECTED_ERROR):
            i = 0
            spr = SPARTNReader(
                self.streamSPARTN,
                quitonerror=ERRRAISE,
                decode=True,
                key=None,
            )
            for raw, parsed in spr:
                if raw is not None:
                    i += 1

    def testnullkeyparse(
        self,
    ):  # test null decryption key in parse method
        EXPECTED_ERROR = "Key must be provided if decoding is enabled"
        with self.assertRaisesRegex(ParameterError, EXPECTED_ERROR):
            spr = SPARTNReader.parse(
                self.streamSPARTN,
                decode=True,
                key=None,
            )

    def testdatastream(self):  # test serialize()
        spr = SPARTNReader(self.streamSPARTN)
        res = str(spr.datastream)
        # print(res[-17:])
        self.assertEqual(
            res[-17:],
            "spartn_mqtt.log'>",
        )


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
