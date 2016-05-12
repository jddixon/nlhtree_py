#!/usr/bin/env python3

# testWalker.py

import hashlib
import sys
import unittest

from nlhtree import *

EXAMPLE = """dataDir
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

    def testSpotCheckTree(self):
        # DEBUG
        #print("\nSPOT CHECKS")
        # END
        REL_PATH_TO_DATA = 'example/dataDir'
        tree = NLHTree.createFromFileSystem(REL_PATH_TO_DATA, usingSHA1=True)
        self.assertIsNotNone(tree)
        self.assertEqual(len(tree.nodes), 6)
        self.assertEqual(tree.name, 'dataDir')

        node0 = tree.nodes[0]
        self.assertTrue(node0.isLeaf)
        self.assertEqual(node0.name, 'data1')

        node1 = tree.nodes[1]
        self.assertTrue(node1.isLeaf)
        self.assertEqual(node1.name, 'data2')

        node2 = tree.nodes[2]
        self.assertFalse(node2.isLeaf)
        self.assertEqual(node2.name, 'subDir1')
        self.assertEqual(len(node2.nodes), 2)

        node5 = tree.nodes[5]
        self.assertFalse(node5.isLeaf)
        self.assertEqual(node5.name, 'subDir4')
        self.assertEqual(len(node5.nodes), 1)

        node50 = node5.nodes[0]
        self.assertFalse(node50.isLeaf)
        self.assertEqual(node50.name, 'subDir41')
        self.assertEqual(len(node50.nodes), 1)

        node500 = node50.nodes[0]
        self.assertFalse(node500.isLeaf)
        self.assertEqual(node500.name, 'subDir411')
        self.assertEqual(len(node500.nodes), 1)

        node5000 = node500.nodes[0]
        self.assertTrue(node5000.isLeaf)
        self.assertEqual(node5000.name, 'data31')

    def testWalkers(self):
        REL_PATH_TO_DATA = 'example/dataDir'
        REL_PATH_TO_NLH = 'example/example.nlh'

        tree = NLHTree.createFromFileSystem(REL_PATH_TO_DATA, usingSHA1=True)
        self.assertIsNotNone(tree)
        s = tree.__str__()
        self.assertEqual(EXAMPLE, s)        # the serialized NLHTree

        # The serialized NLHTree, the string s, is identical to the EXAMPLE
        # serialization above.  So we should be able to walk EXAMPLE,
        # walk the disk file, and walk the in-memory object tree and get
        # the same result.

        fromDisk = []
        fromSS = []
        fromStr = []
        fromObj = []

        # -- walk on-disk representation ----------------------------

        # DEBUG
        #print("\nWALK FILE ON DISK")
        sys.stdout.flush()
        # END

        # a couple is a 2-tuple
        for couple in NLHTree.walkFile(REL_PATH_TO_NLH):
            if len(couple) == 1:
                #print("    DIR:  %s" % couple[0])
                fromDisk.append(couple)
            elif len(couple) == 2:
                #print('    FILE: %s %s' % (couple[0], couple[1]))
                fromDisk.append(couple)
            else:
                print('    unexpected couple of length %d' % len(couple))

        # -- walk list-of-strings representation -------------------

        # DEBUG
        #print("\nWALK LIST OF STRINGS")
        sys.stdout.flush()
        # END

        lines = EXAMPLE.split('\n')
        if lines[-1] == '':
            lines = lines[:-1]          # drop last line if blank

        for couple in NLHTree.walkStrings(lines):
            if len(couple) == 1:
                #print("    DIR:  %s" % couple[0])
                fromSS.append(couple)
            elif len(couple) == 2:
                #print('    FILE: %s %s' % (couple[0], couple[1]))
                fromSS.append(couple)
            else:
                print('    unexpected couple of length %d' % len(couple))

        # -- walk string representation -----------------------------

        # DEBUG
        #print("\nWALK STRING")
        sys.stdout.flush()
        # END

        for couple in NLHTree.walkString(EXAMPLE):
            if len(couple) == 1:
                #print("    DIR:  %s" % couple[0])
                fromStr.append(couple)
            elif len(couple) == 2:
                #print('    FILE: %s %s' % (couple[0], couple[1]))
                fromStr.append(couple)
            else:
                print('    unexpected couple of length %d' % len(couple))

        # -- walk NLHTree object ------------------------------------

        # DEBUG
        #print("\nWALK OBJECT")
        sys.stdout.flush()
        hasattr(tree, '__iter__')
        hasattr(tree, '__next__')
        # END

        for couple in tree:
            if len(couple) == 1:
                #print("        DIR:  %s" % couple[0])
                fromObj.append(couple)
            elif len(couple) == 2:
                #print('        FILE: %s %s' % (couple[0], couple[1]))
                fromObj.append(couple)
            else:
                print('        unexpected couple of length %d' % len(couple))

        # -- verify the lists are identical -------------------------

        # DEBUG
        #print("\nIDENTITY CHECKS")
        sys.stdout.flush()
        # END

        def check(a, b):
            # a and b are lists of tuples
            self.assertEqual(len(a), len(b))
            for n in range(len(a)):
                self.assertEqual(a[n], b[n])

        # DEBUG
        #print("\ncomparing fromDisk, fromSS")
        # END
        check(fromDisk, fromSS)

        # DEBUG
        #print("\ncomparing fromDisk, fromStr")
        # END
        #check(fromDisk, fromStr)

        # DEBUG
        #print("\ncomparing fromDisk, fromObj")
        # END
        check(fromDisk, fromObj)

        # -- verify that the operations are reversible, that you can
        # recover the dataDir from the listings ---------------------

        # XXX NOT YET IMPLEMENTED XXX

if __name__ == '__main__':
    unittest.main()
