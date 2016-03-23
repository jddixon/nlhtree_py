#!/usr/bin/python3

# testNLHTree3.py
import hashlib
import re
import time
import unittest

from rnglib import SimpleRNG
from nlhtree import NLHTree as NT
from xlattice import (
    SHA1_BIN_LEN, SHA2_BIN_LEN,
    SHA1_HEX_LEN, SHA2_HEX_LEN)
from xlattice.crypto import SP


class TestNLHTree3 (unittest.TestCase):

    # adapted from the buildList example 2015-05-22
    EXAMPLE1 = [
        'dataDir',
        ' data1 bea7383743859a81b84cec8fde2ccd1f3e2ff688',
        ' data2 895c210f5203c48c1e3a574a2d5eba043c0ec72d',
        ' subDir1',
        '  data11 cb0ece05cbb91501d3dd78afaf362e63816f6757',
        '  data12 da39a3ee5e6b4b0d3255bfef95601890afd80709',
        ' subDir2',
        ' subDir3',
        '  data31 8cddeb23f9de9da4547a0d5adcecc7e26cb098c0',
        ' subDir4',
        '  subDir41',
        '   subDir411',
        '    data41 31c16def9fc4a4b6415b0b133e156a919cf41cc8',
        ' zData 31c16def9fc4a4b6415b0b133e156a919cf41cc8',
    ]
    # this is just a hack but ...
    EXAMPLE2 = [
        'dataDir',
        ' data1 012345678901234567890123bea7383743859a81b84cec8fde2ccd1f3e2ff688',
        ' data2 012345678901234567890123895c210f5203c48c1e3a574a2d5eba043c0ec72d',
        ' subDir1',
        '  data11 012345678901234567890123cb0ece05cbb91501d3dd78afaf362e63816f6757',
        '  data12 012345678901234567890123da39a3ee5e6b4b0d3255bfef95601890afd80709',
        ' subDir2',
        ' subDir3',
        '  data31 0123456789012345678901238cddeb23f9de9da4547a0d5adcecc7e26cb098c0',
        ' subDir4',
        '  subDir41',
        '   subDir411',
        '    data41 01234567890123456789012331c16def9fc4a4b6415b0b133e156a919cf41cc8',
        ' zData 01234567890123456789012331c16def9fc4a4b6415b0b133e156a919cf41cc8',
    ]

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def doTestPatternMatching(self, usingSHA1):
        if usingSHA1:
            ss = self.EXAMPLE1
        else:
            ss = self.EXAMPLE2

        # first line --------------------------------------
        m = NT.DIR_LINE_RE.match(ss[0])
        self.assertTrue(m)
        self.assertEqual(len(m.group(1)), 0)
        self.assertEqual(m.group(2), 'dataDir')

        # simpler approach ----------------------
        name = NT.parseFirstLine(ss[0])
        self.assertEqual(name, 'dataDir')

        # file with indent of 1 ---------------------------
        if usingSHA1:
            m = NT.FILE_LINE_RE_1.match(ss[1])
        else:
            m = NT.FILE_LINE_RE_2.match(ss[1])
        self.assertTrue(m)
        self.assertEqual(len(m.group(1)), 1)
        self.assertEqual(m.group(2), 'data1')

        # that simpler approach -----------------
        indent, name, hash = NT.parseOtherLine(ss[1])
        self.assertEqual(indent, 1)
        self.assertEqual(name, 'data1')
        if usingSHA1:
            self.assertEqual(len(hash), SHA1_HEX_LEN)
        else:
            self.assertEqual(len(hash), SHA2_HEX_LEN)

        # subdirectory ------------------------------------
        m = NT.DIR_LINE_RE.match(ss[3])
        self.assertTrue(m)
        self.assertEqual(len(m.group(1)), 1)
        self.assertEqual(m.group(2), 'subDir1')

        # that simpler approach -----------------
        indent, name, hash = NT.parseOtherLine(ss[3])
        self.assertEqual(indent, 1)
        self.assertEqual(name, 'subDir1')
        self.assertEqual(hash, None)

        # lower level file ----------------------
        if usingSHA1:
            m = NT.FILE_LINE_RE_1.match(ss[12])
        else:
            m = NT.FILE_LINE_RE_2.match(ss[12])
        self.assertTrue(m)
        self.assertEqual(len(m.group(1)), 4)
        self.assertEqual(m.group(2), 'data41')

        # that simpler approach -----------------
        indent, name, hash = NT.parseOtherLine(ss[12])
        self.assertEqual(indent, 4)
        self.assertEqual(name, 'data41')
        if usingSHA1:
            self.assertEqual(len(hash), SHA1_HEX_LEN)
        else:
            self.assertEqual(len(hash), SHA2_HEX_LEN)

    def testPatternMatching(self):
        self.doTestPatternMatching(usingSHA1=True)
        self.doTestPatternMatching(usingSHA1=False)

    def doTestSerialization(self, usingSHA1):
        if usingSHA1:
            tree = NT.createFromStringArray(self.EXAMPLE1, usingSHA1)
        else:
            tree = NT.createFromStringArray(self.EXAMPLE2, usingSHA1)
        self.assertEqual(tree.usingSHA1, usingSHA1)

        ss = []
        tree.toStrings(ss, 0)

        tree2 = NT.createFromStringArray(ss, usingSHA1)
        self.assertEqual(tree, tree2)

        s = '\n'.join(ss) + '\n'
        tree3 = NT.parse(s, usingSHA1)
        s3 = tree3.__str__()

        self.assertEqual(s3, s)
        self.assertEqual(tree3, tree)

    def testSerialization(self):
        self.doTestSerialization(usingSHA1=True)
        self.doTestSerialization(usingSHA1=False)


if __name__ == '__main__':
    unittest.main()
