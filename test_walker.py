#!/usr/bin/env python3

# testWalker.py

import sys
import unittest

import hashlib
if sys.version_info < (3, 6):
    # pylint: disable=unused-import
    import sha3     # monkey-patches hashlib

from xlattice import Q, check_using_sha
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
 data1 023d6598659f6a6b044ee909f3f3e6c4343850a1c5c71ef3f873c8e46b68e898
 data2 29223e6e7c63529feaa441773097b68951fe8652830098b3c5c2df72fd5b7821
 subDir1
  data11 9394e20adb8adf9727ee6d12377aa57230eb548eb2c718d117c2e9c3aecf0e33
  data12 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
 subDir2
 subDir3
  data31 9adc17b1d861fae64ddbc792fafb097c55d316a585359b6356af8fa8992aefac
 subDir4
  subDir41
   subDir411
    data31 4308da851a73798454e22ee6d71a4d0732b9fd1ab10e607da53bf8c88ad7d44b
"""

EXAMPLE3 = """dataDir
 data1 adf6c7f792e8198631aacbbc8cee51181176f4c157d578ee226040d70f552db1
 data2 c6e5bfc9f7189ef6276d0bf25f05c12c0e1dcdf10e1ac69f62a0642e9d7dfcc5
 subDir1
  data11 03ef2f36e12e9afaaabb71fe84c6db3a225714bfa0bd58440727932e23174886
  data12 a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a
 subDir2
 subDir3
  data31 9400dfa37b52665f2056c93071a851a5e4c3c2c9245d39c640d9de796fa3d530
 subDir4
  subDir41
   subDir411
    data31 360ba73957c140fc28b8d6a8b7033cd2f896158fc8988fc68bb4877e4e13a048
"""


class TestWalker (unittest.TestCase):

    def setUp(self): pass

    def tearDown(self): pass

    def testSpotCheckTree(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.doTestSpotCheckTree(using)

    def doTestSpotCheckTree(self, using_sha):
        check_using_sha(using_sha)

        # DEBUG
        #print("\nSPOT CHECKS")
        # END
        if using_sha == Q.USING_SHA1:
            REL_PATH_TO_DATA = 'example1/dataDir'
        else:
            REL_PATH_TO_DATA = 'example2/dataDir'
        tree = NLHTree.create_from_file_system(REL_PATH_TO_DATA, using_sha)
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

    def doTestWalkers(self, using_sha):

        # DEBUG
        # print("\ndoTestWalkers, %s" % using_sha)
        # END

        check_using_sha(using_sha)
        if using_sha == Q.USING_SHA1:
            REL_PATH_TO_DATA = 'example1/dataDir'
            REL_PATH_TO_NLH = 'example1/example.nlh'
            EXAMPLE = EXAMPLE1
        elif using_sha == Q.USING_SHA2:
            REL_PATH_TO_DATA = 'example2/dataDir'
            REL_PATH_TO_NLH = 'example2/example.nlh'
            EXAMPLE = EXAMPLE2
        elif using_sha == Q.USING_SHA3:
            REL_PATH_TO_DATA = 'example3/dataDir'
            REL_PATH_TO_NLH = 'example3/example.nlh'
            EXAMPLE = EXAMPLE3

        tree = NLHTree.create_from_file_system(REL_PATH_TO_DATA, using_sha)
        self.assertIsNotNone(tree)
        string = tree.__str__()
        self.assertEqual(EXAMPLE, string)        # the serialized NLHTree

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
        # print("\nWALK FILE ON DISK")
        # sys.stdout.flush()
        # END

        # a couple is a 2-tuple
        for couple in NLHTree.walkFile(REL_PATH_TO_NLH, using_sha):
            if len(couple) == 1:
                # print("    DIR:  %s" % couple[0])       # DEBUG
                fromDisk.append(couple)
            elif len(couple) == 2:
                # print('    FILE: %s %s' % (couple[0], couple[1])) # DEBUG
                fromDisk.append(couple)
            else:
                print('    unexpected couple of length %d' % len(couple))

        # -- walk list-of-strings representation -------------------

        lines = EXAMPLE.split('\n')
        if lines[-1] == '':
            lines = lines[:-1]          # drop last line if blank

        # DEBUG
        # print("\nWALK LIST OF STRINGS; %s; there are %d lines" % (
        #    using_sha, len(lines)))
        # sys.stdout.flush()
        # END

        for couple in NLHTree.walkStrings(lines, using_sha):
            if len(couple) == 1:
                # print("    DIR:  %s" % couple[0])     # DEBUG
                fromSS.append(couple)
            elif len(couple) == 2:
                # print('    FILE: %s %s' % (couple[0], couple[1])) # DEBUG
                fromSS.append(couple)
            else:
                print('    unexpected couple of length %d' % len(couple))

        # -- walk string representation -----------------------------

        # DEBUG
        #print("\nWALK STRING")
        # sys.stdout.flush()
        # END

        for couple in NLHTree.walkString(EXAMPLE, using_sha):
            if len(couple) == 1:
                # print("    DIR:  %s" % couple[0])     # DEBUG
                fromStr.append(couple)
            elif len(couple) == 2:
                # print('    FILE: %s %s' % (couple[0], couple[1])) # DEBUG
                fromStr.append(couple)
            else:
                print('    unexpected couple of length %d' % len(couple))

        # -- walk NLHTree object ------------------------------------

        # DEBUG
        #print("\nWALK OBJECT")
        # sys.stdout.flush()
        #hasattr(tree, '__iter__')
        #hasattr(tree, '__next__')
        # END

        for couple in tree:
            if len(couple) == 1:
                # print("        DIR:  %s" % couple[0])     # DEBUG
                fromObj.append(couple)
            elif len(couple) == 2:
                # print('        FILE: %s %s' % (couple[0], couple[1])) # DEBUG
                fromObj.append(couple)
            else:
                print('        unexpected couple of length %d' % len(couple))

        # -- verify the lists are identical -------------------------

        # DEBUG
        #print("\nIDENTITY CHECKS %s" % using_sha)
        # sys.stdout.flush()
        # END

        def compareLists(aVal, bVal):
            # a and b are lists of tuples
            self.assertEqual(len(aVal), len(bVal))
            for n in range(len(aVal)):
                self.assertEqual(aVal[n], bVal[n])

        # DEBUG
#       #print("FROM_DISK:")
#       for i in fromDisk:
#           if len(i) == 1:
#               print("  %s" % (i[0]))
#           else:
#               print("  %s %s" % (i[0], i[1]))

#       print("FROM_SS:")
#       for i in fromSS:
#           if len(i) == 1:
#               print("  %s" % (i[0]))
#           else:
#               print("  %s %s" % (i[0], i[1]))
        # END

        compareLists(fromDisk, fromSS)

        # DEBUG
        #print("\ncomparing fromDisk, fromStr")
        # END
        compareLists(fromDisk, fromStr)

        # DEBUG
        #print("\ncomparing fromDisk, fromObj")
        # END
        compareLists(fromDisk, fromObj)

        # -- verify that the operations are reversible, that you can
        # recover the dataDir from the listings ---------------------

        # XXX NOT YET IMPLEMENTED XXX

if __name__ == '__main__':
    unittest.main()
