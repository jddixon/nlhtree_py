# nlhtree_py/nlhtree/base.py

import binascii
import fnmatch
import os
import re
from stat import *
from xlattice.crypto import SP   # for get_spaces()
from nlhtree import NLHTree
from xlattice import (
    SHA1_BIN_LEN, SHA2_BIN_LEN,
    SHA1_HEX_LEN, SHA2_HEX_LEN,
    SHA1_BIN_NONE, SHA2_BIN_NONE)

__all__ = [
    'NLHBase',
]


class NLHBase(object):

    def __init__(self, name, using_sha):
        self._root = NLHTree(name, using_sha)   # immutable ref to a NLHTree
        self._cur_tree = self._root              # the current tree; mutable
        self._using_sha = using_sha

    @property
    def name(self):
        return self._root.name

    @property
    def using_sha(self):
        return self._root.using_sha

    @property
    def root(self):
        return self._root

    @property
    def cur_tree(self):
        return self._cur_tree

    @cur_tree.setter
    def cur_tree(self, path):
        if not path or path == '':
            raise RuntimeError('path may not be None or empty')

        # needs to handle more complex cases
        path = path.strip()
        parts = path.split('/')             # many possible problems ignored
        if len(parts) == 0:
            # find a node with this name

            # if it's a leaf, error

            # otherwise set cur_tree to point to this node
            pass
        else:
            raise NotImplementedError("can't handle multi-part paths yet")

            # XXX if the path begins with a forward slash ('/'), then
            # tentatively set the current tree to the root and then
            # apply the normal relpath logic from there

    # SYNONYMS ------------------------------------------------------
    @property
    def usingSHA(self):
        return self.using_sha

    @property
    def curTree(self):
        return self._cur_tree

    @curTree.setter
    def curTree(self, path):
        self.cur_tree = path

    # END SYN -------------------------------------------------------
