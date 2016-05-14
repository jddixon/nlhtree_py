#!/usr/bin/env python3

# testIters.py

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


class TestIters (unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testIters(self):
        REL_PATH_TO_DATA = 'example/dataDir'
        REL_PATH_TO_NLH = 'example/example.nlh'

        tree = NLHTree.createFromFileSystem(REL_PATH_TO_DATA, usingSHA1=True)
        self.assertIsNotNone(tree)
        s = tree.__str__()
        self.assertEqual(EXAMPLE, s)        # the serialized NLHTree

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
        self.assertEqual(couple[1], node0.hexHash)

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
        self.assertEqual(couple[1], node1.hexHash)

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
