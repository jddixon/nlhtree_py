#!/usr/bin/env python3
# testNLHLeaf.py

""" Test NLHLeaf-related functions. """

import sys
import time
import unittest

import hashlib
from rnglib import SimpleRNG
from xlattice import HashTypes, check_hashtype
from nlhtree import NLHLeaf

if sys.version_info < (3, 6):
    # pylint: disable=unused-import
    import sha3     # monkey-patches hashlib
    assert sha3     # suppress warning


class TestNLHLeaf(unittest.TestCase):
    """ Test NLHLeaf-related functions. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def do_test_simple_constructor(self, hashtype):
        """ Test constructor for specific hash. """

        check_hashtype(hashtype)
        # pylint:disable=redefined-variable-type
        if hashtype == HashTypes.SHA1:
            sha = hashlib.sha1()
        elif hashtype == HashTypes.SHA2:
            sha = hashlib.sha256()
        elif hashtype == HashTypes.SHA3:
            sha = hashlib.sha3_256()

        name = self.rng.next_file_name(8)
        nnn = self.rng.some_bytes(8)
        self.rng.next_bytes(nnn)
        sha.update(nnn)
        hash0 = sha.digest()

        leaf0 = NLHLeaf(name, hash0, hashtype)
        self.assertEqual(name, leaf0.name)
        self.assertEqual(hash0, leaf0.bin_hash)

        name2 = name
        while name2 == name:
            name2 = self.rng.next_file_name(8)
        nnn = self.rng.some_bytes(8)
        self.rng.next_bytes(nnn)
        sha.update(nnn)
        hash1 = sha.digest()
        leaf1 = NLHLeaf(name2, hash1, hashtype)
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

        for hashtype in HashTypes:
            self.do_test_simple_constructor(hashtype)


if __name__ == '__main__':
    unittest.main()
