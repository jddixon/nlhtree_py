# nlhtree_py/nlhtree/__init__.py

import binascii, fnmatch, os
from stat       import *
from xlattice.u import fileSHA1, fileSHA2

from xlattice   import (
        SHA1_BIN_LEN, SHA2_BIN_LEN, SHA1_BIN_NONE, SHA2_BIN_NONE)

__all__ = [ '__version__',      '__version_date__',
            'NLHBase',  'NLHNode',  'NLHLeaf',  'NLHTree',
        ]

__version__         = '0.2.0'
__version_date__    = '2015-05-22'


class NLHBase(object):

    def __init__(self, name):
        self._root = NLHTree(name)          # immutable ref to a NLHTree
        self._curTree = self._root          # the current tree; mutable

    @property
    def name(self):
        return self._root.name

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

    def __eq__(self, other):
        if other == None:
            return False
        if not isinstance(other, NLHLeaf):
            return False
        return (self.name == other.name) and (self._hash == other._hash)

    @staticmethod
    def createFromFileSystem(path, name, usingSHA1=False):
        """
        Create an NLHLeaf from the contents of the file at **path**.
        The name is part of the path but is passed to simplify the code.
        Returns None if the file cannot be found.
        """
        if os.path.exists(path):
            if usingSHA1:
                hash = fileSHA1(path)
            else:
                hash = fileSHA2(path)
            bHash = binascii.a2b_hex(hash)
            return NLHLeaf(name, bHash)
        else:
            return None

class NLHTree(NLHNode):
    def __init__(self, name):
        super().__init__(name)
        self._nodes = []

    @property
    def isLeaf(self):
        return False

    @property
    def nodes(self):
        return self._nodes

    def __eq__(self, other):
        if other == None:
            return False
        if not isinstance(other, NLHTree):
            return False
        if self.name != other.name:
            return False
        if len(self._nodes) != len(other._nodes):
            return False
        for i in range(len(self._nodes)):
            if not self._nodes[i] == other._nodes[i]:
                return False
        return True

    def delete(self, pat):
        """
        Delete nodes whose names match the pattern.  This is
        a glob, as in UNIX-style file name pattern matching.
        """

        remainder = []
        for node in self.nodes:
            if not fnmatch.fnmatch(node.name, pat):
                remainder.append(node) 
        if len(remainder) != len(self._nodes):
            self._nodes = remainder

    def find(self, pat):
        """
        Return a list of nodes whose names match the pattern.  This is
        a glob, as in UNIX-style file name pattern matching.  The list
        is guaranteed to be sorted by node name.
        """
        matches = []
        for node in self.nodes:
            if fnmatch.fnmatch(node.name, pat):
                matches.append(node)
        return matches

    def insert(self, node):
        """ 
        Insert an NLHNode into the tree's list of nodes, maintaining
        sort order.  If a node with the same name already exists, an
        exception will be raised.
        """
        # XXX need checks
        lenNodes = len(self._nodes)
        name = node.name
        done = False
        for i in range(lenNodes):
            iName = self._nodes[i].name
            if name < iName:
                # insert before
                if i == 0:
                    self._nodes = [node] + self._nodes
                    done = True
                    break
                else:
                    before = self._nodes[0:i]
                    after  = self._nodes[i:]
                    self._nodes  = before + [node] + after
                    done = True
                    break
            elif name == iName:
                raise RuntimeException(
                    "attempt to add two nodes with the same name: '%s'" % name)
        if not done:
            self._nodes.append(node)

    def list(self, pat):
        """
        Return a sorted list of node names.  If the node is a tree,
        its name is preceded by '* ', a an asterisk followed by a 
        space.  Otherwise the node's name is preceded by two spaces.
        """
        el = []
        for q in self._nodes:
            if fnmatch.fnmatch(q.name, pat):
                if q.isLeaf:
                    el.append('  ' + q.name)
                else:
                    el.append('* ' + q.name)
        return el

    @staticmethod
    def createFromFileSystem(pathToDir, usingSHA1 = False, 
                                        exRE = None, matchRE = None):
        """
        Create an NLHTree based on the information in the directory
        at pathToDir.  The name of the directory will be the last component
        of pathToDir.  Return the NLHTree.
        """
        if not pathToDir:
            raise RuntimeError("cannot create a NLHTree, no path set")
        if not os.path.exists(pathToDir):
            raise RuntimeError(
                "NLHTree: directory '%s' does not exist" % pathToDir)
        (path, junk, name) = pathToDir.rpartition('/')
        if path == '':
            raise RuntimeError("cannot parse path " + pathToDir)

        tree = NLHTree(name)

        # Create data structures for constituent files and subdirectories
        # These are sorted by the bare name
        files = os.listdir(pathToDir)  # empty if you just append .sort()
        files.sort()                    # sorts in place
        if files:
            for file in files:
                # exclusions take priority over matches
                if exRE and exRE.search(file):
                    continue
                if matchRE and not matchRE.search(file):
                    continue
                node = None
                pathToFile = os.path.join(pathToDir, file)
                s = os.lstat(pathToFile)        # ignores symlinks
                mode = s.st_mode
                # os.path.isdir(path) follows symbolic links
                if S_ISDIR(mode):
                    node = NLHTree.createFromFileSystem(
                            pathToFile, usingSHA1,exRE, matchRE)
                # S_ISLNK(mode) is true if symbolic link
                # isfile(path) follows symbolic links
                elif os.path.isfile(pathToFile):        # S_ISREG(mode):
                    node = NLHLeaf.createFromFileSystem(
                                pathToFile, file, usingSHA1)
                # otherwise, just ignore it ;-)

                if node:
                    tree._nodes.append(node)

        return tree
