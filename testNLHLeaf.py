#!/usr/bin/python3

# testNLHLeaf.py
import hashlib, time, unittest

from rnglib     import SimpleRNG
from nlhtree    import *

class TestNLHLeaf (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG( time.time() )
    def tearDown(self):
        pass

    # utility functions #############################################
    
    # actual unit tests #############################################
    def doTestSimpleConstructor(self, usingSHA1):
        if usingSHA1:
            sha = hashlib.sha1()
        else:
            sha = hashlib.sha256()

        fileName = self.rng.nextFileName(8)
        n    = self.rng.someBytes(8)
        self.rng.nextBytes(n)
        sha.update(n)
        hash0 = sha.digest()

        leaf0 = NLHLeaf(fileName, hash0)
        self.assertEqual( fileName, leaf0.name )
        self.assertEqual( hash0, leaf0.binHash)

        fileName2 = fileName
        while fileName2 == fileName:
            fileName2 = self.rng.nextFileName(8)
        n    = self.rng.someBytes(8)
        self.rng.nextBytes(n)
        sha.update(n)
        hash1 = sha.digest()
        leaf1 = NLHLeaf(fileName2, hash1)
        self.assertEqual( fileName2, leaf1.name )
        self.assertEqual( hash1, leaf1.binHash)

        self.assertEqual ( leaf0, leaf0 )
        self.assertFalse ( leaf0 == leaf1 )

    def testSimplestConstructor(self):
        self.doTestSimpleConstructor(usingSHA1=True)   
        self.doTestSimpleConstructor(usingSHA1=False)

if __name__ == '__main__':
    unittest.main()
