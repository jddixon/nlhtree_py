#!/usr/bin/env python3

# testNLHTree.py

import hashlib
import time
import unittest

from rnglib import SimpleRNG
from nlhtree import *


class TestNLHTree (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################
    def makeLeaf(self, namesSoFar, usingSHA1):
        while True:
            name = self.rng.nextFileName(8)
            if name not in namesSoFar:
                namesSoFar.add(name)
                break
        n = self.rng.someBytes(8)        # 8 quasi-random bytes
        if usingSHA1:
            sha = hashlib.sha1()
        else:
            sha = hashlib.sha256()
        sha.update(n)
        return NLHLeaf(name, sha.digest())

    # actual unit tests #############################################
    def testSimpleConstructor(self):
        self.doTestSimpleConstructor(usingSHA1=True)
        self.doTestSimpleConstructor(usingSHA1=False)

    def doTestSimpleConstructor(self, usingSHA1):
        name = self.rng.nextFileName(8)
        tree = NLHTree(name, usingSHA1)
        self.assertEqual(tree.name, name)
        self.assertEqual(tree.usingSHA1, usingSHA1)
        self.assertEqual(len(tree.nodes), 0)

    def doTestInsert4Leafs(self, usingSHA1):
        """
        Create 4 leaf nodes with random but unique names.  Insert
        them into a tree, verifying that the resulting sort is correct.
        """
        if usingSHA1:
            sha = hashlib.sha1()
        else:
            sha = hashlib.sha256()
        name = self.rng.nextFileName(8)
        tree = NLHTree(name, usingSHA1)
        leafNames = set()
        a = self.makeLeaf(leafNames, usingSHA1)
        b = self.makeLeaf(leafNames, usingSHA1)
        c = self.makeLeaf(leafNames, usingSHA1)
        d = self.makeLeaf(leafNames, usingSHA1)
        self.assertEqual(len(tree.nodes), 0)
        tree.insert(a)
        self.assertEqual(len(tree.nodes), 1)
        tree.insert(b)
        self.assertEqual(len(tree.nodes), 2)
        tree.insert(c)
        self.assertEqual(len(tree.nodes), 3)
        tree.insert(d)
        self.assertEqual(len(tree.nodes), 4)
        # we expect the nodes to be sorted
        for i in range(3):
            self.assertTrue(tree.nodes[i].name < tree.nodes[i + 1].name)

        matches = tree.list('*')
        for ndx, q in enumerate(tree.nodes):
            self.assertEqual(matches[ndx], '  ' + q.name)

        self.assertEqual(tree, tree)
        tree2 = tree.clone()
        self.assertEqual(tree2, tree)

    def testInsert4Leafs(self):
        self.doTestInsert4Leafs(usingSHA1=True)
        self.doTestInsert4Leafs(usingSHA1=False)


if __name__ == '__main__':
    unittest.main()
