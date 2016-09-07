#!/usr/bin/env python3

# testCrossFunctions.py

import os
import shutil
import time
import unittest

from rnglib import SimpleRNG
from nlhtree import NLHTree
from xlattice import Q
from xlattice.util import makeExRE


class TestCrossFunctions (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def doTestCrossFunctions(self, usingSHA):
        # we assume that there is valid data in
        #   example/{example.nlh,dataDir,uDir}

        if usingSHA == Q.USING_SHA1:
            GOLD_DATA = 'example1/dataDir'
            GOLD_LIST_FILE = 'example1/example.nlh'
        elif usingSHA == Q.USING_SHA2:
            GOLD_DATA = 'example2/dataDir'
            GOLD_LIST_FILE = 'example2/example.nlh'
        else:
            # FIX ME FIX ME
            raise UnimplementedError

        TARGET_DATA_DIR = 'tmp/dataDir'
        TARGET_LIST_FILE = 'tmp/listing.nlh'
        TARGET_UDIR = 'tmp/uDir'

        # clear the tmp/ directory entirely
        if os.path.exists('tmp'):
            shutil.rmtree('tmp')

        os.makedirs(os.path.join(TARGET_UDIR, 'in'), mode=0o755, exist_ok=True)
        os.makedirs(
            os.path.join(
                TARGET_UDIR,
                'tmp'),
            mode=0o755,
            exist_ok=True)
        self.assertTrue(os.path.exists(os.path.join(TARGET_UDIR, 'in')))

        exclusions = ['build']
        exRE = makeExRE(exclusions)

        tree = NLHTree.createFromFileSystem(GOLD_DATA, usingSHA, exRE, None)
        tree.saveToUDir(GOLD_DATA, TARGET_UDIR, usingSHA)

        self.assertTrue(os.path.exists(GOLD_LIST_FILE))
        with open(GOLD_LIST_FILE, 'r') as f:
            goldListing = f.read()

        outputListing = tree.__str__()
        self.assertEqual(goldListing, outputListing)

        tree = NLHTree.createFromFileSystem(GOLD_DATA, usingSHA)
        self.assertIsNotNone(tree)

        # first iteration over tree
        unmatched = tree.checkInDataDir(GOLD_DATA)
        self.assertEqual(len(unmatched), 0)

        # second iteration over tree
        unmatched = tree.checkInUDir(TARGET_UDIR)
        if len(unmatched) > 0:
            for u in unmatched:
                # DEBUG
                print(u)
                # END
                print("not matched: ", u)
        self.assertEqual(len(unmatched), 0)

        # third iteration over tree - this should create the data directory
        unmatched = tree.populateDataDir(TARGET_UDIR, 'tmp')
        self.assertEqual(len(unmatched), 0)

        self.assertTrue(os.path.exists(TARGET_DATA_DIR),
                        'data directory created')

        unmatched = tree.checkInDataDir(TARGET_DATA_DIR)
        self.assertEqual(len(unmatched), 0)

        tree2 = NLHTree.createFromFileSystem(TARGET_DATA_DIR, usingSHA)
        self.assertEqual(tree, tree2)

    def testSimplestConstructor(self):
        for using in [Q.USING_SHA1, Q.USING_SHA2, ]:
            # FIX ME FIX ME
            self.doTestCrossFunctions(using)

if __name__ == '__main__':
    unittest.main()
