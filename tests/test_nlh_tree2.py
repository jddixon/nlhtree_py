#!/usr/bin/env python3
# testNLHTree.py

""" Test trees derived from various quasi-random directory structures. """

import os
#import re
import shutil
# import sys
import time
import unittest

# import hashlib          # unused
from rnglib import SimpleRNG
from xlattice import (HashTypes, check_hashtype)
from nlhtree import NLHTree

# if sys.version_info < (3, 6):
#    # pylint: disable=unused-import
#    import sha3     # monkey-patches hashlib

ONE = 1
FOUR = 4
MAX_NAME_LEN = 8


class TestNLHTree2(unittest.TestCase):
    """ Test trees derived from various quasi-random directory structures. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions ---------------------------------------------

    def get_two_unique_directory_names(self):
        """ Make two unique directory names. """

        dir_name1 = self.rng.next_file_name(MAX_NAME_LEN)
        dir_name2 = dir_name1
        while dir_name2 == dir_name1:
            dir_name2 = self.rng.next_file_name(MAX_NAME_LEN)
        self.assertTrue(len(dir_name1) > 0)
        self.assertTrue(len(dir_name2) > 0)
        self.assertTrue(dir_name1 != dir_name2)
        return (dir_name1, dir_name2)

    def make_one_named_test_directory(self, name, depth, width):
        """
        Create a test directory below tmp/ with specified characteristics.
        """

        dir_path = "tmp/%s" % name
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        self.rng.next_data_dir(dir_path, depth, width, 32)
        return dir_path

    def make_two_test_directories(self, depth, width):
        """ Make two distinct quasi-random test directories below tmp/. """

        dir_name1 = self.rng.next_file_name(MAX_NAME_LEN)
        dir_path1 = self.make_one_named_test_directory(dir_name1, depth, width)

        dir_name2 = dir_name1
        while dir_name2 == dir_name1:
            dir_name2 = self.rng.next_file_name(MAX_NAME_LEN)
        dir_path2 = self.make_one_named_test_directory(dir_name2, depth, width)

        return (dir_name1, dir_path1, dir_name2, dir_path2)

    # unit tests ----------------------------------------------------

    def test_pathless_unbound(self):
        """ Test the constructor using various hash types. """

        for hashtype in [HashTypes.SHA1, HashTypes.SHA2, HashTypes.SHA3, ]:
            self.do_test_pathless_unbound(hashtype)

    def do_test_pathless_unbound(self, hashtype):
        """ Test constructor using two directories and a specific hash type. """

        (dir_name1, dir_name2) = self.get_two_unique_directory_names()

        check_hashtype(hashtype)
        tree1 = NLHTree(dir_name1, hashtype)
        self.assertEqual(dir_name1, tree1.name)
        self.assertEqual(tree1.hashtype, hashtype)

        tree2 = NLHTree(dir_name2, hashtype)
        self.assertEqual(dir_name2, tree2.name)
        self.assertEqual(tree2.hashtype, hashtype)

        self.assertTrue(tree1 == tree1)
        self.assertFalse(tree1 == tree2)
        self.assertFalse(tree1 is None)

        tree1c = tree1.clone()
        self.assertEqual(tree1c, tree1)

    def test_bound_flat_dirs(self):
        """
        Test directory is single level, with four data files, using
        various hash types.
        """
        for hashtype in HashTypes:
            self.do_test_bound_flat_dirs(hashtype)

    def do_test_bound_flat_dirs(self, hashtype):
        """
        Test directory is single level, with four data files, using
        specific hash type.
        """

        (dir_name1, dir_path1, dir_name2, dir_path2) =\
            self.make_two_test_directories(ONE, FOUR)
        tree1 = NLHTree.create_from_file_system(dir_path1, hashtype)
        self.assertEqual(dir_name1, tree1.name, True)
        nodes1 = tree1.nodes
        self.assertTrue(nodes1 is not None)
        self.assertEqual(FOUR, len(nodes1))

        tree2 = NLHTree.create_from_file_system(dir_path2, hashtype)
        self.assertEqual(dir_name2, tree2.name)
        nodes2 = tree2.nodes
        self.assertTrue(nodes2 is not None)
        self.assertEqual(FOUR, len(nodes2))

        self.assertEqual(tree1, tree1)
        self.assertFalse(tree1 == tree2)
        self.assertFalse(tree1 is None)

        tree1c = tree1.clone()
        self.assertEqual(tree1c, tree1)

    def test_bound_needle_dirs1(self):
        """
        Test directories four deep with one data file at the lowest level
        using various hash types.
        """
        for hashtype in HashTypes:
            self.do_test_bound_needle_dirs(hashtype)

    def do_test_bound_needle_dirs(self, hashtype):
        """
        Test directories four deep with one data file at the lowest level
        using specific hash type.
        """
        (dir_name1, dir_path1, dir_name2, dir_path2) =\
            self.make_two_test_directories(FOUR, ONE)
        tree1 = NLHTree.create_from_file_system(dir_path1, hashtype)

        self.assertEqual(dir_name1, tree1.name)
        nodes1 = tree1.nodes
        self.assertTrue(nodes1 is not None)
        self.assertEqual(ONE, len(nodes1))

        tree2 = NLHTree.create_from_file_system(dir_path2, hashtype)
        self.assertEqual(dir_name2, tree2.name)
        nodes2 = tree2.nodes
        self.assertTrue(nodes2 is not None)
        self.assertEqual(ONE, len(nodes2))

        self.assertTrue(tree1 == tree1)
        self.assertFalse(tree1 == tree2)

        tree1c = tree1.clone()
        self.assertEqual(tree1c, tree1)


if __name__ == '__main__':
    unittest.main()
