# nlhtree_py/nlhtree/__init__.py

import binascii
from xlattice   import (
        SHA1_BIN_LEN, SHA2_BIN_LEN,
        SHA1_BIN_NONE, SHA2_BIN_NONE)

__all__ = [ '__version__',      '__version_date__',
            'NLHBase',  'NLHNode',  'NLHLeaf',  'NLHTree',
        ]

__version__         = '0.1.0'
__version_date__    = '2015-05-21'


class NLHBase(object):

    def __init__(self, name):
        self._root = nlhTree(name)          # immutable ref to a NLHTree
        self._curTree = self._root          # the current tree; mutable

    @property
    def root(self):
        return self._root

    @property
    def curTree(self):
        return self._curTree.name
    @curTree.setter
    def curTree(self, path):
        if not path or path == '':
            raise RuntimeError('path may not be None or empty')

        # needs to handle more complex cases
        path = path.strip()
        parts = path.strip('/')             # many possible problems ignored
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

    @property
    def root(self):
        return self._root                   # ref to an NLHTree


class NLHNode(object):

    def __init__(self, name):
        # XXX needs checks
        self._name = name

    @property
    def name(self):
        return self._name

    @property
    def isLeaf(self):
        raise NotImplemented()

    @staticmethod
    def checkHash(hash):
        """ return True if SHA1, False if SHA2, otherwise raise """
        if hash == None:
            raise RuntimeError('hash cannot be None')
        hashLen = len(hash)
        if hashLen == SHA1_BIN_LEN:
            return True
        elif hashLen == SHA2_BIN_LEN:
            return False
        else:
            raise RuntimeError('not a valid SHA hash length')

class NLHLeaf(NLHNode):

    def __init__(self, name, hash):
        super().__init__(name)
        NLHNode.checkHash(hash)             # exception if check fails
        self._hash = hash

    @property
    def hexHash(self):
        return binascii.b2a_hex(self._hash, 'ascii')

    @property
    def binHash(self):
        return self._hash

    @property
    def isLeaf(self):
        return True

    @property
    def usingSHA1(self):
        return checkHash(self._hash)

class NLHTree(NLHNode):
    def __init__(self, name):
        super().__init__(name)
        self._nodes = []

    @property
    def isLeaf(self):
        return False

    def insert(self, node):
        # XXX need checks
        lenNodes = len(self._nodes)
        if lenNodes == 0:
            self._nodes.append(node)
        else:
            name = node.name
            for i in range(lenNodes):
                iName = self._nodes[i]
                if name > iName:
                    # insert before
                    if i == 0:
                        self._nodes = [node] + self._nodes  
                    else:
                        before = self._nodes[0:i-1]
                        after  = self._nodes[i:]
                        self._nodes  = before + [node] + after
