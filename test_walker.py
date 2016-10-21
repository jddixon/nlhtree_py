#!/usr/bin/env python3
# test_walker.py

"""
Walk the example data structures (directory tree, content-keyed store,
and serialized NLHTree) verifying consistency.
"""

# import sys
import unittest

# import hashlib
from xlattice import Q, check_using_sha
from nlhtree import NLHTree, NLHLeaf

# if sys.version_info < (3, 6):
#     # pylint: disable=unused-import
#     import sha3     # monkey-patches hashlib

EXAMPLE1 = """dataDir
 data1 34463aa26c4d7214a96e6e42c3a9e8f55727c695
 data2 14193743b265973e5824ca5257eef488094e19e9
 subDir1
  data11 58089ce970b65940dd5bf07703cd81b4306cb8f0
  data12 da39a3ee5e6b4b0d3255bfef95601890afd80709
 subDir2
 subDir3
  data31 487607ec22ee1255cc31c35506c64b1819a48090
 subDir4
  subDir41
   subDir411
    data31 0b57d3ab229a69ce5f7fad62f9fe654fe96c51bb
"""

EXAMPLE2 = """dataDir
 data1 023d6598659f6a6b044ee909f3f3e6c4343850a1c5c71ef3f873c8e46b68e898
 data2 29223e6e7c63529feaa441773097b68951fe8652830098b3c5c2df72fd5b7821
 subDir1
  data11 9394e20adb8adf9727ee6d12377aa57230eb548eb2c718d117c2e9c3aecf0e33
  data12 e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
 subDir2
 subDir3
  data31 9adc17b1d861fae64ddbc792fafb097c55d316a585359b6356af8fa8992aefac
 subDir4
  subDir41
   subDir411
    data31 4308da851a73798454e22ee6d71a4d0732b9fd1ab10e607da53bf8c88ad7d44b
"""

EXAMPLE3 = """dataDir
 data1 adf6c7f792e8198631aacbbc8cee51181176f4c157d578ee226040d70f552db1
 data2 c6e5bfc9f7189ef6276d0bf25f05c12c0e1dcdf10e1ac69f62a0642e9d7dfcc5
 subDir1
  data11 03ef2f36e12e9afaaabb71fe84c6db3a225714bfa0bd58440727932e23174886
  data12 a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a
 subDir2
 subDir3
  data31 9400dfa37b52665f2056c93071a851a5e4c3c2c9245d39c640d9de796fa3d530
 subDir4
  subDir41
   subDir411
    data31 360ba73957c140fc28b8d6a8b7033cd2f896158fc8988fc68bb4877e4e13a048
"""


