#!/usr/bin/env python3
# testNLHTree3.py

""" Test more NLHTree functionality. """

import hashlib
import re
import time
import unittest

from rnglib import SimpleRNG
from nlhtree import NLHTree as NT
from xlattice import (Q, check_using_sha,
                      SHA1_BIN_LEN, SHA2_BIN_LEN, SHA3_BIN_LEN,
                      SHA1_HEX_LEN, SHA2_HEX_LEN, SHA3_HEX_LEN)
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
    EXAMPLE3 = [
        'dataDir',
        ' data1 6d57759cf499a8ff7762a10043548f22513ed83456452332a8abd4b59d7e9203',
        ' data2 dacbf5c11f4ddbd1277ecbc304e09967d3124148560f82634d3912db8b4bd547',
        ' subDir1',
        '  data11 fb47958129f261f65c1655002ff5f9806bc969283ad772af5e8caaf214a9ed72',
        '  data12 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
        ' subDir2',
        ' subDir3',
        '  data31 7659fb836a76fb3f3369e1a4ca247104220e4778d5862e38a123e10f02520e87',
        ' subDir4',
        '  subDir41',
        '   subDir411',
        '    data41 00bb6d0864cb4952a0c41cbea65cf09de41e00fc6fa1011a27c5dd8814c98175',
    ]

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def do_test_pattern_matching(self, using_sha):
        check_using_sha(using_sha)
        if using_sha == Q.USING_SHA1:
            ss = self.EXAMPLE1
        elif using_sha == Q.USING_SHA2:
            ss = self.EXAMPLE2
        elif using_sha == Q.USING_SHA3:
            ss = self.EXAMPLE3

        # first line --------------------------------------
        m = NT.DIR_LINE_RE.match(ss[0])
        self.assertTrue(m)
        self.assertEqual(len(m.group(1)), 0)
        self.assertEqual(m.group(2), 'dataDir')

        # simpler approach ----------------------
        name = NT.parse_first_line(ss[0])
        self.assertEqual(name, 'dataDir')

        # file with indent of 1 ---------------------------
        if using_sha == Q.USING_SHA1:
            m = NT.FILE_LINE_RE_1.match(ss[1])
        else:
            # XXX This works for both SHA2 and SHA3
            m = NT.FILE_LINE_RE_2.match(ss[1])
        self.assertTrue(m)
        self.assertEqual(len(m.group(1)), 1)
        self.assertEqual(m.group(2), 'data1')

        # that simpler approach -----------------
        indent, name, hash = NT.parse_other_line(ss[1])
        self.assertEqual(indent, 1)
        self.assertEqual(name, 'data1')
        if using_sha == Q.USING_SHA1:
            self.assertEqual(len(hash), SHA1_HEX_LEN)
        else:
            # XXX This works for both SHA2 and SHA 3
            self.assertEqual(len(hash), SHA2_HEX_LEN)

        # subdirectory ------------------------------------
        m = NT.DIR_LINE_RE.match(ss[3])
        self.assertTrue(m)
        self.assertEqual(len(m.group(1)), 1)
        self.assertEqual(m.group(2), 'subDir1')

        # that simpler approach -----------------
        indent, name, hash = NT.parse_other_line(ss[3])
        self.assertEqual(indent, 1)
        self.assertEqual(name, 'subDir1')
        self.assertEqual(hash, None)

        # lower level file ----------------------
        if using_sha == Q.USING_SHA1:
            m = NT.FILE_LINE_RE_1.match(ss[12])
        else:
            # XXX This works for both SHA2 and SHA 3
            m = NT.FILE_LINE_RE_2.match(ss[12])
        self.assertTrue(m)
        self.assertEqual(len(m.group(1)), 4)
        self.assertEqual(m.group(2), 'data41')

        # that simpler approach -----------------
        indent, name, hash = NT.parse_other_line(ss[12])
        self.assertEqual(indent, 4)
        self.assertEqual(name, 'data41')
        if using_sha == Q.USING_SHA1:
            self.assertEqual(len(hash), SHA1_HEX_LEN)
        else:
            # XXX This works for both SHA2 and SHA 3
            self.assertEqual(len(hash), SHA2_HEX_LEN)

    def test_pattern_matching(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_pattern_matching(using)

    def do_test_serialization(self, using_sha):
        check_using_sha(using_sha)
        tree = NT.create_from_string_array(self.EXAMPLE1, using_sha)
        self.assertEqual(tree.using_sha, using_sha)

        ss = []
        tree.toStrings(ss, 0)

        tree2 = NT.create_from_string_array(ss, using_sha)
        self.assertEqual(tree, tree2)

        s = '\n'.join(ss) + '\n'
        tree3 = NT.parse(s, using_sha)
        s3 = tree3.__str__()

        self.assertEqual(s3, s)
        self.assertEqual(tree3, tree)

        dupe3 = tree3.clone()
        self.assertEqual(dupe3, tree3)

    def test_serialization(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_serialization(using)


if __name__ == '__main__':
    unittest.main()
