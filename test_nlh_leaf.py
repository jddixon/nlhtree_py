#!/usr/bin/env python3
# testNLHLeaf.py

""" Test NLHLeaf-related functions. """

import sys
import time
import unittest

import hashlib
from rnglib import SimpleRNG
from xlattice import Q, check_using_sha
from nlhtree import NLHLeaf

if sys.version_info < (3, 6):
    # pylint: disable=unused-import
    import sha3     # monkey-patches hashlib


class TestNLHLeaf(unittest.TestCase):
    """ Test NLHLeaf-related functions. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def do_test_simple_constructor(self, using_sha):
        """ Test constructor for specific hash. """

        check_using_sha(using_sha)
        # pylint:disable=redefine-variable-type
        if using_sha == Q.USING_SHA1:
            sha = hashlib.sha1()
        elif using_sha == Q.USING_SHA2:
            sha = hashlib.sha256()
        elif using_sha == Q.USING_SHA3:
            sha = hashlib.sha3_256()

        name = self.rng.next_file_name(8)
        nnn = self.rng.someBytes(8)
        self.rng.next_bytes(nnn)
        sha.update(nnn)
        hash0 = sha.digest()

        leaf0 = NLHLeaf(name, hash0, using_sha)
        self.assertEqual(name, leaf0.name)
        self.assertEqual(hash0, leaf0.bin_hash)

        name2 = name
        while name2 == name:
            name2 = self.rng.next_file_name(8)
        nnn = self.rng.someBytes(8)
        self.rng.next_bytes(nnn)
        sha.update(nnn)
        hash1 = sha.digest()
        leaf1 = NLHLeaf(name2, hash1, using_sha)
        self.assertEqual(name2, leaf1.name)
        self.assertEqual(hash1, leaf1.bin_hash)

        self.assertEqual(leaf0, leaf0)
        self.assertEqual(leaf1, leaf1)
        self.assertFalse(leaf0 == leaf1)

        leaf0c = leaf0.clone()
        self.assertEqual(leaf0c, leaf0)

        leaf1c = leaf1.clone()
        self.assertEqual(leaf1c, leaf1)

    def test_simplest_constructor(self):
        """ Test simple constructor for various hashes. """

        for using in [Q.USING_SHA1, Q.USING_SHA2, ]:
            self.do_test_simple_constructor(using)

if __name__ == '__main__':
    unittest.main()
