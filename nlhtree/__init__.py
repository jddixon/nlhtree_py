# nlhtree_py/nlhtree/__init__.py

""" NLHNode, NLHTree, NLHLeaf and supporting elements. """

import binascii
import fnmatch
import itertools
import os
import re
import sys
from stat import S_ISDIR

from xlattice import HashTypes, check_hashtype
from xlattice.crypto import SP   # for get_spaces()
from xlattice.u import (file_sha1hex, file_sha2hex, file_sha3hex, UDir)

from xlattice import (
    SHA1_BIN_LEN, SHA1_HEX_LEN, SHA1_BIN_NONE, SHA1_HEX_NONE,
    SHA2_BIN_LEN, SHA2_HEX_LEN, SHA2_BIN_NONE, SHA2_HEX_NONE,
    SHA3_BIN_LEN, SHA3_HEX_LEN, SHA3_BIN_NONE, SHA3_HEX_NONE)

__all__ = ['__version__', '__version_date__',
           'NLHNode', 'NLHLeaf', 'NLHTree', ]

__version__ = '0.7.4'
__version_date__ = '2017-01-11'


class NLHError(RuntimeError):
    """ Errors relating to NLHNode and child classe. """
    pass


class NLHParseError(NLHError):
    """ Parse errors relating to NLHNode and child classe. """
    pass


class NLHNode(object):
    """ Parent class for nodes in an NLH tree. """

    def __init__(self, name, hashtype=HashTypes.SHA2):
        check_hashtype(hashtype)
        self._name = name.strip()
        self._hashtype = hashtype
        self._bin_hash = None

    @property
    def name(self):
        return self._name

    @property
    def hashtype(self):
        return self._hashtype

    @property
    def hex_hash(self):
        if self._bin_hash is None:
            if self._hashtype == HashTypes.SHA1:
                return SHA1_HEX_NONE
            elif self._hashtype == HashTypes.SHA2:
                return SHA2_HEX_NONE
            elif self._hashtype == HashTypes.SHA3:
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
    def check_hash(bin_hash, hashtype):
        """ raise if inappropriate bin_hash length"""

        if bin_hash is None:
            raise NLHError('binary hash cannot be None')
        bin_hash_len = len(bin_hash)
        len_ok = True
        if hashtype == HashTypes.SHA1:
            if bin_hash_len != SHA1_BIN_LEN:
                len_ok = False
        elif hashtype == HashTypes.SHA2:
            if bin_hash_len != SHA2_BIN_LEN:
                len_ok = False
        elif hashtype == HashTypes.SHA3:
            if bin_hash_len != SHA3_BIN_LEN:
                len_ok = False
        else:
            raise NLHError("invalid sha hash type ", hashtype)
        if not len_ok:
            raise NLHError(
                '%s: not a valid SHA binary hash length: %d' % (
                    hashtype, bin_hash_len))

    def __eq__(self, other):
        raise NotImplementedError

    def clone(self):
        raise NotImplementedError

    def __iter__(self):
        raise NotImplementedError

    def __next__(self):
        raise NotImplementedError


