# nlhtree_py/nlhtree/__init__.py

import binascii
import fnmatch
import itertools
import os
import re
import sys
from stat import *

from xlattice.crypto import SP   # for getSpaces()
from xlattice.u import (fileSHA1Hex, fileSHA2Hex, UDir)

from xlattice import (
    SHA1_BIN_LEN, SHA2_BIN_LEN,
    SHA1_HEX_LEN, SHA2_HEX_LEN,
    SHA1_BIN_NONE, SHA2_BIN_NONE,
    SHA1_HEX_NONE, SHA2_HEX_NONE)

__all__ = ['__version__', '__version_date__',
           'NLHNode', 'NLHLeaf', 'NLHTree',
           ]

__version__ = '0.4.28'
__version_date__ = '2016-07-22'


class NLHError(RuntimeError):
    pass


class NLHParseError(NLHError):
    pass


class NLHNode(object):

    def __init__(self, name, usingSHA1=False):
        # XXX needs checks
        self._name = name
        self._usingSHA1 = usingSHA1
        self._binHash = None

    @property
    def name(self):
        return self._name

    @property
    def usingSHA1(self):
        return self._usingSHA1

    @property
    def hexHash(self):
        if self._binHash is None:
            if self._usingSHA1:
                return SHA1_HEX_NONE
            else:
                return SHA2_HEX_NONE
        else:
            return str(binascii.b2a_hex(self._binHash), 'ascii')

    @hexHash.setter
    def hexHash(self, value):
        if self._binHash:
            raise NLHError('attempt to set non-null hash')
        self._binHash = bytes(binascii.a2b_hex(value))

    @property
    def binHash(self):
        return self._binHash

    @binHash.setter
    def binHash(self, value):
        if self._binHash:
            raise NLHError('attempt to set non-null hash')
        self._binHash = value

    @staticmethod
    def checkHash(hash):
        """ return True if SHA1, False if SHA2, otherwise raise """
        if hash is None:
            raise NLHError('hash cannot be None')
        hashLen = len(hash)
        if hashLen == SHA1_BIN_LEN:
            return True
        elif hashLen == SHA2_BIN_LEN:
            return False
        else:
            raise NLHError('not a valid SHA hash length')

    def __eq__(self):
        raise NotImplementedError

    def clone(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError


class NLHLeaf(NLHNode):

    def __init__(self, name, hash):
        usingSHA1 = NLHNode.checkHash(hash)   # exception if check fails
        super().__init__(name, usingSHA1)

        # XXX VERIFY HASH IS WELL-FORMED

        if hash:
            self._binHash = hash
        else:
            self._binHash = None

        self.iterUsed = False

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, NLHLeaf):
            return False
        return (self._name == other._name) and (
            self._binHash == other._binHash)

    def _toString(self, indent):
        return "%s%s %s" % (
            SP.getSpaces(indent),
            self._name,
            self.hexHash)

    def clone(self):
        """ make a deep copy """
        return NLHLeaf(self._name, self._binHash)

    # ITERABLE ############################################

    def __iter__(self):
        return self

    def __next__(self):
        if self.iterUsed:
            raise StopIteration
        else:
            self.iterUsed = True
            return (self._name, self.hexHash)

    # END ITERABLE ########################################

    @staticmethod
    def createFromFileSystem(path, name, usingSHA1=False):
        """
        Create an NLHLeaf from the contents of the file at **path**.
        The name is part of the path but is passed to simplify the code.
        Returns None if the file cannot be found.
        """
        if os.path.exists(path):
            if usingSHA1:
                hash = fileSHA1Hex(path)
            else:
                hash = fileSHA2Hex(path)
            bHash = binascii.a2b_hex(hash)
            return NLHLeaf(name, bHash)
        else:
            return None


