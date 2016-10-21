#!/usr/bin/env python3
# testNLHTree.py

""" Test NLHTree-related functions. """

import sys
import time
import unittest

import hashlib

from rnglib import SimpleRNG
from nlhtree import NLHTree, NLHLeaf
from xlattice import Q, check_using_sha

if sys.version_info < (3, 6):
    # pylint: disable=unused-import
    import sha3     # monkey-patches hashlib


class TestNLHTree(unittest.TestCase):
    """ Test NLHTree-related functions. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################
    def make_leaf(self, names_so_far, using_sha):
        """ Build a leaf with random name and data using specific hash. """

        while True:
            name = self.rng.next_file_name(8)
            if name not in names_so_far:
                names_so_far.add(name)
                break
        nnn = self.rng.someBytes(8)        # 8 quasi-random bytes
        # pylint:disable=redefined-variable-type
        if using_sha == Q.USING_SHA1:
            sha = hashlib.sha1()
        elif using_sha == Q.USING_SHA2:
            sha = hashlib.sha256()
        elif using_sha == Q.USING_SHA3:
            sha = hashlib.sha3_256()
        sha.update(nnn)
        return NLHLeaf(name, sha.digest(), using_sha)

    # actual unit tests #############################################
    def test_simple_constructor(self):
        """ Build a tree with random name and data using various hashes. """

        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_simple_constructor(using)

    def do_test_simple_constructor(self, using_sha):
        """ Build a tree with random name and data using specific hash type. """

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
        name = self.rng.next_file_name(8)
        tree = NLHTree(name, using_sha)
        leaf_names = set()
        a_leaf = self.make_leaf(leaf_names, using_sha)
        b_leaf = self.make_leaf(leaf_names, using_sha)
        c_leaf = self.make_leaf(leaf_names, using_sha)
        d_leaf = self.make_leaf(leaf_names, using_sha)
        self.assertEqual(len(tree.nodes), 0)
        tree.insert(a_leaf)
        self.assertEqual(len(tree.nodes), 1)
        tree.insert(b_leaf)
        self.assertEqual(len(tree.nodes), 2)
        tree.insert(c_leaf)
        self.assertEqual(len(tree.nodes), 3)
        tree.insert(d_leaf)
        self.assertEqual(len(tree.nodes), 4)
        # we expect the nodes to be sorted
        for ndx in range(3):
            self.assertTrue(tree.nodes[ndx].name < tree.nodes[ndx + 1].name)

        matches = tree.list('*')
        for ndx, qqq in enumerate(tree.nodes):
            self.assertEqual(matches[ndx], '  ' + qqq.name)

        self.assertEqual(tree, tree)
        tree2 = tree.clone()
        self.assertEqual(tree2, tree)

    def test_insert_4_leafs(self):
        """
        Test inserting 4 leafs into a tree using various hash types.
        """
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_insert_4_leafs(using)


if __name__ == '__main__':
    unittest.main()
