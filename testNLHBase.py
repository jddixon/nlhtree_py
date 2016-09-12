#!/usr/bin/env python3

# testNLHBase.py
import hashlib
import sha3         # should be conditional

import time
import unittest

from rnglib import SimpleRNG
from nlhtree.base import NLHBase
from nlhtree import *

from xlattice import Q, checkUsingSHA


class TestNLHBase (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def doTestConstructor(self, usingSHA):
        name = self.rng.nextFileName(8)
        b = NLHBase(name, usingSHA)
        self.assertEqual(b.name, name)
        self.assertEqual(b.usingSHA, usingSHA)
        root = b.root
        ct = b.curTree
        self.assertEqual(root.name, ct.name)

    def testConstructor(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.doTestConstructor(using)

    def doTestWithSimpleTree(self, usingSHA):
        if usingSHA == Q.USING_SHA1:
            sha = hashlib.sha1()
        elif usingSHA == Q.USING_SHA2:
            sha = hashlib.sha256()
        elif usingSHA == Q.USING_SHA3:
            sha = hashlib.sha3_256()

        # XXX WORKING HERE

    def testSimpletTree(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.doTestWithSimpleTree(using)


if __name__ == '__main__':
    unittest.main()
