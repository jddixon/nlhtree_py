# nlhtree_py/nlhtree/base.py

""" Test behavior of NLHBase. """

# from stat import *
# from xlattice.crypto import SP   # for get_spaces()
from nlhtree import NLHTree
# from xlattice import (
#     SHA1_BIN_LEN, SHA2_BIN_LEN,
#     SHA1_HEX_LEN, SHA2_HEX_LEN,
#     SHA1_BIN_NONE, SHA2_BIN_NONE)

__all__ = [
    'NLHBase',
]


class NLHBase(object):
    """ Test behavior of NLHBase. """

    def __init__(self, name, using_sha):
        self._root = NLHTree(name, using_sha)   # immutable ref to a NLHTree
        self._cur_tree = self._root              # the current tree; mutable
        self._using_sha = using_sha

    @property
    def name(self):
        """ Return the name of the tree. """

        return self._root.name

    @property
    def using_sha(self):
        """ Return which hash type we are using. """

        return self._root.using_sha

    @property
    def root(self):
        """ Return the root of the current tree. """

        return self._root

    @property
    def cur_tree(self):
        """ Return the current tree. """

        return self._cur_tree

    @cur_tree.setter
    def cur_tree(self, path):
        """
        Make the given path the root of the tree.

        XXX STUBBED
        """

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
