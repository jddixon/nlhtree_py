# nlhtree_py/nlhtree/__init__.py

import binascii
import fnmatch
import itertools
import os
import re
import sys
from stat import *

from xlattice import Q, check_using_sha
from xlattice.crypto import SP   # for get_spaces()
from xlattice.u import (file_sha1hex, file_sha2hex, file_sha3hex, UDir)

from xlattice import (
    SHA1_BIN_LEN, SHA1_HEX_LEN, SHA1_BIN_NONE, SHA1_HEX_NONE,
    SHA2_BIN_LEN, SHA2_HEX_LEN, SHA2_BIN_NONE, SHA2_HEX_NONE,
    SHA3_BIN_LEN, SHA3_HEX_LEN, SHA3_BIN_NONE, SHA3_HEX_NONE)

__all__ = ['__version__', '__version_date__',
           'NLHNode', 'NLHLeaf', 'NLHTree',
           ]

__version__ = '0.7.0'
__version_date__ = '2016-10-20'


class NLHError(RuntimeError):
    pass


class NLHParseError(NLHError):
    pass


class NLHNode(object):

    def __init__(self, name, using_sha=Q.USING_SHA2):
        check_using_sha(using_sha)
        self._name = name.strip()
        self._using_sha = using_sha
        self._bin_hash = None

    @property
    def name(self):
        return self._name

    @property
    def using_sha(self):
        return self._using_sha

    @property
    def hex_hash(self):
        if self._bin_hash is None:
            if self._using_sha == Q.USING_SHA1:
                return SHA1_HEX_NONE
            elif self._using_sha == Q.USING_SHA2:
                return SHA2_HEX_NONE
            elif self._using_sha == Q.USING_SHA3:
                return SHA3_HEX_NONE
        else:
            return str(binascii.b2a_hex(self._bin_hash), 'ascii')

    @hex_hash.setter
    def hex_hash(self, value):
        if self._bin_hash:
            raise NLHError('attempt to set non-null hash')
        self._bin_hash = bytes(binascii.a2b_hex(value))

    @property
    def bin_hash(self):
        return self._bin_hash

    @bin_hash.setter
    def bin_hash(self, value):
        if self._bin_hash:
            raise NLHError('attempt to set non-null hash')
        self._bin_hash = value

    @staticmethod
    def check_hash(bin_hash, using_sha):
        """ raise if inappropriate bin_hash length"""

        if bin_hash is None:
            raise NLHError('binary hash cannot be None')
        bin_hash_len = len(bin_hash)
        if bin_hash_len != SHA1_BIN_LEN and \
                bin_hash_len != SHA2_BIN_LEN and \
                bin_hash_len != SHA3_BIN_LEN:
            raise NLHError('not a valid SHA binary hash length')

    def __eq__(self, other):
        raise NotImplementedError

    def clone(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError

    # SYNONYMS ------------------------------------------------------
    @property
    def usingSHA(self):
        """ SYNONYM """
        return self.using_sha

    @property
    def hexHash(self):
        """ SYNONYM """
        return self.hex_hash

    @hexHash.setter
    def hexHash(self, value):
        """ SYNONYM """
        self.hex_hash(value)

    @property
    def binHash(self):
        """ SYNONYM """
        return self.bin_hash

    @binHash.setter
    def binHash(self, value):
        """ SYNONYM """
        self._bin_hash(value)

    @staticmethod
    def checkHash(bin_hash, using_sha):
        """ SYNONYM """
        NLHNode.check_hash(bin_hash, using_sha)

    # END SYN -------------------------------------------------------


class NLHLeaf(NLHNode):

    def __init__(self, name, bin_hash, using_sha):
        # exception if check fails
        NLHNode.check_hash(bin_hash, using_sha)
        super().__init__(name, using_sha)

        if bin_hash:
            self._bin_hash = bin_hash
        else:
            self._bin_hash = None

        self.iter_used = False

    def __eq__(self, other):
        if other is None:
            return False
        if not isinstance(other, NLHLeaf):
            return False
        return (self._name == other._name) and (
            self._bin_hash == other._bin_hash)

    def _toString(self, indent):
        return "%s%s %s" % (
            SP.get_spaces(indent),
            self._name,
            self.hex_hash)

    def clone(self):
        """ make a deep copy """

        hash_len = len(self._bin_hash)
        if hash_len == SHA1_BIN_LEN:
            using_sha = Q.USING_SHA1
        elif hash_len == SHA2_BIN_LEN:
            using_sha = Q.USING_SHA2
        elif hash_len == SHA3_BIN_LEN:
            using_sha = Q.USING_SHA3

        return NLHLeaf(self._name, self._bin_hash, using_sha)

    # ITERABLE ############################################

    def __iter__(self):
        return self

    def __next__(self):
        if self.iter_used:
            raise StopIteration
        else:
            self.iter_used = True
            return (self._name, self.hex_hash)

    # END ITERABLE ########################################

    @staticmethod
    def create_from_file_system(path, name, using_sha=Q.USING_SHA2):
        """
        Create an NLHLeaf from the contents of the file at **path**.
        The name is part of the path but is passed to simplify the code.
        Returns None if the file cannot be found.
        """
        if os.path.exists(path):
            if using_sha == Q.USING_SHA1:
                hash = file_sha1hex(path)
            elif using_sha == Q.USING_SHA2:
                hash = file_sha2hex(path)
            elif using_sha == Q.USING_SHA3:
                hash = file_sha3hex(path)
            bHash = binascii.a2b_hex(hash)
            return NLHLeaf(name, bHash, using_sha)
        else:
            return None

    # SYNONYMS ------------------------------------------------------
    @staticmethod
    def createFromFileSystem(path, name, using_sha=Q.USING_SHA2):
        return NLHLeaf.create_from_file_system(path, name, using_sha)

    # END SYN -------------------------------------------------------


class NLHTree(NLHNode):

    # notice the terminating forward slash and lack of newlines or CR-LF
    DIR_LINE_RE = re.compile(r'^( *)([a-z0-9_\$\+\-\.~]+/?)$',
                             re.IGNORECASE)
    FILE_LINE_RE_1 = re.compile(r'^( *)([a-z0-9_\$\+\-\.:~]+/?) ([0-9a-f]{40})$',
                                re.IGNORECASE)

    FILE_LINE_RE_2 = re.compile(r'^( *)([a-z0-9_\$\+\-\.:~]+/?) ([0-9a-f]{64})$',
                                re.IGNORECASE)

    FILE_LINE_RE_3 = re.compile(r'^( *)([a-z0-9_\$\+\-\.:~]+/?) ([0-9a-f]{64})$',
                                re.IGNORECASE)

    def __init__(self, name, using_sha=Q.USING_SHA2):
        super().__init__(name, using_sha)
        self._nodes = []
        self._n = -1            # duplication seems necessary
        self._prefix = ''       # ditto
        self._subTree = None    # for iterators

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
        if self.using_sha != other.using_sha:
            return False
        if len(self._nodes) != len(other._nodes):
            return False
        for i in range(len(self._nodes)):
            if not self._nodes[i] == other._nodes[i]:
                return False
        return True

    def clone(self):
        """ return a deep copy of the tree """
        tree = NLHTree(self._name, self.using_sha)
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
        if node.using_sha != self.using_sha:
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
        self.to_strings(ss, 0)
        s = '\n'.join(ss) + '\n'
        return s

    def to_strings(self, ss, indent=0):
        ss.append("%s%s" % (SP.get_spaces(indent), self._name))
        for node in self._nodes:
            if isinstance(node, NLHLeaf):
                ss.append(node._toString(indent + 1))
            else:
                node.to_strings(ss, indent + 1)

    @staticmethod
    def create_from_file_system(path_to_dir, using_sha=Q.USING_SHA2,
                                ex_re=None, match_re=None):
        """
        Create an NLHTree based on the information in the directory
        at path_to_dir.  The name of the directory will be the last component
        of path_to_dir.  Return the NLHTree.
        """
        if not path_to_dir:
            raise NLHError("cannot create a NLHTree, no path set")
        if not os.path.exists(path_to_dir):
            raise NLHError(
                "NLHTree.create_from_file_system: directory '%s' does not exist" % path_to_dir)
        (path, junk, name) = path_to_dir.rpartition('/')
        if path == '':
            raise NLHError("cannot parse path " + path_to_dir)

        tree = NLHTree(name, using_sha)

        # Create data structures for constituent files and subdirectories
        # These are sorted by the bare name
        # empty if you just append .sort()
        files = sorted(os.listdir(path_to_dir))
        if files:
            for file in files:
                # exclusions take priority over matches
                if ex_re and ex_re.match(file):
                    continue
                if match_re and not match_re.search(file):
                    continue
                node = None
                path_to_file = os.path.join(path_to_dir, file)
                s = os.lstat(path_to_file)        # ignores symlinks
                mode = s.st_mode
                # os.path.isdir(path) follows symbolic links
                if S_ISDIR(mode):
                    node = NLHTree.create_from_file_system(
                        path_to_file, using_sha, ex_re, match_re)
                # S_ISLNK(mode) is true if symbolic link
                # isfile(path) follows symbolic links
                elif os.path.isfile(path_to_file):        # S_ISREG(mode):
                    node = NLHLeaf.create_from_file_system(
                        path_to_file, file, using_sha)
                # otherwise, just ignore it ;-)

                if node:
                    tree._nodes.append(node)

        return tree

    @staticmethod
    def parse_first_line(s):
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
    def parse_other_line(s):
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
    def create_from_string_array(lines, using_sha=Q.USING_SHA2):
        # at entry, we don't know whether the string array uses
        # SHA1 or SHA256

        if len(lines) == 0:
            return None

        name = NLHTree.parse_first_line(lines[0])
        cur_level = NLHTree(name, using_sha)     # our first push
        root = cur_level
        stack = [root]
        depth = 0

        lines = lines[1:]
        for line in lines:
            indent, name, hash = NLHTree.parse_other_line(line)
            if hash is not None:
                bHash = binascii.a2b_hex(hash)

            if indent > depth + 1:
                # DEBUG
                print("IMPOSSIBLE: indent %d, depth %d" % (indent, depth))
                # END
                if hash:
                    leaf = NLHLeaf(name, bHash, using_sha)
                    stack[depth].insert(leaf)
                else:
                    subTree = NLHTree(name, using_sha)
                    stack.append(subTree)
                    depth += 1
            elif indent == depth + 1:
                if hash is None:
                    subTree = NLHTree(name, using_sha)
                    stack[depth].insert(subTree)
                    stack.append(subTree)
                    depth += 1
                else:
                    leaf = NLHLeaf(name, bHash, using_sha)
                    stack[depth].insert(leaf)

            else:
                while indent < depth + 1:
                    stack.pop()
                    depth -= 1
                if hash is None:
                    subTree = NLHTree(name, using_sha)
                    stack[depth].insert(subTree)
                    stack.append(subTree)
                    depth += 1
                else:
                    leaf = NLHLeaf(name, bHash, using_sha)
                    stack[depth].insert(leaf)

        return root

    @staticmethod
    def parseFile(path_to_file, using_sha):
        with open(path_to_file, 'r') as f:
            s = f.read()
        return NLHTree.parse(s, using_sha)

    @staticmethod
    def parse(s, using_sha):
        if not s or s == '':
            raise NLHParseError('cannot parse an empty string')
        ss = s.split('\n')
        if ss[-1] == '':
            ss = ss[:-1]
        return NLHTree.create_from_string_array(ss, using_sha)

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

        holder, delim, dir_name = dataDir.rpartition('/')
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

        uDir = UDir.discover(uPath, using_sha=self.using_sha)

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

        uDir = UDir.discover(uPath, using_sha=self.using_sha)

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

        uDir = UDir.discover(uPath, using_sha=self.using_sha)

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

                    path_to_file = os.path.join(path, couple[0])
                    with open(path_to_file, 'wb') as f:
                        f.write(data)
            else:
                print("degenerate/malformed tuple of length %d" % len(couple))

        return unmatched

    def saveToUDir(self, dataDir,
                   uPath=os.environ['DVCZ_UDIR'], using_sha=Q.USING_SHA2):
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

        u = UDir.discover(uPath, using_sha=self.using_sha)

        unmatched = []
        for couple in self:
            if len(couple) == 1:
                continue                   # it's a directory

            elif len(couple) == 2:
                relPath = couple[0]
                hash = couple[1]
                path_to_file = os.path.join(path, relPath)
                if not os.path.exists(path_to_file):
                    unmatched.append(path)
                else:
                    u.copyAndPut(path_to_file, hash)
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
    def walkFile(path_to_file, using_sha):
        """
        For each line in the NLHTree listing, return either the
        relative path to a directory (including the directory name)
        or the relative path to a file plus its SHA1 hex hash.
        Each of these is a tuple: the former is a singleton, and the
        latter is a 2-tuple.

        The path to the listing file is NOT included in these relative
        paths.
        """
        if not os.path.exists(path_to_file):
            raise NLHError('file not found: ' + path_to_file)
        curDepth = 0
        path = ''
        parts = []
        hash_len = -1

        with open(path_to_file, 'r') as f:
            line = f.readline()
            lineNbr = 0
            while line:
                done = False

                # -- dir --------------------------------------------
                m = NLHTree.DIR_LINE_RE.match(line)
                if m:
                    depth = len(m.group(1))
                    dir_name = m.group(2)
                    if depth == curDepth:
                        parts.append(dir_name)
                        curDepth += 1
                    elif depth < curDepth:
                        parts[depth] = dir_name
                        parts = parts[:depth + 1]
                    else:
                        raise NLHError("corrupt nlhTree listing")
                    path = '/'.join(parts)

                    yield (path, )
                    done = True

                # -- file -------------------------------------------
                if not done:
                    if using_sha == Q.USING_SHA1:
                        m = NLHTree.FILE_LINE_RE_1.match(line)
                    elif using_sha == Q.USING_SHA2:
                        m = NLHTree.FILE_LINE_RE_2.match(line)
                    elif using_sha == Q.USING_SHA3:
                        m = NLHTree.FILE_LINE_RE_3.match(line)
                    if m:
                        curDepth = len(m.group(1))
                        fileName = m.group(2)
                        hash = m.group(3)
                        yield (os.path.join(path, fileName), hash)
                        done = True
                    # DEBUG
                    else:
                        print("NO FILE LINE MATCH ON %s" % line)
                    # END

                line = f.readline()
                lineNbr += 1

    @staticmethod
    def _walk_strings(ss, using_sha=Q.USING_SHA2):
        curDepth = 0
        path = ''
        parts = []
        hash_len = -1

        for lineNbr, line in enumerate(ss):
            done = False

            # -- dir --------------------------------------------
            m = NLHTree.DIR_LINE_RE.match(line)
            if m:
                depth = len(m.group(1))
                dir_name = m.group(2)
                if depth == curDepth:
                    parts.append(dir_name)
                    curDepth += 1
                elif depth < curDepth:
                    parts[depth] = dir_name
                    parts = parts[:depth + 1]
                else:
                    raise NLHError("corrupt nlhTree listing")
                path = '/'.join(parts)

                yield (path, )
                done = True

            # -- file -------------------------------------------
            if not done:
                if using_sha == Q.USING_SHA1:
                    m = NLHTree.FILE_LINE_RE_1.match(line)
                elif using_sha == Q.USING_SHA2:
                    m = NLHTree.FILE_LINE_RE_2.match(line)
                elif using_sha == Q.USING_SHA3:
                    m = NLHTree.FILE_LINE_RE_3.match(line)
                else:
                    raise NotImplementedError()
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

    @staticmethod
    def walkString(s, using_sha=Q.USING_SHA2):
        """
        s is an NLHTree listing in the form of a single string with
        lines ending with newlines.  There is a newline at the end of
        the listing.
        """
        check_using_sha(using_sha)
        lines = s.split('\n')
        if lines[-1] == '':
            lines = lines[:-1]          # drop the last line if empty
        return NLHTree._walk_strings(lines, using_sha)

    @staticmethod
    def walkStrings(ss, using_sha=Q.USING_SHA2):
        """
        For each line in the NLHTree listing, return either the
        relative path to a directory (including the directory name)
        or the relative path to a file plus its SHA1 hex hash.
        Each of these is a tuple: the former is a singleton, and the
        latter is a 2-tuple.

        The NLHTree listing is in the form of a list of lines.

        COMMENTS AND BLANK LINES ARE NOT YET SUPPORTED.
        """
        check_using_sha(using_sha)
        return NLHTree._walk_strings(ss, using_sha)

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
                    nextNode.hex_hash,)
        else:
            self._subTree = nextNode.__iter__()

            self._subTree._prefix = os.path.join(self._prefix, self._name)

            return self._subTree.__next__()

    # END ITERABLE ########################################

    # SYNONYMS ------------------------------------------------------
    def toStrings(self, lines, indent=0):
        self.to_strings(lines, indent)

    @staticmethod
    def createFromFileSystem(path_to_dir, using_sha=Q.USING_SHA2,
                             ex_re=None, match_re=None):
        return NLHTree.create_from_file_system(
            path_to_dir, using_sha, ex_re, match_re)

    @staticmethod
    def parseFirstLine(line):
        return NLHTree.parse_first_line(line)

    @staticmethod
    def parseOtherLine(line):
        return NLHTree.parse_other_line(line)

    @staticmethod
    def createFromStringArray(lines, using_sha=Q.USING_SHA2):
        return NLHTree.create_from_string_array(lines, using_sha)

    # END SYN -------------------------------------------------------
