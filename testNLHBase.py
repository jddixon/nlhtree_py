#!/usr/bin/env python3

# testNLHBase.py
import hashlib
import time
import unittest

from rnglib import SimpleRNG
from nlhtree.base import NLHBase
from nlhtree import *

from xlattice import Q


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
        self.doTestConstructor(True)
        self.doTestConstructor(False)

    def doTestWithSimpleTree(self, usingSHA):
        if usingSHA == Q.USING_SHA1:
            sha = hashlib.sha1()
        else:
            # FIX ME FIX ME FIX ME
            sha = hashlib.sha256()

        # XXX WORKING HERE

    def testSimpletTree(self):
        self.doTestWithSimpleTree(usingSHA=True)
        self.doTestWithSimpleTree(usingSHA=False)


if __name__ == '__main__':
    unittest.main()
