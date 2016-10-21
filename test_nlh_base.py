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

from xlattice import Q  # , check_using_sha

if sys.version_info < (3, 6):
    # pylint: disable=unused-import
    import sha3     # monkey-patches hashlib


class TestNLHBase(unittest.TestCase):
    """ Test basic NLHTree functions. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def do_test_constructor(self, using_sha):
        """ Check functionality of NLHBase constructor for specifc hash. """

        name = self.rng.next_file_name(8)
        base = NLHBase(name, using_sha)
        self.assertEqual(base.name, name)
        self.assertEqual(base.using_sha, using_sha)
        root = base.root
        curt = base.cur_tree
        self.assertEqual(root.name, curt.name)

    def test_constructor(self):
        """ Check functionality of NLHBase constructor.  """

        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_constructor(using)

    def do_test_with_simple_tree(self, using_sha):
        """ XXX STUB: test simple tree with specific hash. """

        # pylint:disable=redefined-variable-type
        if using_sha == Q.USING_SHA1:
            sha = hashlib.sha1()
        elif using_sha == Q.USING_SHA2:
            sha = hashlib.sha256()
        elif using_sha == Q.USING_SHA3:
            sha = hashlib.sha3_256()

        # XXX WORKING HERE
        _ = sha

    def test_simple_tree(self):
        """ XXX STUB: test building simple tree. """
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_with_simple_tree(using)


if __name__ == '__main__':
    unittest.main()
