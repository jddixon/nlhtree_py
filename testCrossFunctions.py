#!/usr/bin/env python3

# testCrossFunctions.py

import os
import shutil
import time
import unittest

from rnglib import SimpleRNG
from nlhtree import NLHTree


class TestCrossFunctions (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions #############################################

    # actual unit tests #############################################
    def doTestCrossFunctions(self, usingSHA1):
        # we assume that there is valid data in
        #   example/{example.nlh,dataDir,uDir}

        self.assertTrue(usingSHA1)       # the only mode currently supported

        GOLD_DATA = 'example/dataDir'
        GOLD_LIST_FILE = 'example/example.nlh'

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

        # copy the standard data directory into tmp/uDir, creating a
        # listing file tmp/list.nlh as a side effect
        NLHTree.saveToUDir(GOLD_DATA, TARGET_UDIR, TARGET_LIST_FILE, usingSHA1)

        self.assertTrue(os.path.exists, GOLD_LIST_FILE)
        with open(GOLD_LIST_FILE, 'r') as f:
            goldListing = f.read()

        self.assertTrue(os.path.exists, TARGET_LIST_FILE)
        with open(TARGET_LIST_FILE, 'r') as f:
            outputListing = f.read()

        self.assertEqual(goldListing, outputListing)

        tree = NLHTree.createFromFileSystem(GOLD_DATA, usingSHA1)

        # THIS IS THE WRONG TEST - argument should be TARGET_DATA_DIR XXX
        unmatched = tree.checkInDataDir(GOLD_DATA)
        self.assertEqual(len(unmatched), 0)

        unmatched = tree.checkInUDir(TARGET_UDIR)
        self.assertEqual(len(unmatched), 0)

    def testSimplestConstructor(self):
        self.doTestCrossFunctions(usingSHA1=True)
        # self.doTestCrossFunctions(usingSHA1=False)


if __name__ == '__main__':
    unittest.main()
