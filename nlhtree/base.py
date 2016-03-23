# nlhtree_py/nlhtree/base.py

import binascii
import fnmatch
import os
import re
from stat import *
from xlattice.u import fileSHA1, fileSHA2
from xlattice.crypto import SP   # for getSpaces()
from nlhtree import NLHTree
from xlattice import (
    SHA1_BIN_LEN, SHA2_BIN_LEN,
    SHA1_HEX_LEN, SHA2_HEX_LEN,
    SHA1_BIN_NONE, SHA2_BIN_NONE)

__all__ = [
    'NLHBase',
]


class NLHBase(object):

    def __init__(self, name, usingSHA1):
        self._root = NLHTree(name, usingSHA1)   # immutable ref to a NLHTree
        self._curTree = self._root              # the current tree; mutable
        self._usingSHA1 = usingSHA1

    @property
    def name(self):
        return self._root.name

    @property
    def usingSHA1(self):
        return self._root.usingSHA1

    @property
    def root(self):
        return self._root

    @property
    def curTree(self):
        return self._curTree

    @curTree.setter
    def curTree(self, path):
        if not path or path == '':
            raise RuntimeError('path may not be None or empty')

        # needs to handle more complex cases
        path = path.strip()
        parts = path.split('/')             # many possible problems ignored
        if len(parts) == 0:
            # find a node with this name

            # if it's a leaf, error

            # otherwise set curTree to point to this node
            pass
        else:
            raise NotImplemented("can't handle multi-part paths yet")

            # XXX if the path begins with a forward slash ('/'), then
            # tentatively set the current tree to the root and then
            # apply the normal relpath logic from there
