#!/usr/bin/env python3
# testNLHBase.py

""" Test basic NLHTree functions. """

import hashlib
import sys
import time
import unittest

from rnglib import SimpleRNG
from nlhtree.base import NLHBase
# from nlhtree import *

from xlattice import HashTypes  # , check_hashtype

if sys.version_info < (3, 6):
    # pylint: disable=unused-import
    import sha3     # monkey-patches hashlib


class TestNLHBase(unittest.TestCase):
    """ Test basic NLHTree functions. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def do_test_constructor(self, hashtype):
        """ Check functionality of NLHBase constructor for specifc hash. """

        name = self.rng.next_file_name(8)
        base = NLHBase(name, hashtype)
        self.assertEqual(base.name, name)
        self.assertEqual(base.hashtype, hashtype)
        root = base.root
        curt = base.cur_tree
        self.assertEqual(root.name, curt.name)

    def test_constructor(self):
        """ Check functionality of NLHBase constructor.  """

        for hashtype in HashTypes:
            self.do_test_constructor(hashtype)

    def do_test_with_simple_tree(self, hashtype):
        """ XXX STUB: test simple tree with specific hash. """

        # pylint:disable=redefined-variable-type
        if hashtype == HashTypes.SHA1:
            sha = hashlib.sha1()
        elif hashtype == HashTypes.SHA2:
            sha = hashlib.sha256()
        elif hashtype == HashTypes.SHA3:
            sha = hashlib.sha3_256()

        # XXX WORKING HERE
        _ = sha

    def test_simple_tree(self):
        """ XXX STUB: test building simple tree. """
        for hashtype in HashTypes:
            self.do_test_with_simple_tree(hashtype)


if __name__ == '__main__':
    unittest.main()
