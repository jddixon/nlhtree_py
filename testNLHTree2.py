#!/usr/bin/python3

# testNLHTree.py
import hashlib
import os
import re
import shutil
import sys
import time
import unittest

from rnglib import SimpleRNG
from xlattice import SHA1_HEX_NONE, SHA2_HEX_NONE
from nlhtree import *

ONE = 1
FOUR = 4
MAX_NAME_LEN = 8


class TestNLHTree2 (unittest.TestCase):

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    # utility functions ---------------------------------------------

    def getTwoUniqueDirectoryNames(self):
        dirName1 = self.rng.nextFileName(MAX_NAME_LEN)
        dirName2 = dirName1
        while dirName2 == dirName1:
            dirName2 = self.rng.nextFileName(MAX_NAME_LEN)
        self.assertTrue(len(dirName1) > 0)
        self.assertTrue(len(dirName2) > 0)
        self.assertTrue(dirName1 != dirName2)
        return (dirName1, dirName2)

    def makeOneNamedTestDirectory(self, name, depth, width):
        dirPath = "tmp/%s" % name
        if os.path.exists(dirPath):
            shutil.rmtree(dirPath)
        self.rng.nextDataDir(dirPath, depth, width, 32)
        return dirPath

    def makeTwoTestDirectories(self, depth, width):
        dirName1 = self.rng.nextFileName(MAX_NAME_LEN)
        dirPath1 = self.makeOneNamedTestDirectory(dirName1, depth, width)

        dirName2 = dirName1
        while dirName2 == dirName1:
            dirName2 = self.rng.nextFileName(MAX_NAME_LEN)
        dirPath2 = self.makeOneNamedTestDirectory(dirName2, depth, width)

        return (dirName1, dirPath1, dirName2, dirPath2)

    # unit tests ----------------------------------------------------

    def testPathlessUnboundConstructor1(self):
        self.doTestPathlessUnboundConstructor1(usingSHA1=True)
        self.doTestPathlessUnboundConstructor1(usingSHA1=False)

    def doTestPathlessUnboundConstructor1(self, usingSHA1):
        (dirName1, dirName2) = self.getTwoUniqueDirectoryNames()

        tree1 = NLHTree(dirName1, usingSHA1)
        self.assertEqual(dirName1, tree1.name)
        self.assertEqual(tree1.usingSHA1, usingSHA1)

        tree2 = NLHTree(dirName2, usingSHA1)
        self.assertEqual(dirName2, tree2.name)
        self.assertEqual(tree2.usingSHA1, usingSHA1)

        self.assertTrue(tree1 == tree1)
        self.assertFalse(tree1 == tree2)
        self.assertFalse(tree1 is None)

    def testBoundFlatDirs(self):
        self.doTestBoundFlatDirs(usingSHA1=True)
        self.doTestBoundFlatDirs(usingSHA1=False)

    def doTestBoundFlatDirs(self, usingSHA1):
        """test directory is single level, with four data files"""
        (dirName1, dirPath1, dirName2, dirPath2) = \
            self.makeTwoTestDirectories(ONE, FOUR)
        tree1 = NLHTree.createFromFileSystem(dirPath1, usingSHA1)
        self.assertEqual(dirName1, tree1.name, True)
        nodes1 = tree1.nodes
        self.assertTrue(nodes1 is not None)
        self.assertEqual(FOUR, len(nodes1))

        tree2 = NLHTree.createFromFileSystem(dirPath2, usingSHA1)
        self.assertEqual(dirName2, tree2.name)
        nodes2 = tree2.nodes
        self.assertTrue(nodes2 is not None)
        self.assertEqual(FOUR, len(nodes2))

        self.assertEqual(tree1, tree1)
        self.assertFalse(tree1 == tree2)
        self.assertFalse(tree1 is None)

    def testBoundNeedleDirs1(self):
        self.doTestBoundNeedleDirs(usingSHA1=True)
        self.doTestBoundNeedleDirs(usingSHA1=False)

    def doTestBoundNeedleDirs(self, usingSHA1):
        """test directories four deep with one data file at the lowest level"""
        (dirName1, dirPath1, dirName2, dirPath2) = \
            self.makeTwoTestDirectories(FOUR, ONE)
        tree1 = NLHTree.createFromFileSystem(dirPath1, usingSHA1)

        self.assertEqual(dirName1, tree1.name)
        nodes1 = tree1.nodes
        self.assertTrue(nodes1 is not None)
        self.assertEqual(ONE, len(nodes1))

        tree2 = NLHTree.createFromFileSystem(dirPath2, usingSHA1)
        self.assertEqual(dirName2, tree2.name)
        nodes2 = tree2.nodes
        self.assertTrue(nodes2 is not None)
        self.assertEqual(ONE, len(nodes2))

        self.assertTrue(tree1 == tree1)
        self.assertFalse(tree1 == tree2)

if __name__ == '__main__':
    unittest.main()
