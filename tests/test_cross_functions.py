#!/usr/bin/env python3
# testCrossFunctions.py

""" Test functions for cross-comparing data structures. """

import os
import shutil
import time
import unittest

from rnglib import SimpleRNG
from nlhtree import NLHTree
from xlattice import HashTypes, check_hashtype
from xlutil import make_ex_re


class TestCrossFunctions(unittest.TestCase):
    """ Test functions for cross-comparing data structures. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def do_test_cross_functions(self, hashtype):
        """
        Test cross functions for specific hash type.

        We assume that there is valid data in
            example/{example.nlh,dataDir,uDir}
        """
        check_hashtype(hashtype)

        if hashtype == HashTypes.SHA1:
            gold_data = 'example1/dataDir'
            gold_list_file = 'example1/example.nlh'
        elif hashtype == HashTypes.SHA2:
            gold_data = 'example2/dataDir'
            gold_list_file = 'example2/example.nlh'
        elif hashtype == HashTypes.SHA3:
            gold_data = 'example3/dataDir'
            gold_list_file = 'example3/example.nlh'
        elif hashtype == HashTypes.BLAKE2B:
            gold_data = 'example4/dataDir'
            gold_list_file = 'example4/example.nlh'
        else:
            raise NotImplementedError

        target_data_dir = 'tmp/dataDir'
        # target_list_file = 'tmp/listing.nlh'      # never used
        target_u_dir = 'tmp/uDir'

        # clear the tmp/ directory entirely
        if os.path.exists('tmp'):
            shutil.rmtree('tmp')

        os.makedirs(
            os.path.join(
                target_u_dir,
                'in'),
            mode=0o755,
            exist_ok=True)
        os.makedirs(
            os.path.join(
                target_u_dir,
                'tmp'),
            mode=0o755,
            exist_ok=True)
        self.assertTrue(os.path.exists(os.path.join(target_u_dir, 'in')))

        exclusions = ['build']
        ex_re = make_ex_re(exclusions)

        tree = NLHTree.create_from_file_system(
            gold_data, hashtype, ex_re, None)
        tree.save_to_u_dir(gold_data, target_u_dir, hashtype)

        self.assertTrue(os.path.exists(gold_list_file))
        with open(gold_list_file, 'r') as file:
            gold_listing = file.read()

        output_listing = tree.__str__()
        # DEBUG
        # print("OUTPUT LISING for %s:\n%s" % (hashtype, output_listing))
        # END
        self.assertEqual(gold_listing, output_listing)

        tree = NLHTree.create_from_file_system(gold_data, hashtype)
        self.assertIsNotNone(tree)

        # first iteration over tree
        unmatched = tree.check_in_data_dir(gold_data)
        self.assertEqual(len(unmatched), 0)

        # second iteration over tree
        unmatched = tree.check_in_u_dir(target_u_dir)
        if unmatched:
            for unm in unmatched:
                # DEBUG
                # print(u)
                # END
                print("not matched: ", unm)
        self.assertEqual(len(unmatched), 0)

        # third iteration over tree - this should create the data directory
        unmatched = tree.populate_data_dir(target_u_dir, 'tmp')
        self.assertEqual(len(unmatched), 0)

        self.assertTrue(os.path.exists(target_data_dir),
                        'data directory created')

        unmatched = tree.check_in_data_dir(target_data_dir)
        self.assertEqual(len(unmatched), 0)

        tree2 = NLHTree.create_from_file_system(target_data_dir, hashtype)
        self.assertEqual(tree, tree2)

    def test_simplest_constructor(self):
        """ Test cross functions for various hash types. """

        for hashtype in HashTypes:
            self.do_test_cross_functions(hashtype)


if __name__ == '__main__':
    unittest.main()
