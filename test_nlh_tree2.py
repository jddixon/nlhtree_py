#!/usr/bin/env python3

# testNLHTree.py

import os
import re
import shutil
import sys
import time
import unittest

import hashlib
if sys.version_info < (3, 6):
    # pylint: disable=unused-import
    import sha3     # monkey-patches hashlib

from rnglib import SimpleRNG
from xlattice import (SHA1_HEX_NONE, SHA2_HEX_NONE, SHA3_HEX_NONE,
                      Q, check_using_sha)
from nlhtree import *

ONE = 1
FOUR = 4
MAX_NAME_LEN = 8


class TestNLHTree2 (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions ---------------------------------------------

    def get_two_unique_directory_names(self):
        dir_name1 = self.rng.nextFileName(MAX_NAME_LEN)
        dir_name2 = dir_name1
        while dir_name2 == dir_name1:
            dir_name2 = self.rng.nextFileName(MAX_NAME_LEN)
        self.assertTrue(len(dir_name1) > 0)
        self.assertTrue(len(dir_name2) > 0)
        self.assertTrue(dir_name1 != dir_name2)
        return (dir_name1, dir_name2)

    def make_one_named_test_directory(self, name, depth, width):
        dir_path = "tmp/%s" % name
        if os.path.exists(dir_path):
            shutil.rmtree(dir_path)
        self.rng.next_data_dir(dir_path, depth, width, 32)
        return dir_path

    def make_two_test_directories(self, depth, width):
        dir_name1 = self.rng.nextFileName(MAX_NAME_LEN)
        dir_path1 = self.make_one_named_test_directory(dir_name1, depth, width)

        dir_name2 = dir_name1
        while dir_name2 == dir_name1:
            dir_name2 = self.rng.nextFileName(MAX_NAME_LEN)
        dir_path2 = self.make_one_named_test_directory(dir_name2, depth, width)

        return (dir_name1, dir_path1, dir_name2, dir_path2)

    # unit tests ----------------------------------------------------

    def test_pathless_unbound_constructor1(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_pathless_unbound_constructor1(using)

    def do_test_pathless_unbound_constructor1(self, using_sha):
        (dir_name1, dir_name2) = self.get_two_unique_directory_names()

        check_using_sha(using_sha)
        tree1 = NLHTree(dir_name1, using_sha)
        self.assertEqual(dir_name1, tree1.name)
        self.assertEqual(tree1.using_sha, using_sha)

        tree2 = NLHTree(dir_name2, using_sha)
        self.assertEqual(dir_name2, tree2.name)
        self.assertEqual(tree2.using_sha, using_sha)

        self.assertTrue(tree1 == tree1)
        self.assertFalse(tree1 == tree2)
        self.assertFalse(tree1 is None)

        tree1c = tree1.clone()
        self.assertEqual(tree1c, tree1)

    def test_bound_flat_dirs(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_bound_flat_dirs(using)

    def do_test_bound_flat_dirs(self, using_sha):
        """test directory is single level, with four data files"""
        (dir_name1, dir_path1, dir_name2, dir_path2) =\
            self.make_two_test_directories(ONE, FOUR)
        tree1 = NLHTree.create_from_file_system(dir_path1, using_sha)
        self.assertEqual(dir_name1, tree1.name, True)
        nodes1 = tree1.nodes
        self.assertTrue(nodes1 is not None)
        self.assertEqual(FOUR, len(nodes1))

        tree2 = NLHTree.create_from_file_system(dir_path2, using_sha)
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
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_bound_needle_dirs(using)

    def do_test_bound_needle_dirs(self, using_sha):
        """test directories four deep with one data file at the lowest level"""
        (dir_name1, dir_path1, dir_name2, dir_path2) =\
            self.make_two_test_directories(FOUR, ONE)
        tree1 = NLHTree.create_from_file_system(dir_path1, using_sha)

        self.assertEqual(dir_name1, tree1.name)
        nodes1 = tree1.nodes
        self.assertTrue(nodes1 is not None)
        self.assertEqual(ONE, len(nodes1))

        tree2 = NLHTree.create_from_file_system(dir_path2, using_sha)
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
