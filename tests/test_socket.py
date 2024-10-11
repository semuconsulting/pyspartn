"""
Socket reader tests for pyspartn - uses dummy socket class
to achieve 99% test coverage of SocketWrapper.

Created on 11 May 2022

*** NB: must be saved in UTF-8 format ***

:author: semuadmin
"""

import unittest
from socket import socket

from pyspartn.spartnreader import SPARTNReader


class DummySocket(socket):
    """
    Dummy socket class which simulates recv() method
    and TimeoutError.
    """

    def __init__(self, *args, **kwargs):
        self._timeout = False
        if "timeout" in kwargs:
            self._timeout = kwargs["timeout"]
            kwargs.pop("timeout")

        super().__init__(*args, **kwargs)

        pool = (
            b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad"
            + b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad"
            + b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad"
            + b"s\x00\x12\xe2\x00|\x10[\x12H\xf5\t\xa0\xb4+\x99\x02\x15\xe2\x05\x85\xb7\x83\xc5\xfd\x0f\xfe\xdf\x18\xbe\x7fv \xc3`\x82\x98\x10\x07\xdc\xeb\x82\x7f\xcf\xf8\x9e\xa3ta\xad"
        )
        self._stream = pool * round(4096 / len(pool))
        self._buffer = self._stream

    def __enter__(self):
        """
        Context manager enter routine.
        """

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """
        Context manager exit routine.
        """

        self.close()

    def recv(self, num: int) -> bytes:
        if self._timeout:
            raise TimeoutError
        if len(self._buffer) < num:
            self._buffer = self._buffer + self._stream
        buff = self._buffer[:num]
        self._buffer = self._buffer[num:]
        return buff


class SocketTest(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def tearDown(self):
        pass

    # *******************************************
    # Helper methods
    # *******************************************

    def testSocketStub(self):
        EXPECTED_RESULTS = (
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=9, authInd=1, embAuthLen=0, crc=7627181)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=9, authInd=1, embAuthLen=0, crc=7627181)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=9, authInd=1, embAuthLen=0, crc=7627181)>",
            "<SPARTN(SPARTN-1X-OCB-GPS, msgType=0, nData=37, eaf=1, crcType=2, frameCrc=2, msgSubtype=0, timeTagtype=0, gnssTimeTag=3970, solutionId=5, solutionProcId=11, encryptionId=1, encryptionSeq=9, authInd=1, embAuthLen=0, crc=7627181)>",
        )
        raw = None
        with DummySocket() as stream:
            spr = SPARTNReader(stream, bufsize=512)
            buff = spr._stream.buffer  # test buffer getter method
            i = 0
            for raw, parsed in spr:
                if raw is not None:
                    # print(f'"{parsed}",')
                    self.assertEqual(str(parsed), EXPECTED_RESULTS[i])
                    i += 1
                    if i >= 4:
                        break
        self.assertEqual(i, 4)

    def testSocketIter(self):  # test for extended stream
        raw = None
        with DummySocket() as stream:
            spr = SPARTNReader(stream)
            i = 0
            for raw, parsed in spr:
                if raw is None:
                    raise EOFError
                i += 1
                if i >= 123:
                    break
        self.assertEqual(i, 123)

    def testSocketError(self):  # test for simulated socket timeout
        raw = None
        with DummySocket(timeout=True) as stream:
            spr = SPARTNReader(stream)
            i = 0
            for raw, parsed in spr:
                i += 1
                if i >= 4:
                    break
        self.assertEqual(i, 0)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
