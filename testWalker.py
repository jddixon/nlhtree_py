#!/usr/bin/env python3
from xlattice import Q    # FIX ME

# testWalker.py

import hashlib
import sys
import unittest

from nlhtree import *

EXAMPLE1 = """dataDir
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

EXAMPLE2 = """dataDir
 data1 93c4feb737c20fa6428f130cf531997c8680f0cf6487d84b2fbafd4bac1f1b69
 data2 c8eda98bb28d17b280e1c5209668ec70788855e2ff2711e16adc087e9bd7f7c1
 subDir1
  data11 2b0fef7f8a1820fbaf01e5649d153a3f01877ca5ade6f8b548da94eac693934f
  data12 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
 subDir2
 subDir3
  data31 a5a2cc9b232d0b0efecbdf7801172da7cd2bc1df301076297e5cb45032ecadde
 subDir4
  subDir41
   subDir411
    data31 6be91186acce7baa87df8f7cc3a57f716fe9864ec928cf0eb27f53c9d427bed6
"""


class TestWalker (unittest.TestCase):

    def setUp(self): pass

    def tearDown(self): pass

    def testSpotCheckTree(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, ]:
            # FIX ME FIX ME
            self.doTestSpotCheckTree(using)

    def doTestSpotCheckTree(self, usingSHA):
        # DEBUG
        print("\nSPOT CHECKS")
        # END
        if usingSHA == Q.USING_SHA1:
            REL_PATH_TO_DATA = 'example1/dataDir'
        else:
            REL_PATH_TO_DATA = 'example2/dataDir'
        tree = NLHTree.createFromFileSystem(REL_PATH_TO_DATA, usingSHA)
        self.assertIsNotNone(tree)
        self.assertEqual(len(tree.nodes), 6)
        self.assertEqual(tree.name, 'dataDir')

        node0 = tree.nodes[0]
        self.assertTrue(isinstance(node0, NLHLeaf))
        self.assertEqual(node0.name, 'data1')

        node1 = tree.nodes[1]
        self.assertTrue(isinstance(node1, NLHLeaf))
        self.assertEqual(node1.name, 'data2')

        node2 = tree.nodes[2]
        self.assertFalse(isinstance(node2, NLHLeaf))
        self.assertEqual(node2.name, 'subDir1')
        self.assertEqual(len(node2.nodes), 2)

        node5 = tree.nodes[5]
        self.assertFalse(isinstance(node5, NLHLeaf))
        self.assertEqual(node5.name, 'subDir4')
        self.assertEqual(len(node5.nodes), 1)

        node50 = node5.nodes[0]
        self.assertFalse(isinstance(node50, NLHLeaf))
        self.assertEqual(node50.name, 'subDir41')
        self.assertEqual(len(node50.nodes), 1)

        node500 = node50.nodes[0]
        self.assertFalse(isinstance(node500, NLHLeaf))
        self.assertEqual(node500.name, 'subDir411')
        self.assertEqual(len(node500.nodes), 1)

        node5000 = node500.nodes[0]
        self.assertTrue(isinstance(node5000, NLHLeaf))
        self.assertEqual(node5000.name, 'data31')

    def testWalkers(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, ]:
            self.doTestWalkers(using)

    def doTestWalkers(self, usingSHA):

        # DEBUG
        print("\ndoTestWalkers, %s" % usingSHA)
        # END

        if usingSHA == Q.USING_SHA1:
            REL_PATH_TO_DATA = 'example1/dataDir'
            REL_PATH_TO_NLH = 'example1/example.nlh'
            EXAMPLE = EXAMPLE1
        else:
            # FIX ME FIX ME
            REL_PATH_TO_DATA = 'example2/dataDir'
            REL_PATH_TO_NLH = 'example2/example.nlh'
            EXAMPLE = EXAMPLE2

        tree = NLHTree.createFromFileSystem(REL_PATH_TO_DATA, usingSHA)
        self.assertIsNotNone(tree)
        s = tree.__str__()
        self.assertEqual(EXAMPLE, s)        # the serialized NLHTree

        # The serialized NLHTree, the string s, is identical to the EXAMPLE1/2
        # serialization above.  So we should be able to walk EXAMPLE1/2,
        # walk the disk file, and walk the in-memory object tree and get
        # the same result.

        fromDisk = []
        fromSS = []
        fromStr = []
        fromObj = []

        # -- walk on-disk representation ----------------------------

        # DEBUG
        print("\nWALK FILE ON DISK")
        sys.stdout.flush()
        # END

        # a couple is a 2-tuple
        for couple in NLHTree.walkFile(REL_PATH_TO_NLH, usingSHA):
            if len(couple) == 1:
                print("    DIR:  %s" % couple[0])
                fromDisk.append(couple)
            elif len(couple) == 2:
                print('    FILE: %s %s' % (couple[0], couple[1]))
                fromDisk.append(couple)
            else:
                print('    unexpected couple of length %d' % len(couple))

        # -- walk list-of-strings representation -------------------

        # DEBUG
        print("\nWALK LIST OF STRINGS")
        sys.stdout.flush()
        # END

        lines = EXAMPLE.split('\n')
        if lines[-1] == '':
            lines = lines[:-1]          # drop last line if blank

        for couple in NLHTree.walkStrings(lines):
            if len(couple) == 1:
                print("    DIR:  %s" % couple[0])
                fromSS.append(couple)
            elif len(couple) == 2:
                print('    FILE: %s %s' % (couple[0], couple[1]))
                fromSS.append(couple)
            else:
                print('    unexpected couple of length %d' % len(couple))

        # -- walk string representation -----------------------------

        # DEBUG
        print("\nWALK STRING")
        sys.stdout.flush()
        # END

        for couple in NLHTree.walkString(EXAMPLE):
            if len(couple) == 1:
                print("    DIR:  %s" % couple[0])
                fromStr.append(couple)
            elif len(couple) == 2:
                print('    FILE: %s %s' % (couple[0], couple[1]))
                fromStr.append(couple)
            else:
                print('    unexpected couple of length %d' % len(couple))

        # -- walk NLHTree object ------------------------------------

        # DEBUG
        print("\nWALK OBJECT")
        sys.stdout.flush()
        hasattr(tree, '__iter__')
        hasattr(tree, '__next__')
        # END

        for couple in tree:
            if len(couple) == 1:
                print("        DIR:  %s" % couple[0])
                fromObj.append(couple)
            elif len(couple) == 2:
                print('        FILE: %s %s' % (couple[0], couple[1]))
                fromObj.append(couple)
            else:
                print('        unexpected couple of length %d' % len(couple))

        # -- verify the lists are identical -------------------------

        # DEBUG
        print("\nIDENTITY CHECKS")
        sys.stdout.flush()
        # END

        def compareLists(a, b):
            # a and b are lists of tuples
            self.assertEqual(len(a), len(b))
            for n in range(len(a)):
                self.assertEqual(a[n], b[n])

        # DEBUG
        print("FROM_DISK:")
        for i in fromDisk:
            if len(i) == 1:
                print("  %s" % (i[0]))
            else:
                print("  %s %s" % (i[0], i[1]))

        print("FROM_SS:")
        for i in fromSS:
            if len(i) == 1:
                print("  %s" % (i[0]))
            else:
                print("  %s %s" % (i[0], i[1]))
        # END

        compareLists(fromDisk, fromSS)

        # DEBUG
        print("\ncomparing fromDisk, fromStr")
        # END
        compareLists(fromDisk, fromStr)

        # DEBUG
        print("\ncomparing fromDisk, fromObj")
        # END
        compareLists(fromDisk, fromObj)

        # -- verify that the operations are reversible, that you can
        # recover the dataDir from the listings ---------------------

        # XXX NOT YET IMPLEMENTED XXX

if __name__ == '__main__':
    unittest.main()