class NLHTree(NLHNode):

    # notice the terminating forward slash and lack of newlines or CR-LF
    DIR_LINE_RE = re.compile(r'^( *)([a-z0-9_\$\+\-\.~]+/?)$',
                             re.IGNORECASE)
    FILE_LINE_RE_1 = re.compile(r'^( *)([a-z0-9_\$\+\-\.:~]+/?) ([0-9a-f]{40})$',
                                re.IGNORECASE)

    FILE_LINE_RE_2 = re.compile(r'^( *)([a-z0-9_\$\+\-\.:~]+/?) ([0-9a-f]{64})$',
                                re.IGNORECASE)

    def __init__(self, name, usingSHA1=False):
        super().__init__(name, usingSHA1)
        self._nodes = []
        self._n = -1            # duplication seems necessary
        self._prefix = ''       # ditto

    @property
    def nodes(self):
        return self._nodes

    def __eq__(self, other):

        if other is None:
            return False
        if not isinstance(other, NLHTree):
            return False
        if self._name != other._name:
            return False
        if self.usingSHA1 != other.usingSHA1:
            return False
        if len(self._nodes) != len(other._nodes):
            return False
        for i in range(len(self._nodes)):
            if not self._nodes[i] == other._nodes[i]:
                return False
        return True

    def clone(self):
        """ return a deep copy of the tree """
        tree = NLHTree(self._name, self.usingSHA1)
        for node in self._nodes:
            tree.insert(node)
        return tree

    def delete(self, pat):
        """
        Delete nodes whose names match the pattern.  This is
        a glob, as in UNIX-style file name pattern matching.
        """

        remainder = []
        for node in self._nodes:
            if not fnmatch.fnmatch(node._name, pat):
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
        for node in self._nodes:
            if fnmatch.fnmatch(node._name, pat):
                matches.append(node)
        return matches

    def insert(self, node):
        """
        Insert an NLHNode into the tree's list of nodes, maintaining
        sort order.  If a node with the same name already exists, an
        exception will be raised.
        """
        if node.usingSHA1 != self.usingSHA1:
            raise NLHError("incompatible SHA types")
        # XXX need checks
        lenNodes = len(self._nodes)
        name = node._name
        done = False
        for i in range(lenNodes):
            iName = self._nodes[i]._name
            if name < iName:
                # insert before
                if i == 0:
                    self._nodes = [node] + self._nodes
                    done = True
                    break
                else:
                    before = self._nodes[0:i]
                    after = self._nodes[i:]
                    self._nodes = before + [node] + after
                    done = True
                    break
            elif name == iName:
                raise NLHError(
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
            if fnmatch.fnmatch(q._name, pat):
                if isinstance(q, NLHLeaf):
                    el.append('  ' + q._name)
                else:
                    el.append('* ' + q._name)
        return el

    def __str__(self):
        ss = []
        self.toStrings(ss, 0)
        s = '\n'.join(ss) + '\n'
        return s

    def toStrings(self, ss, indent=0):
        ss.append("%s%s" % (SP.getSpaces(indent), self._name))
        for node in self._nodes:
            if isinstance(node, NLHLeaf):
                ss.append(node._toString(indent + 1))
            else:
                node.toStrings(ss, indent + 1)

    @staticmethod
    def createFromFileSystem(pathToDir, usingSHA1=False,
                             exRE=None, matchRE=None):
        """
        Create an NLHTree based on the information in the directory
        at pathToDir.  The name of the directory will be the last component
        of pathToDir.  Return the NLHTree.
        """
        if not pathToDir:
            raise NLHError("cannot create a NLHTree, no path set")
        if not os.path.exists(pathToDir):
            raise NLHError(
                "NLHTree.createFromFileSystem: directory '%s' does not exist" % pathToDir)
        (path, junk, name) = pathToDir.rpartition('/')
        if path == '':
            raise NLHError("cannot parse path " + pathToDir)

        tree = NLHTree(name, usingSHA1)

        # Create data structures for constituent files and subdirectories
        # These are sorted by the bare name
        # empty if you just append .sort()
        files = sorted(os.listdir(pathToDir))
        if files:
            for file in files:
                # exclusions take priority over matches
                if exRE and exRE.match(file):
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
                        pathToFile, usingSHA1, exRE, matchRE)
                # S_ISLNK(mode) is true if symbolic link
                # isfile(path) follows symbolic links
                elif os.path.isfile(pathToFile):        # S_ISREG(mode):
                    node = NLHLeaf.createFromFileSystem(
                        pathToFile, file, usingSHA1)
                # otherwise, just ignore it ;-)

                if node:
                    tree._nodes.append(node)

        return tree

    @staticmethod
    def parseFirstLine(s):
        """
        Return the name found in the first line or raise an exception.
        """
        m = NLHTree.DIR_LINE_RE.match(s)
        if not m:
            raise NLHParseError("first line doesn't match expected pattern")
        if len(m.group(1)) != 0:
            raise NLHParseError("unexpected indent on first line")
        return m.group(2)   # the name

    @staticmethod
    def parseOtherLine(s):
        """
        Return the indent (the number of spaces), the name on the line,
        and other None or the hash found.
        """

        m = NLHTree.DIR_LINE_RE.match(s)
        if m:
            return len(m.group(1)), m.group(2), None

        m = NLHTree.FILE_LINE_RE_1.match(s)
        if m:
            return len(m.group(1)), m.group(2), m.group(3)

        m = NLHTree.FILE_LINE_RE_2.match(s)
        if m:
            return len(m.group(1)), m.group(2), m.group(3)

        raise NLHParseError("can't parse line: '%s'" % s)

    @staticmethod
    def createFromStringArray(ss, usingSHA1=False):
        # at entry, we don't know whether the string array uses
        # SHA1 or SHA256

        if len(ss) == 0:
            return None

        name = NLHTree.parseFirstLine(ss[0])
        root = curLevel = NLHTree(name, usingSHA1)     # our first push
        stack = [root]
        depth = 0

        ss = ss[1:]
        for line in ss:
            indent, name, hash = NLHTree.parseOtherLine(line)
            if hash is not None:
                bHash = binascii.a2b_hex(hash)

            if indent > depth + 1:
                # DEBUG
                print("IMPOSSIBLE: indent %d, depth %d" % (indent, depth))
                # END
                if hash:
                    leaf = NLHLeaf(name, bHash)
                    stack[depth].insert(leaf)
                else:
                    subTree = NLHTree(name, usingSHA1)
                    stack.append(subTree)
                    depth += 1
            elif indent == depth + 1:
                if hash is None:
                    subTree = NLHTree(name, usingSHA1)
                    stack[depth].insert(subTree)
                    stack.append(subTree)
                    depth += 1
                else:
                    leaf = NLHLeaf(name, bHash)
                    stack[depth].insert(leaf)

            else:
                while indent < depth + 1:
                    stack.pop()
                    depth -= 1
                if hash is None:
                    subTree = NLHTree(name, usingSHA1)
                    stack[depth].insert(subTree)
                    stack.append(subTree)
                    depth += 1
                else:
                    leaf = NLHLeaf(name, bHash)
                    stack[depth].insert(leaf)

        return root

    @staticmethod
    def parseFile(pathToFile, usingSHA1):
        with open(pathToFile, 'r') as f:
            s = f.read()
        return NLHTree.parse(s, usingSHA1)

    @staticmethod
    def parse(s, usingSHA1):
        if not s or s == '':
            raise NLHParseError('cannot parse an empty string')
        ss = s.split('\n')
        if ss[-1] == '':
            ss = ss[:-1]
        return NLHTree.createFromStringArray(ss, usingSHA1)

    # DATA_DIR/U_DIR INTERACTION ------------------------------------

    def checkInDataDir(self, dataDir):
        """
        Walk the tree, verifying that all leafs (files) can be found in
        dataDir by relative path and that the content key is correct.  This
        does NOT verify that all files have corresponding leaf nodes.

        dataDir is a path, the last component of which is the name of
        the data directory and so also the name of the NLHTree.
        """

        # if / not found, holder, the holding directory, is an empty string.
        # Return a list of leaf nodes which are not matched.  If everything
        # is OK this will be empty.

        holder, delim, dirName = dataDir.rpartition('/')
        if delim == '':
            holder = ''
        unmatched = []
        for couple in self:
            if len(couple) == 1:
                # it's a directory
                pass
            else:
                relPath = couple[0]
                hash = couple[1]
                path = os.path.join(holder, relPath)
                if not os.path.exists(path):
                    unmatched.append(path)
        return unmatched

    def checkInUDir(self, uPath):
        """
        Walk the tree, verifying that all leaf nodes have corresponding
        files in uDir, files with the same content key.
        """

        uDir = UDir.discover(uPath, usingSHA1=self.usingSHA1)

        unmatched = []
        for couple in self:
            if len(couple) == 1:
                # it's a directory
                pass
            else:
                relPath = couple[0]
                hash = couple[1]
                if not uDir.exists(hash):
                    unmatched.append((relPath, hash,))
        return unmatched

    def dropFromUDir(self, uPath):
        """ Remove all leaf nodes in this NLHTree from uDir """

        uDir = UDir.discover(uPath, usingSHA1=self.usingSHA1)

        unmatched = []
        for couple in self:
            if len(couple) == 1:
                # it's a directory
                pass
            else:
                hash = couple[1]
                ok = uDir.delete(hash)
                if not ok:
                    relPath = couple[0]
                    unmatched.append((relPath, hash,))
        return unmatched

    def populateDataDir(self, uPath, path):
        """
        path is the path to the data directory, excluding the name
        of the directory itself, which will be the name of the tree
        """
        if not os.path.exists(uPath):
            raise NLHError(
                "populateDataDir: uPath '%s' does not exist" % uPath)

        uDir = UDir.discover(uPath, usingSHA1=self.usingSHA1)

        unmatched = []
        for couple in self:
            if len(couple) == 1:
                # it's a directory
                dir = os.path.join(path, couple[0])
                os.makedirs(dir, mode=0o755, exist_ok=True)
            elif len(couple) == 2:
                hash = couple[1]
                if not uDir.exists(hash):
                    unmatched.append(hash)
                else:
                    data = uDir.getData(hash)

                    pathToFile = os.path.join(path, couple[0])
                    with open(pathToFile, 'wb') as f:
                        f.write(data)
            else:
                print("degenerate/malformed tuple of length %d" % len(couple))

        return unmatched

    def saveToUDir(self, dataDir,
                   uPath=os.environ['DVCZ_UDIR'], usingSHA1=False):
        """
        Given an NLHTree for the data directory, walk the tree, copying
        all files present in dataDir into uPath by content key.  We assume
        that uPath is well-formed.
        """

        # the last part of dataDir is the name of the tree
        (path, junk, name) = dataDir.rpartition('/')
        if name != self.name:
            raise "name of directory (%s) does not match name of tree (%s)"

        # DEBUG
        #print("saveToUDir %s ==> %s" % (dataDir, uPath))
        #print("  path => '%s'" % path)
        # END

        u = UDir.discover(uPath, usingSHA1=self.usingSHA1)

        unmatched = []
        for couple in self:
            if len(couple) == 1:
                # DEBUG
                #print("  DIR:  %s" % couple[0])
                # END
                continue                   # it's a directory

            elif len(couple) == 2:
                relPath = couple[0]
                hash = couple[1]
                pathToFile = os.path.join(path, relPath)
                # DEBUG
                #print("  FILE: %s" % pathToFile)
                # END
                if not os.path.exists(pathToFile):
                    # DEBUG
                    #print("path does not exist: %s" % pathToFile)
                    # END
                    unmatched.append(path)
                else:
                    u.copyAndPut(pathToFile, hash)
            else:
                s = []
                for part in couple:
                    s.append(part.__str__())
                unmatched.append(':'.join(s))
                print(
                    "INTERNAL ERROR: node is neither Tree nor Leaf\n  %s" %
                    s)

        return unmatched

    # ITERATORS #####################################################

    @staticmethod
    def walkFile(pathToFile):
        """
        For each line in the NLHTree listing, return either the
        relative path to a directory (including the directory name)
        or the relative path to a file plus its SHA1 hex hash.
        Each of these is a tuple: the former is a singleton, and the
        latter is a 2-tuple.

        The path to the listing file is NOT included in these relative
        paths.
        """
        if not os.path.exists(pathToFile):
            raise NLHError('file not found: ' + pathToFile)
        curDepth = 0
        path = ''
        parts = []
        hashLen = -1
        usingSHA1 = False

        with open(pathToFile, 'r') as f:
            line = f.readline()
            lineNbr = 0
            while line:
                done = False

                # -- dir --------------------------------------------
                m = NLHTree.DIR_LINE_RE.match(line)
                if m:
                    depth = len(m.group(1))
                    dirName = m.group(2)
                    if depth == curDepth:
                        parts.append(dirName)
                        curDepth += 1
                    elif depth < curDepth:
                        parts[depth] = dirName
                        parts = parts[:depth + 1]
                    else:
                        raise NLHError("corrupt nlhTree listing")
                    path = '/'.join(parts)

                    yield (path, )
                    done = True

                # -- file -------------------------------------------
                if not done:
                    m = NLHTree.FILE_LINE_RE_1.match(line)
                    if m:
                        curDepth = len(m.group(1))
                        fileName = m.group(2)
                        hash = m.group(3)
                        yield (os.path.join(path, fileName), hash)
                        done = True
                # -- error ------------------------------------------
                if not done:
                    yield ("DUNNO WHAT THIS IS: %s" % line, )
                    done = True
                line = f.readline()
                lineNbr += 1

    @staticmethod
    def walkString(s):
        """
        s is an NLHTree listing in the form of a single string with
        lines ending with newlines.  There is a newline at the end of
        the listing.
        """
        lines = s.split('\n')
        if lines[-1] == '':
            lines = lines[:-1]          # drop the last line if empty
        return NLHTree.walkStrings(lines)

    @staticmethod
    def walkStrings(ss):
        """
        For each line in the NLHTree listing, return either the
        relative path to a directory (including the directory name)
        or the relative path to a file plus its SHA1 hex hash.
        Each of these is a tuple: the former is a singleton, and the
        latter is a 2-tuple.

        The NLHTree listing is in the form of a list of lines.

        COMMENTS AND BLANK LINES ARE NOT YET SUPPORTED.
        """

        curDepth = 0
        path = ''
        parts = []
        hashLen = -1
        usingSHA1 = False

        for lineNbr, line in enumerate(ss):
            done = False

            # -- dir --------------------------------------------
            m = NLHTree.DIR_LINE_RE.match(line)
            if m:
                depth = len(m.group(1))
                dirName = m.group(2)
                if depth == curDepth:
                    parts.append(dirName)
                    curDepth += 1
                elif depth < curDepth:
                    parts[depth] = dirName
                    parts = parts[:depth + 1]
                else:
                    raise NLHError("corrupt nlhTree listing")
                path = '/'.join(parts)

                yield (path, )
                done = True

            # -- file -------------------------------------------
            if not done:
                m = NLHTree.FILE_LINE_RE_1.match(line)
                if m:
                    curDepth = len(m.group(1))
                    fileName = m.group(2)
                    hash = m.group(3)
                    yield (os.path.join(path, fileName), hash)
                    done = True
            # -- error ------------------------------------------
            if not done:
                yield ("DUNNO WHAT THIS IS: %s" % line, )
                done = True

    # ITERABLE ############################################

    def __iter__(self):

        self._n = -1
        self._subTree = None
        self._prefix = ''
        return self

    def __next__(self):

        # For the first call:
        if self._n < 0:
            self._n += 1
            return (os.path.join(self._prefix, self._name), )

        if self._n >= len(self._nodes):
            raise StopIteration

        if self._subTree:
            try:
                couple = self._subTree.__next__()
                return couple
            except StopIteration:
                self._subTree = None
                self._n += 1
                if self._n >= len(self._nodes):
                    raise StopIteration

        nextNode = self._nodes[self._n]
        if isinstance(nextNode, NLHLeaf):
            self._n += 1
            return (os.path.join(self._prefix,
                                 os.path.join(self._name, nextNode._name)),
                    nextNode.hexHash,)
        else:
            self._subTree = nextNode.__iter__()

            self._subTree._prefix = os.path.join(self._prefix, self._name)

            return self._subTree.__next__()

    # END ITERABLE ########################################
