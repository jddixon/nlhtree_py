#!/usr/bin/env python3

# testNLHLeaf.py
import hashlib
import time
import unittest

from rnglib import SimpleRNG
from nlhtree import *
from xlattice import Q


class TestNLHLeaf (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def doTestSimpleConstructor(self, usingSHA):
        if usingSHA == Q.USING_SHA1:
            sha = hashlib.sha1()
        else:
            # FIX ME FIX ME FIX ME
            sha = hashlib.sha256()

        name = self.rng.nextFileName(8)
        n = self.rng.someBytes(8)
        self.rng.nextBytes(n)
        sha.update(n)
        hash0 = sha.digest()

        leaf0 = NLHLeaf(name, hash0, usingSHA)
        self.assertEqual(name, leaf0.name)
        self.assertEqual(hash0, leaf0.binHash)

        name2 = name
        while name2 == name:
            name2 = self.rng.nextFileName(8)
        n = self.rng.someBytes(8)
        self.rng.nextBytes(n)
        sha.update(n)
        hash1 = sha.digest()
        leaf1 = NLHLeaf(name2, hash1, usingSHA)
        self.assertEqual(name2, leaf1.name)
        self.assertEqual(hash1, leaf1.binHash)

        self.assertEqual(leaf0, leaf0)
        self.assertEqual(leaf1, leaf1)
        self.assertFalse(leaf0 == leaf1)

        leaf0c = leaf0.clone()
        self.assertEqual(leaf0c, leaf0)

        leaf1c = leaf1.clone()
        self.assertEqual(leaf1c, leaf1)

    def testSimplestConstructor(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, ]:
            self.doTestSimpleConstructor(using)

if __name__ == '__main__':
    unittest.main()
