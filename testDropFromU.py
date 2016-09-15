#!/usr/bin/env python3

# nlhtree_py/testDropFromU.py

import hashlib
import sha3     # must follow hashlib

import os
import time
import unittest
from binascii import hexlify

from rnglib import SimpleRNG
from nlhtree import *
from xlattice import Q, checkUsingSHA
from xlattice.u import UDir


class TestDropFromU (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def generateUDT(self, struc, usingSHA):
        """
        Generate under ./tmp a data directory with random content,
        a uDir containing the same data, and an NLHTree that matches.
        uDir has the directory structure (DIR_FLAT, DIR16x16, DIR256x256,
        etc requested.  Hashes are SHA1 if using SHA1 is True, SHA256
        otherwise.

        values is a list of binary values, each the content of a file
        under dataDir.  Each value contains a non-zero number of bytes.

        hashes is a list of the SHA hashes of the values.  Each hash
        is a binary value.  If using SHA1 it consists of 20 bytes.

        return uPath, dataPath, tree, hashes, values
        """

        # make a unique U directory under ./tmp/
        os.makedirs('tmp', mode=0o755, exist_ok=True)
        uRootName = self.rng.nextFileName(8)
        uPath = os.path.join('tmp', uRootName)
        while os.path.exists(uPath):
            uRootName = self.rng.nextFileName(8)
            uPath = os.path.join('tmp', uRootName)

        # DEBUG
        print("uRootName = %s" % uRootName)
        # END

        # create uDir and the NLHTree
        uDir = UDir(uPath, struc, usingSHA)
        self.assertTrue(os.path.exists(uPath))

        # make a unique data directory under tmp/
        dataTmp = self.rng.nextFileName(8)
        tmpPath = os.path.join('tmp', dataTmp)
        while os.path.exists(tmpPath):
            dataTmp = self.rng.nextFileName(8)
            tmpPath = os.path.join('tmp', dataTmp)

        # dataDir must have same base name as NLHTree
        topName = self.rng.nextFileName(8)
        dataPath = os.path.join(tmpPath, topName)
        dataDir = os.makedirs(dataPath, mode=0o755)

        # DEBUG
        #print("dataTmp = %s" % dataTmp)
        #print("topName = %s" % topName)
        #print('dataPath = %s' % dataPath)
        # END

        tree = NLHTree(topName, usingSHA)

        # generate N and N unique random values, where N is at least 16
        N = 16 + self.rng.nextInt16(16)
        # DEBUG
        #print("N = %d" % N)
        # END

        values = []
        hashes = []
        for n in range(N):
            # generate datum ------------------------------
            vLen = 32 + self.rng.nextInt16(32)      # length of value generated
            datum = self.rng.someBytes(vLen)        # that many random bytes
            values.append(datum)

            # generate hash = binKey ----------------------
            if usingSHA == Q.USING_SHA1:
                sha = hashlib.sha1()
            elif usingSHA == Q.USING_SHA2:
                sha = hashlib.sha256()
            elif usingSHA == Q.USING_SHA3:
                sha = hashlib.sha3_256()
            sha.update(datum)
            binKey = sha.digest()
            hexKey = sha.hexdigest()
            hashes.append(binKey)

            # write data file -----------------------------
            fileName = 'value%04d' % n
            pathToFile = os.path.join(dataPath, fileName)
            with open(pathToFile, 'wb') as f:
                # DEBUG
                #print("writing %s to %s" % (hexKey, pathToFile))
                # END
                f.write(datum)

            # insert leaf into tree -----------------------
            pathFromTop = os.path.join(topName, fileName)
            leaf = NLHLeaf(fileName, binKey, usingSHA)
            tree.insert(leaf)

            # DEBUG
            #print("  inserting <%s %s>" % (leaf.name, leaf.hexHash))
            # END

            # write data into uDir ------------------------
            uDir.putData(datum, hexKey)

        return uPath, dataPath, tree, hashes, values

    def doTestWithEphemeralTree(self, struc, usingSHA):

        uPath, dataPath, tree, hashes, values = self.generateUDT(
            struc, usingSHA)

        # DEBUG
        #print("TREE:\n%s" % tree)
        # END
        # verify that the dataDir matches the nlhTree
        tree2 = NLHTree.createFromFileSystem(dataPath, usingSHA)
        # DEBUG
        #print("TREE2:\n%s" % tree2)
        # END
        self.assertEqual(tree2, tree)

        N = len(values)             # number of values present
        hexHashes = []
        for i in range(N):
            hexHashes.append(hexlify(hashes[i]).decode('ascii'))

        p = [i for i in range(N)]  # indexes into lists
        self.rng.shuffle(p)         # shuffled

        K = self.rng.nextInt16(N)   # we will drop this many indexes

        # DEBUG
        # print("dropping %d from %d elements" % (K, N))
        # END

        dropMe = p[0:K]        # indexes of values to drop
        keepMe = p[K:]         # of those which should still be present

        # construct an NLHTree containing values to be dropped from uDir
        q = tree.clone()
        for i in keepMe:
            name = 'value%04d' % i
            q.delete(name)     # the parameter is a glob !

        # these values should be absent from q: they won't be dropped from uDir
        for i in keepMe:
            name = 'value%04d' % i
            x = q.find(name)
            self.assertEqual(len(x), 0)

        # these values shd still be present in q: they'll be dropped from UDir
        for i in dropMe:
            name = 'value%04d' % i
            x = q.find(name)
            self.assertEqual(len(x), 1)

        # the q subtree contains those elements which will be dropped
        # from uDir
        unmatched = q.dropFromUDir(uPath)
        # DEBUG
        # for x in unmatched:  # (relPath, hash)
        #    print("unmatched: %s %s" % (x[0], x[1]))
        # END
        # self.assertEqual( len(unmatched), 0)      ### XXX

        uDir = UDir(uPath, struc, usingSHA)
        self.assertTrue(os.path.exists(uPath))

        # these values should still be present in uDir
        for i in keepMe:
            hexHash = hexHashes[i]
            self.assertTrue(uDir.exists(hexHash))

        # these values should NOT be present in UDir
        for i in dropMe:
            hexHash = hexHashes[i]
            self.assertFalse(uDir.exists(hexHash))

    def testWithEphemeralTree(self):
        for struc in [UDir.DIR_FLAT, UDir.DIR16x16, UDir.DIR256x256, ]:
            for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
                self.doTestWithEphemeralTree(struc, using)

if __name__ == '__main__':
    unittest.main()
