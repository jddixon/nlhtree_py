#!/usr/bin/env python3

# testWalker.py

import hashlib
import time
import unittest

from nlhtree import *

EXAMPLE="""dataDir
 data1 34463aa26c4d7214a96e6e42c3a9e8f55727c695
 data2 14193743b265973e5824ca5257eef488094e19e9
 subDir1
  data11 58089ce970b65940dd5bf07703cd81b4306cb8f0
  data12 da39a3ee5e6b4b0d3255bfef95601890afd80709
 subDir2
 subDir3
  data31 487607ec22ee1255cc31c35506c64b1819a48090
 subDir4
  subDir41
   subDir411
    data31 0b57d3ab229a69ce5f7fad62f9fe654fe96c51bb
"""

class TestWalker (unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def testWalker(self):
        REL_PATH_TO_DATA = 'example/dataDir'
        tree = NLHTree.createFromFileSystem(REL_PATH_TO_DATA, usingSHA1=True)
        self.assertIsNotNone(tree)
        s    = tree.__str__()
        self.assertEqual(EXAMPLE, s)

        # The serialized NLHTree, the string s, is identical to the EXAMPLE 
        # serialization above.  So we should be able to walk EXAMPLE, 
        # walk the disk file, and walk the in-memory object tree and get
        # the same result.

        fromEX   = []
        fromDisk = []
        fromObj  = []

        # a couple is a 2-tuple

if __name__ == '__main__':
    unittest.main()
