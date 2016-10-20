#!/usr/bin/env python3

# testIters.py

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


class TestIters (unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testIters(self):

        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.doTestIters(using)

    def doTestIters(self, using_sha):
        check_using_sha(using_sha)
        if using_sha == Q.USING_SHA1:
            REL_PATH_TO_DATA = 'example1/dataDir'
            REL_PATH_TO_NLH = 'example1/example.nlh'
        elif using_sha == Q.USING_SHA2:
            REL_PATH_TO_DATA = 'example2/dataDir'
            REL_PATH_TO_NLH = 'example2/example.nlh'
        elif using_sha == Q.USING_SHA3:
            REL_PATH_TO_DATA = 'example3/dataDir'
            REL_PATH_TO_NLH = 'example3/example.nlh'

        tree = NLHTree.create_from_file_system(REL_PATH_TO_DATA, using_sha)
        self.assertIsNotNone(tree)
        string = tree.__str__()
        if using_sha == Q.USING_SHA1:
            self.assertEqual(EXAMPLE1, string)        # the serialized NLHTree
        elif using_sha == Q.USING_SHA2:
            self.assertEqual(EXAMPLE2, string)        # the serialized NLHTree
        elif using_sha == Q.USING_SHA3:
            self.assertEqual(EXAMPLE3, string)        # the serialized NLHTree
        else:
            raise NotImplementedError

        # The serialized NLHTree, the string s, is identical to the EXAMPLE
        # serialization above.

        # -- tree root ----------------------------------------------
        nodes = tree.nodes
        self.assertIsNotNone(nodes)

        root = tree
        self.assertFalse(isinstance(root, NLHLeaf))
        self.assertTrue(hasattr(root, '__iter__'))
        self.assertTrue(hasattr(root, '__next__'))

        couple = root.__next__()
        self.assertEqual(len(couple), 1)

        # -- leaf node ----------------------------------------------
        node0 = nodes[0]
        self.assertTrue(isinstance(node0, NLHLeaf))
        self.assertTrue(hasattr(node0, '__iter__'))
        self.assertTrue(hasattr(node0, '__next__'))

        couple = node0.__next__()
        self.assertEqual(len(couple), 2)
        self.assertEqual(couple[0], node0.name)
        self.assertEqual(couple[1], node0.hex_hash)

        try:
            couple = node0.__next__()
            self.fail('second __next__ on leaf succeeded')
        except StopIteration:
            pass

        # -- leaf node ----------------------------------------------
        node1 = nodes[1]
        self.assertTrue(isinstance(node1, NLHLeaf))
        self.assertTrue(hasattr(node1, '__iter__'))
        self.assertTrue(hasattr(node1, '__next__'))

        couple = node1.__next__()
        self.assertEqual(len(couple), 2)
        self.assertEqual(couple[0], node1.name)
        self.assertEqual(couple[1], node1.hex_hash)

        try:
            couple = node1.__next__()
            self.fail('second __next__ on leaf succeeded')
        except StopIteration:
            pass

        # -- dir node -----------------------------------------------
        node2 = nodes[2]
        self.assertFalse(isinstance(node2, NLHLeaf))
        self.assertTrue(hasattr(node2, '__iter__'))
        self.assertTrue(hasattr(node2, '__next__'))

        couple = node2.__next__()
        self.assertEqual(len(couple), 1)
        self.assertEqual(couple[0], node2.name)


if __name__ == '__main__':
    unittest.main()