class TestWalker(unittest.TestCase):
    """
    Walk the example data structures (directory tree, content-keyed store,
    and serialized NLHTree) verifying consistency.
    """

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_spot_check_tree(self):
        """
        Run spot checks on the example files for the supported range
        of hash types.
        """
        for using in [Q.USING_SHA1, Q.USING_SHA2, Q.USING_SHA3, ]:
            self.do_test_spot_check_tree(using)

    def do_test_spot_check_tree(self, using_sha):
        """
        Run spot checks on the example files for the specified hash type.
        """
        check_using_sha(using_sha)

        # DEBUG
        #print("\nSPOT CHECKS")
        # END
        if using_sha == Q.USING_SHA1:
            rel_path_to_data = 'example1/dataDir'
        else:
            rel_path_to_data = 'example2/dataDir'
        tree = NLHTree.create_from_file_system(rel_path_to_data, using_sha)
        self.assertIsNotNone(tree)
        self.assertEqual(len(tree.nodes), 6)
        self.assertEqual(tree.name, 'dataDir')

        node0 = tree.nodes[0]
        self.assertTrue(isinstance(node0, NLHLeaf))
        self.assertEqual(node0.name, 'data1')

        node1 = tree.nodes[1]
        self.assertTrue(isinstance(node1, NLHLeaf))
        self.assertEqual(node1.name, 'data2')

        node2 = tree.nodes[2]
        self.assertFalse(isinstance(node2, NLHLeaf))
        self.assertEqual(node2.name, 'subDir1')
        self.assertEqual(len(node2.nodes), 2)

        node5 = tree.nodes[5]
        self.assertFalse(isinstance(node5, NLHLeaf))
        self.assertEqual(node5.name, 'subDir4')
        self.assertEqual(len(node5.nodes), 1)

        node50 = node5.nodes[0]
        self.assertFalse(isinstance(node50, NLHLeaf))
        self.assertEqual(node50.name, 'subDir41')
        self.assertEqual(len(node50.nodes), 1)

        node500 = node50.nodes[0]
        self.assertFalse(isinstance(node500, NLHLeaf))
        self.assertEqual(node500.name, 'subDir411')
        self.assertEqual(len(node500.nodes), 1)

        node5000 = node500.nodes[0]
        self.assertTrue(isinstance(node5000, NLHLeaf))
        self.assertEqual(node5000.name, 'data31')

    def test_walkers(self):
        """ Run the walker for a number of hash types. """

        for using in [Q.USING_SHA1, Q.USING_SHA2, ]:
            self.do_test_walkers(using)

    def do_test_walkers(self, using_sha):
        """
        Run the walker for a specific hash type.
        """
        # DEBUG
        # print("\ndo_test_walkers, %s" % using_sha)
        # END

        check_using_sha(using_sha)
        if using_sha == Q.USING_SHA1:
            rel_path_to_data = 'example1/dataDir'
            rel_path_to_nlh = 'example1/example.nlh'
            example = EXAMPLE1
        elif using_sha == Q.USING_SHA2:
            rel_path_to_data = 'example2/dataDir'
            rel_path_to_nlh = 'example2/example.nlh'
            example = EXAMPLE2
        elif using_sha == Q.USING_SHA3:
            rel_path_to_data = 'example3/dataDir'
            rel_path_to_nlh = 'example3/example.nlh'
            example = EXAMPLE3

        tree = NLHTree.create_from_file_system(rel_path_to_data, using_sha)
        self.assertIsNotNone(tree)
        string = tree.__str__()
        self.assertEqual(example, string)        # the serialized NLHTree

        # The serialized NLHTree, the string s, is identical to the example1/2
        # serialization above.  So we should be able to walk example1/2,
        # walk the disk file, and walk the in-memory object tree and get
        # the same result.

        from_disk = []
        from_strings = []
        from_str = []
        from_obj = []

        # -- walk on-disk representation ----------------------------

        # DEBUG
        # print("\nWALK FILE ON DISK")
        # sys.stdout.flush()
        # END

        # a couple is a 2-tuple
        for couple in NLHTree.walk_file(rel_path_to_nlh, using_sha):
            if len(couple) == 1:
                # print("    DIR:  %s" % couple[0])       # DEBUG
                from_disk.append(couple)
            elif len(couple) == 2:
                # print('    FILE: %s %s' % (couple[0], couple[1])) # DEBUG
                from_disk.append(couple)
            else:
                print('    unexpected couple of length %d' % len(couple))

        # -- walk list-of-strings representation -------------------

        lines = example.split('\n')
        if lines[-1] == '':
            lines = lines[:-1]          # drop last line if blank

        # DEBUG
        # print("\nWALK LIST OF STRINGS; %s; there are %d lines" % (
        #    using_sha, len(lines)))
        # sys.stdout.flush()
        # END

        for couple in NLHTree.walk_strings(lines, using_sha):
            if len(couple) == 1:
                # print("    DIR:  %s" % couple[0])     # DEBUG
                from_strings.append(couple)
            elif len(couple) == 2:
                # print('    FILE: %s %s' % (couple[0], couple[1])) # DEBUG
                from_strings.append(couple)
            else:
                print('    unexpected couple of length %d' % len(couple))

        # -- walk string representation -----------------------------

        # DEBUG
        #print("\nWALK STRING")
        # sys.stdout.flush()
        # END

        for couple in NLHTree.walk_string(example, using_sha):
            if len(couple) == 1:
                # print("    DIR:  %s" % couple[0])     # DEBUG
                from_str.append(couple)
            elif len(couple) == 2:
                # print('    FILE: %s %s' % (couple[0], couple[1])) # DEBUG
                from_str.append(couple)
            else:
                print('    unexpected couple of length %d' % len(couple))

        # -- walk NLHTree object ------------------------------------

        # DEBUG
        #print("\nWALK OBJECT")
        # sys.stdout.flush()
        #hasattr(tree, '__iter__')
        #hasattr(tree, '__next__')
        # END

        for couple in tree:
            if len(couple) == 1:
                # print("        DIR:  %s" % couple[0])     # DEBUG
                from_obj.append(couple)
            elif len(couple) == 2:
                # print('        FILE: %s %s' % (couple[0], couple[1])) # DEBUG
                from_obj.append(couple)
            else:
                print('        unexpected couple of length %d' % len(couple))

        # -- verify the lists are identical -------------------------

        # DEBUG
        #print("\nIDENTITY CHECKS %s" % using_sha)
        # sys.stdout.flush()
        # END

        def compare_lists(a_list, b_list):
            """ Verify that two lists of tuples are the same. """

            self.assertEqual(len(a_list), len(b_list))
            for ndx, a_val in enumerate(a_list):
                self.assertEqual(a_val, b_list[ndx])

        # DEBUG
#       #print("FROM_DISK:")
#       for i in from_disk:
#           if len(i) == 1:
#               print("  %s" % (i[0]))
#           else:
#               print("  %s %s" % (i[0], i[1]))

#       print("FROM_SS:")
#       for i in from_strings:
#           if len(i) == 1:
#               print("  %s" % (i[0]))
#           else:
#               print("  %s %s" % (i[0], i[1]))
        # END

        compare_lists(from_disk, from_strings)

        # DEBUG
        #print("\ncomparing from_disk, from_str")
        # END
        compare_lists(from_disk, from_str)

        # DEBUG
        #print("\ncomparing from_disk, from_obj")
        # END
        compare_lists(from_disk, from_obj)

        # -- verify that the operations are reversible, that you can
        # recover the dataDir from the listings ---------------------

        # XXX NOT YET IMPLEMENTED XXX

if __name__ == '__main__':
    unittest.main()
