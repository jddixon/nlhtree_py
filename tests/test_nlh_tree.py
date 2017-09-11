#!/usr/bin/env python3
# testNLHTree.py

""" Test NLHTree-related functions. """

import sys
import time
import unittest

import hashlib

from rnglib import SimpleRNG
from nlhtree import NLHTree, NLHLeaf
from xlattice import HashTypes, check_hashtype

if sys.version_info < (3, 6):
    # pylint: disable=unused-import
    import sha3     # monkey-patches hashlib
    assert sha3     # suppresses warning


class TestNLHTree(unittest.TestCase):
    """ Test NLHTree-related functions. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################
    def make_leaf(self, names_so_far, hashtype):
        """ Build a leaf with random name and data using specific hash. """

        while True:
            name = self.rng.next_file_name(8)
            if name not in names_so_far:
                names_so_far.add(name)
                break
        nnn = self.rng.some_bytes(8)        # 8 quasi-random bytes
        # pylint:disable=redefined-variable-type
        if hashtype == HashTypes.SHA1:
            sha = hashlib.sha1()
        elif hashtype == HashTypes.SHA2:
            sha = hashlib.sha256()
        elif hashtype == HashTypes.SHA3:
            sha = hashlib.sha3_256()
        sha.update(nnn)
        return NLHLeaf(name, sha.digest(), hashtype)

    # actual unit tests #############################################
    def test_simple_constructor(self):
        """ Build a tree with random name and data using various hashes. """

        for using in [HashTypes.SHA1, HashTypes.SHA2, HashTypes.SHA3, ]:
            self.do_test_simple_constructor(using)

    def do_test_simple_constructor(self, hashtype):
        """
        Build a tree with random name and data using specific hash type.
        """

        name = self.rng.next_file_name(8)
        tree = NLHTree(name, hashtype)
        self.assertEqual(tree.name, name)
        self.assertEqual(tree.hashtype, hashtype)
        self.assertEqual(len(tree.nodes), 0)

    def do_test_insert_4_leafs(self, hashtype):
        """
        Create 4 leaf nodes with random but unique names.  Insert
        them into a tree, verifying that the resulting sort is correct.
        """
        check_hashtype(hashtype)
        name = self.rng.next_file_name(8)
        tree = NLHTree(name, hashtype)
        leaf_names = set()
        a_leaf = self.make_leaf(leaf_names, hashtype)
        b_leaf = self.make_leaf(leaf_names, hashtype)
        c_leaf = self.make_leaf(leaf_names, hashtype)
        d_leaf = self.make_leaf(leaf_names, hashtype)
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
        for using in [HashTypes.SHA1, HashTypes.SHA2, HashTypes.SHA3, ]:
            self.do_test_insert_4_leafs(using)


if __name__ == '__main__':
    unittest.main()
