#!/usr/bin/python3

# testNLHTree.py
import hashlib, time, unittest

from rnglib     import SimpleRNG
from nlhtree    import *

class TestNLHTree (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG( time.time() )
    def tearDown(self):
        pass

    # utility functions #############################################
    
    # actual unit tests #############################################
    def testSimpleConstructor(self):
        name = self.rng.nextFileName(8)
        tree = NLHTree(name)
        self.assertEqual(tree.name, name)

    def doTestSimpleTree(self, usingSHA1):
        if usingSHA1:
            sha = hashlib.sha1()
        else:
            sha = hashlib.sha256()

        # XXX HACKED FROM testLeaf, NEEDS REWRITE
        name = self.rng.nextFileName(8)
        n    = self.rng.someBytes(8)
        self.rng.nextBytes(n)
        sha.update(n)
        hash0 = sha.digest()

        leaf0 = NLHLeaf(name, hash0)
        self.assertEqual( name, leaf0.name )
        self.assertEqual( hash0, leaf0.binHash)

        name2 = name
        while name2 == name:
            name2 = self.rng.nextFileName(8)
        n    = self.rng.someBytes(8)
        self.rng.nextBytes(n)
        sha.update(n)
        hash1 = sha.digest()
        leaf1 = NLHLeaf(name2, hash1)
        self.assertEqual( name2, leaf1.name )
        self.assertEqual( hash1, leaf1.binHash)

        self.assertEqual ( leaf0, leaf0 )
        self.assertFalse ( leaf0 == leaf1 )

    def testSimpletTree (self):
        self.doTestSimpleTree(usingSHA1=True)   
        self.doTestSimpleTree(usingSHA1=False)

    
if __name__ == '__main__':
    unittest.main()
