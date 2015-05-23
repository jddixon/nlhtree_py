#!/usr/bin/python3

# testNLHBase.py
import hashlib, time, unittest

from rnglib     import SimpleRNG
from nlhtree    import *

class TestNLHBase (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG( time.time() )
    def tearDown(self):
        pass

    # utility functions #############################################
    
    # actual unit tests #############################################
    def testConstructor(self):
        name = self.rng.nextFileName(8)
        b = NLHBase(name)
        self.assertEqual(b.name, name)
        root   = b.root
        ct     = b.curTree
        self.assertEqual(root.name, ct.name)
        
    def doTestWithSimpleTree(self, usingSHA1):
        if usingSHA1:
            sha = hashlib.sha1()
        else:
            sha = hashlib.sha256()

        # XXX WORKING HERE

    def testSimpletTree (self):
        self.doTestWithSimpleTree(usingSHA1=True)   
        self.doTestWithSimpleTree(usingSHA1=False)

    
if __name__ == '__main__':
    unittest.main()
