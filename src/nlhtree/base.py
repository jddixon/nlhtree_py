# nlhtree_py/nlhtree/base.py

""" Test behavior of NLHBase. """

from nlhtree import NLHTree

__all__ = [
    'NLHBase',
]


class NLHBase(object):
    """ Test behavior of NLHBase. """

    def __init__(self, name, hashtype):
        self._root = NLHTree(name, hashtype)   # immutable ref to a NLHTree
        self._cur_tree = self._root              # the current tree; mutable
        self._hashtype = hashtype

    @property
    def name(self):
        """ Return the name of the tree. """

        return self._root.name

    @property
    def hashtype(self):
        """ Return which hash type we are using. """

        return self._root.hashtype

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

        if not path:
            raise RuntimeError('path may not be None or empty')

        # needs to handle more complex cases
        path = path.strip()
        parts = path.split('/')             # many possible problems ignored
        if parts:
            raise NotImplementedError("can't handle multi-part paths yet")

            # XXX if the path begins with a forward slash ('/'), then
            # tentatively set the current tree to the root and then
            # apply the normal relpath logic from there

        # find a node with this name
        # XXX STUB XXX

        # if it's a leaf, error
        # XXX STUB XXX

        # otherwise set cur_tree to point to this node
        self._cur_tree = path
