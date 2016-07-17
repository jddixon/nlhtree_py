#!/usr/bin/env python3

# nlhtree_py/testRmFromU.py

import hashlib
import os
import time
import unittest

from rnglib import SimpleRNG
from nlhtree import *
from xlattice.u import (UDir, DIR_FLAT, DIR16x16, DIR256x256)


class TestRmFromU (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def doTestWithEphemeralTree(self, struc, usingSHA1):

        #############################################################
        # STILL ISN'T RIGHT: dataDir Name SHOULD BE SAME AS uRootName
        #############################################################

        # make a unique data directory under tmp/
        dataName = self.rng.nextFileName(8)
        dataPath = os.path.join('tmp', dataName)
        while os.path.exists(dataPath):
            dataName = self.rng.nextFileName(8)
            dataPath = os.path.join('tmp', dataName)

        dataDir = os.mkdir(dataPath, 0o755)
        # DEBUG
        print("dataName = %s" % dataName)
        # END

        # make a unique U directory under tmp/
        uRootName = self.rng.nextFileName(8)
        uPath = os.path.join('tmp', uRootName)
        while os.path.exists(uPath):
            uRootName = self.rng.nextFileName(8)
            uPath = os.path.join('tmp', uRootName)

        # DEBUG
        print("uRootName = %s" % uRootName)
        # END

        # create uDir and the NLHTree
        uDir = UDir(uPath, struc, usingSHA1)
        self.assertTrue(os.path.exists(uPath))

        tree = NLHTree(uRootName, usingSHA1)

        # generate N and N unique random values, where N is at least 16
        N = 16 + self.rng.nextInt16(16)
        # DEBUG
        print("N = %d" % N)
        # END

        values = []
        hashes = []
        for n in range(N):
            # generate datum ------------------------------
            vLen = 32 + self.rng.nextInt16(32)      # length of value generated
            datum = self.rng.someBytes(vLen)        # that many random bytes
            values.append(datum)

            # generate hash = binKey ----------------------
            if usingSHA1:
                sha = hashlib.sha1()
            else:
                sha = hashlib.sha256()
            sha.update(datum)
            binKey = sha.digest()
            hexKey = sha.hexdigest()
            hashes.append(binKey)

            # write data file -----------------------------
            fileName = 'value%04d' % n
            pathToFile = os.path.join(dataPath, fileName)
            with open(pathToFile, 'wb') as f:
                # DEBUG
                print("writing %s to %s" % (hexKey, pathToFile))
                # END
                f.write(datum)

            # insert leaf into tree -----------------------
            leaf = NLHLeaf(fileName, binKey)
            tree.insert(leaf)

            # write data into uDir ------------------------
            uDir.putData(datum, hexKey)

        # verify that the dataDir matches the nlhTree
        tree2 = NLHTree.createFromFileSystem(dataPath, usingSHA1)

        # DEBUG
        print("TREE:\n%s" % tree)
        print("TREE2:\n%s" % tree2)
        # END

        self.assertEqual(tree2, tree)

        # WORKING HERE

    def testWithEphemeralTree(self):
        for struc in [DIR_FLAT, DIR16x16, DIR256x256, ]:
            self.doTestWithEphemeralTree(struc, True)
            self.doTestWithEphemeralTree(struc, False)

if __name__ == '__main__':
    unittest.main()
