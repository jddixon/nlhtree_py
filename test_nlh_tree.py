#!/usr/bin/env python3
# testNLHTree.py

""" Test NLHTree-related functions. """

import sys
import time
import unittest

import hashlib
if sys.version_info < (3, 6):
    # pylint: disable=unused-import
    import sha3     # monkey-patches hashlib

from rnglib import SimpleRNG
from nlhtree import *
from xlattice import Q, check_using_sha


class TestNLHTree (unittest.TestCase):
    """ Test NLHTree-related functions. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################
    def make_leaf(self, names_so_far, using_sha):
        while True:
            name = self.rng.next_file_name(8)
            if name not in names_so_far:
                names_so_far.add(name)
                break
        n = self.rng.someBytes(8)        # 8 quasi-random bytes
        if using_sha == Q.USING_SHA1:
            sha = hashlib.sha1()
        elif using_sha == Q.USING_SHA2:
            sha = hashlib.sha256()
        elif using_sha == Q.USING_SHA3:
            sha = hashlib.sha3_256()
        sha.update(n)
        return NLHLeaf(name, sha.digest(), using_sha)

    # actual unit tests #############################################
    def test_simple_constructor(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_simple_constructor(using)

    def do_test_simple_constructor(self, using_sha):
        name = self.rng.next_file_name(8)
        tree = NLHTree(name, using_sha)
        self.assertEqual(tree.name, name)
        self.assertEqual(tree.using_sha, using_sha)
        self.assertEqual(len(tree.nodes), 0)

    def do_test_insert_4_leafs(self, using_sha):
        """
        Create 4 leaf nodes with random but unique names.  Insert
        them into a tree, verifying that the resulting sort is correct.
        """
        check_using_sha(using_sha)
        if using_sha == Q.USING_SHA1:
            sha = hashlib.sha1()
        elif using_sha == Q.USING_SHA2:
            sha = hashlib.sha256()
        elif using_sha == Q.USING_SHA3:
            sha = hashlib.sha3_256()
        name = self.rng.next_file_name(8)
        tree = NLHTree(name, using_sha)
        leaf_names = set()
        aVal = self.make_leaf(leaf_names, using_sha)
        bVal = self.make_leaf(leaf_names, using_sha)
        cVal = self.make_leaf(leaf_names, using_sha)
        dVal = self.make_leaf(leaf_names, using_sha)
        self.assertEqual(len(tree.nodes), 0)
        tree.insert(aVal)
        self.assertEqual(len(tree.nodes), 1)
        tree.insert(bVal)
        self.assertEqual(len(tree.nodes), 2)
        tree.insert(cVal)
        self.assertEqual(len(tree.nodes), 3)
        tree.insert(dVal)
        self.assertEqual(len(tree.nodes), 4)
        # we expect the nodes to be sorted
        for i in range(3):
            self.assertTrue(tree.nodes[i].name < tree.nodes[i + 1].name)

        matches = tree.list('*')
        for ndx, q in enumerate(tree.nodes):
            self.assertEqual(matches[ndx], '  ' + q.name)

        self.assertEqual(tree, tree)
        tree2 = tree.clone()
        self.assertEqual(tree2, tree)

    def test_insert_4_leafs(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_insert_4_leafs(using)


if __name__ == '__main__':
    unittest.main()