class NLHLeaf(NLHNode):

    def __init__(self, name, bin_hash, hashtype):
        # exception if check fails
        NLHNode.check_hash(bin_hash, hashtype)
        super().__init__(name, hashtype)

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
        return (self.name == other.name) and (
            self.bin_hash == other.bin_hash)

    def to_string(self, indent):
        return "%s%s %s" % (
            SP.get_spaces(indent),
            self._name,
            self.hex_hash)

    def clone(self):
        """ make a deep copy """

        hash_len = len(self._bin_hash)
        # pylint:disable=redefined-variable-type
        if hash_len == SHA1_BIN_LEN:
            hashtype = HashTypes.SHA1
        elif hash_len == SHA2_BIN_LEN:
            hashtype = HashTypes.SHA2
        elif hash_len == SHA3_BIN_LEN:
            hashtype = HashTypes.SHA3

        return NLHLeaf(self._name, self._bin_hash, hashtype)

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
    def create_from_file_system(path, name, hashtype=HashTypes.SHA2):
        """
        Create an NLHLeaf from the contents of the file at **path**.
        The name is part of the path but is passed to simplify the code.
        Returns None if the file cannot be found.
        """
        if os.path.exists(path):
            if hashtype == HashTypes.SHA1:
                hash_ = file_sha1hex(path)
            elif hashtype == HashTypes.SHA2:
                hash_ = file_sha2hex(path)
            elif hashtype == HashTypes.SHA3:
                hash_ = file_sha3hex(path)
            b_hash = binascii.a2b_hex(hash_)
            return NLHLeaf(name, b_hash, hashtype)
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

    FILE_LINE_RE_3 = re.compile(r'^( *)([a-z0-9_\$\+\-\.:~]+/?) ([0-9a-f]{64})$',
                                re.IGNORECASE)

    def __init__(self, name, hashtype=HashTypes.SHA2):
        super().__init__(name, hashtype)
        self._nodes = []
        self._nn = -1            # duplication seems necessary
        self._prefix = ''       # ditto
        self._sub_tree = None    # for iterators

    @property
    def nodes(self):
        return self._nodes

    @property
    def prefix(self):
        return self._prefix

    @prefix.setter
    def prefix(self, value):
        self._prefix = value

    @property
    def sub_tree(self):
        return self._sub_tree

    def __eq__(self, other):

        if other is None:
            return False
        if not isinstance(other, NLHTree):
            return False
        if self.name != other.name:
            return False
        if self.hashtype != other.hashtype:
            return False
        if len(self.nodes) != len(other.nodes):
            return False
        for i in range(len(self.nodes)):
            if not self.nodes[i] == other.nodes[i]:
                return False
        return True

    def clone(self):
        """ return a deep copy of the tree """
        tree = NLHTree(self._name, self.hashtype)
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
        for node in self._nodes:
            if fnmatch.fnmatch(node.name, pat):
                matches.append(node)
        return matches

    def insert(self, node):
        """
        Insert an NLHNode into the tree's list of nodes, maintaining
        sort order.  If a node with the same name already exists, an
        exception will be raised.
        """
        if node.hashtype != self.hashtype:
            raise NLHError("incompatible SHA types")
        # XXX need checks
        len_nodes = len(self._nodes)
        name = node.name
        done = False
        for ndx in range(len_nodes):
            i_name = self._nodes[ndx].name
            if name < i_name:
                # insert before
                if ndx == 0:
                    self._nodes = [node] + self._nodes
                    done = True
                    break
                else:
                    before = self._nodes[0:ndx]
                    after = self._nodes[ndx:]
                    self._nodes = before + [node] + after
                    done = True
                    break
            elif name == i_name:
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
        elm = []
        for thisg in self._nodes:
            if fnmatch.fnmatch(thisg.name, pat):
                if isinstance(thisg, NLHLeaf):
                    elm.append('  ' + thisg.name)
                else:
                    elm.append('* ' + thisg.name)
        return elm

    def __str__(self):
        strings = []
        self.to_strings(strings, 0)
        string = '\n'.join(strings) + '\n'
        return string

    def to_strings(self, strings, indent=0):
        strings.append("%s%s" % (SP.get_spaces(indent), self._name))
        for node in self._nodes:
            if isinstance(node, NLHLeaf):
                strings.append(node.to_string(indent + 1))
            else:
                node.to_strings(strings, indent + 1)

    @staticmethod
    def create_from_file_system(path_to_dir, hashtype=HashTypes.SHA2,
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
        (path, _, name) = path_to_dir.rpartition('/')
        if path == '':
            raise NLHError("cannot parse path " + path_to_dir)

        tree = NLHTree(name, hashtype)

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
                string = os.lstat(path_to_file)        # ignores symlinks
                mode = string.st_mode
                # os.path.isdir(path) follows symbolic links
                # pylint:disable=redefined-variable-type
                if S_ISDIR(mode):
                    node = NLHTree.create_from_file_system(
                        path_to_file, hashtype, ex_re, match_re)
                # S_ISLNK(mode) is true if symbolic link
                # isfile(path) follows symbolic links
                elif os.path.isfile(path_to_file):        # S_ISREG(mode):
                    node = NLHLeaf.create_from_file_system(
                        path_to_file, file, hashtype)
                # otherwise, just ignore it ;-)

                if node:
                    tree.nodes.append(node)

        return tree

    @staticmethod
    def parse_first_line(string):
        """
        Return the name found in the first line or raise an exception.
        """
        match = NLHTree.DIR_LINE_RE.match(string)
        if not match:
            raise NLHParseError("first line doesn't match expected pattern")
        if len(match.group(1)) != 0:
            raise NLHParseError("unexpected indent on first line")
        return match.group(2)   # the name

    @staticmethod
    def parse_other_line(string):
        """
        Return the indent (the number of spaces), the name on the line,
        and other None or the hash found.
        """

        match = NLHTree.DIR_LINE_RE.match(string)
        if match:
            return len(match.group(1)), match.group(2), None

        match = NLHTree.FILE_LINE_RE_1.match(string)
        if match:
            return len(match.group(1)), match.group(2), match.group(3)

        match = NLHTree.FILE_LINE_RE_2.match(string)
        if match:
            return len(match.group(1)), match.group(2), match.group(3)

        raise NLHParseError("can't parse line: '%s'" % string)

    @staticmethod
    def create_from_string_array(lines, hashtype=HashTypes.SHA2):
        # at entry, we don't know whether the string array uses
        # SHA1 or SHA256

        if len(lines) == 0:
            return None

        name = NLHTree.parse_first_line(lines[0])
        cur_level = NLHTree(name, hashtype)     # our first push
        root = cur_level
        stack = [root]
        depth = 0

        lines = lines[1:]
        for line in lines:
            indent, name, hash_ = NLHTree.parse_other_line(line)
            if hash_ is not None:
                b_hash = binascii.a2b_hex(hash_)

            if indent > depth + 1:
                # DEBUG
                print("IMPOSSIBLE: indent %d, depth %d" % (indent, depth))
                # END
                if hash_:
                    leaf = NLHLeaf(name, b_hash, hashtype)
                    stack[depth].insert(leaf)
                else:
                    sub_tree = NLHTree(name, hashtype)
                    stack.append(sub_tree)
                    depth += 1
            elif indent == depth + 1:
                if hash_ is None:
                    sub_tree = NLHTree(name, hashtype)
                    stack[depth].insert(sub_tree)
                    stack.append(sub_tree)
                    depth += 1
                else:
                    leaf = NLHLeaf(name, b_hash, hashtype)
                    stack[depth].insert(leaf)

            else:
                while indent < depth + 1:
                    stack.pop()
                    depth -= 1
                if hash_ is None:
                    sub_tree = NLHTree(name, hashtype)
                    stack[depth].insert(sub_tree)
                    stack.append(sub_tree)
                    depth += 1
                else:
                    leaf = NLHLeaf(name, b_hash, hashtype)
                    stack[depth].insert(leaf)

        return root

    @staticmethod
    def parse_file(path_to_file, hashtype):
        with open(path_to_file, 'r') as file:
            string = file.read()
        return NLHTree.parse(string, hashtype)

    @staticmethod
    def parse(string, hashtype):
        if not string or string == '':
            raise NLHParseError('cannot parse an empty string')
        strings = string.split('\n')
        if strings[-1] == '':
            strings = strings[:-1]
        return NLHTree.create_from_string_array(strings, hashtype)

    # DATA_DIR/U_DIR INTERACTION ------------------------------------

    def check_in_data_dir(self, data_dir):
        """
        Walk the tree, verifying that all leafs (files) can be found in
        data_dir by relative path and that the content key is correct.  This
        does NOT verify that all files have corresponding leaf nodes.

        data_dir is a path, the last component of which is the name of
        the data directory and so also the name of the NLHTree.
        """

        # if / not found, holder, the holding directory, is an empty string.
        # Return a list of leaf nodes which are not matched.  If everything
        # is OK this will be empty.

        holder, delim, _ = data_dir.rpartition('/')
        if delim == '':
            holder = ''
        unmatched = []
        for couple in self:
            if len(couple) == 1:
                # it's a directory
                pass
            else:
                rel_path = couple[0]
                # hash_ = couple[1]     # UNUSED
                path = os.path.join(holder, rel_path)
                if not os.path.exists(path):
                    unmatched.append(path)
        return unmatched

    def check_in_u_dir(self, u_path):
        """
        Walk the tree, verifying that all leaf nodes have corresponding
        files in u_dir, files with the same content key.
        """

        u_dir = UDir.discover(u_path, hashtype=self.hashtype)

        unmatched = []
        for couple in self:
            if len(couple) == 1:
                # it's a directory
                pass
            else:
                rel_path = couple[0]
                hash_ = couple[1]
                if not u_dir.exists(hash_):
                    unmatched.append((rel_path, hash_,))
        return unmatched

    def drop_from_u_dir(self, u_path):
        """ Remove all leaf nodes in this NLHTree from u_dir """

        u_dir = UDir.discover(u_path, hashtype=self.hashtype)

        unmatched = []
        for couple in self:
            if len(couple) == 1:
                # it's a directory
                pass
            else:
                hash_ = couple[1]
                ok_ = u_dir.delete(hash_)
                if not ok_:
                    rel_path = couple[0]
                    unmatched.append((rel_path, hash_,))
        return unmatched

    def populate_data_dir(self, u_path, path):
        """
        path is the path to the data directory, excluding the name
        of the directory itself, which will be the name of the tree
        """
        if not os.path.exists(u_path):
            raise NLHError(
                "populate_data_dir: u_path '%s' does not exist" % u_path)

        u_dir = UDir.discover(u_path, hashtype=self.hashtype)

        unmatched = []
        for couple in self:
            if len(couple) == 1:
                # it's a directory
                dir_name = os.path.join(path, couple[0])
                os.makedirs(dir_name, mode=0o755, exist_ok=True)
            elif len(couple) == 2:
                hash_ = couple[1]
                if not u_dir.exists(hash_):
                    unmatched.append(hash_)
                else:
                    data = u_dir.get_data(hash_)

                    path_to_file = os.path.join(path, couple[0])
                    with open(path_to_file, 'wb') as file:
                        file.write(data)
            else:
                print("degenerate/malformed tuple of length %d" % len(couple))

        return unmatched

    def save_to_u_dir(self, data_dir,
                      u_path=os.environ['DVCZ_UDIR'], hashtype=HashTypes.SHA2):
        """
        Given an NLHTree for the data directory, walk the tree, copying
        all files present in data_dir into u_path by content key.  We assume
        that u_path is well-formed.
        """

        # the last part of data_dir is the name of the tree
        (path, _, name) = data_dir.rpartition('/')
        if name != self.name:
            raise "name of directory (%s) does not match name of tree (%s)"

        # DEBUG
        #print("save_to_u_dir %s ==> %s" % (data_dir, u_path))
        #print("  path => '%s'" % path)
        # END

        u_dir = UDir.discover(u_path, hashtype=self.hashtype)

        unmatched = []
        for couple in self:
            if len(couple) == 1:
                continue                   # it's a directory

            elif len(couple) == 2:
                rel_path = couple[0]
                hash_ = couple[1]
                path_to_file = os.path.join(path, rel_path)
                if not os.path.exists(path_to_file):
                    unmatched.append(path)
                else:
                    u_dir.copy_and_put(path_to_file, hash_)
            else:
                string = []
                for part in couple:
                    string.append(part.__str__())
                unmatched.append(':'.join(string))
                print(
                    "INTERNAL ERROR: node is neither Tree nor Leaf\n  %s" %
                    string)

        return unmatched

    # ITERATORS #####################################################

    @staticmethod
    def walk_file(path_to_file, hashtype):
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
        cur_depth = 0
        path = ''
        parts = []
        hash_len = -1

        with open(path_to_file, 'r') as file:
            line = file.readline()
            line_nbr = 0
            while line:
                done = False

                # -- dir --------------------------------------------
                match = NLHTree.DIR_LINE_RE.match(line)
                if match:
                    depth = len(match.group(1))
                    dir_name = match.group(2)
                    if depth == cur_depth:
                        parts.append(dir_name)
                        cur_depth += 1
                    elif depth < cur_depth:
                        parts[depth] = dir_name
                        parts = parts[:depth + 1]
                    else:
                        raise NLHError("corrupt nlhTree listing")
                    path = '/'.join(parts)

                    yield (path, )
                    done = True

                # -- file -------------------------------------------
                if not done:
                    if hashtype == HashTypes.SHA1:
                        match = NLHTree.FILE_LINE_RE_1.match(line)
                    elif hashtype == HashTypes.SHA2:
                        match = NLHTree.FILE_LINE_RE_2.match(line)
                    elif hashtype == HashTypes.SHA3:
                        match = NLHTree.FILE_LINE_RE_3.match(line)
                    if match:
                        cur_depth = len(match.group(1))
                        file_name = match.group(2)
                        hash_ = match.group(3)
                        yield (os.path.join(path, file_name), hash_)
                        done = True
                    # DEBUG
                    else:
                        print("NO FILE LINE MATCH ON %s" % line)
                    # END

                line = file.readline()
                line_nbr += 1

    @staticmethod
    def _walk_strings(strings, hashtype=HashTypes.SHA2):
        cur_depth = 0
        path = ''
        parts = []
        hash_len = -1

        for line_nbr, line in enumerate(strings):
            done = False

            # -- dir --------------------------------------------
            match = NLHTree.DIR_LINE_RE.match(line)
            if match:
                depth = len(match.group(1))
                dir_name = match.group(2)
                if depth == cur_depth:
                    parts.append(dir_name)
                    cur_depth += 1
                elif depth < cur_depth:
                    parts[depth] = dir_name
                    parts = parts[:depth + 1]
                else:
                    raise NLHError("corrupt nlhTree listing")
                path = '/'.join(parts)

                yield (path, )
                done = True

            # -- file -------------------------------------------
            if not done:
                if hashtype == HashTypes.SHA1:
                    match = NLHTree.FILE_LINE_RE_1.match(line)
                elif hashtype == HashTypes.SHA2:
                    match = NLHTree.FILE_LINE_RE_2.match(line)
                elif hashtype == HashTypes.SHA3:
                    match = NLHTree.FILE_LINE_RE_3.match(line)
                else:
                    raise NotImplementedError()
                if match:
                    cur_depth = len(match.group(1))
                    file_name = match.group(2)
                    hash_ = match.group(3)
                    yield (os.path.join(path, file_name), hash_)
                done = True

            # -- error ------------------------------------------
            if not done:
                yield ("DUNNO WHAT THIS IS: %s" % line, )
                done = True

    @staticmethod
    def walk_string(string, hashtype=HashTypes.SHA2):
        """
        string is an NLHTree listing in the form of a single string with
        lines ending with newlines.  There is a newline at the end of
        the listing.
        """
        check_hashtype(hashtype)
        lines = string.split('\n')
        if lines[-1] == '':
            lines = lines[:-1]          # drop the last line if empty
        return NLHTree._walk_strings(lines, hashtype)

    @staticmethod
    def walk_strings(strings, hashtype=HashTypes.SHA2):
        """
        For each line in the NLHTree listing, return either the
        relative path to a directory (including the directory name)
        or the relative path to a file plus its SHA1 hex hash.
        Each of these is a tuple: the former is a singleton, and the
        latter is a 2-tuple.

        The NLHTree listing is in the form of a list of lines.

        COMMENTS AND BLANK LINES ARE NOT YET SUPPORTED.
        """
        check_hashtype(hashtype)
        return NLHTree._walk_strings(strings, hashtype)

    # ITERABLE ############################################

    def __iter__(self):
        """ Return an iterator over the NLHTree. """

        self._nn = -1
        self._sub_tree = None
        self._prefix = ''
        return self

    def __next__(self):
        """ Iterator method. """

        # For the first call:
        if self._nn < 0:
            self._nn += 1
            return (os.path.join(self._prefix, self._name), )

        if self._nn >= len(self._nodes):
            raise StopIteration

        if self._sub_tree:
            try:
                couple = self._sub_tree.__next__()
                return couple
            except StopIteration:
                self._sub_tree = None
                self._nn += 1
                if self._nn >= len(self._nodes):
                    raise StopIteration

        next_node = self._nodes[self._nn]
        if isinstance(next_node, NLHLeaf):
            self._nn += 1
            return (os.path.join(self._prefix,
                                 os.path.join(self._name, next_node.name)),
                    next_node.hex_hash,)
        else:
            self._sub_tree = next_node.__iter__()

            self._sub_tree.prefix = os.path.join(self.prefix, self.name)

            return self._sub_tree.__next__()

    # END ITERABLE ########################################
