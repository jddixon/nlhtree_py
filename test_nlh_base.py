#!/usr/bin/env python3
# testNLHBase.py

""" Test basic NLHTree functions. """

import hashlib
import sha3         # monkey-patches hashlib; should be conditional

import time
import unittest

from rnglib import SimpleRNG
from nlhtree.base import NLHBase
from nlhtree import *

from xlattice import Q, checkUsingSHA


class TestNLHBase (unittest.TestCase):
    """ Test basic NLHTree functions. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def do_test_constructor(self, using_sha):
        name = self.rng.next_file_name(8)
        b = NLHBase(name, using_sha)
        self.assertEqual(b.name, name)
        self.assertEqual(b.using_sha, using_sha)
        root = b.root
        ct = b.curTree
        self.assertEqual(root.name, ct.name)

    def testConstructor(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_constructor(using)

    def do_test_with_simple_tree(self, using_sha):
        if using_sha == Q.USING_SHA1:
            sha = hashlib.sha1()
        elif using_sha == Q.USING_SHA2:
            sha = hashlib.sha256()
        elif using_sha == Q.USING_SHA3:
            sha = hashlib.sha3_256()

        # XXX WORKING HERE

    def testSimpletTree(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_with_simple_tree(using)


if __name__ == '__main__':
    unittest.main()
