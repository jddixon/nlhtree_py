#!/usr/bin/env python3
# nlhtree_py/testDropFromU.py

""" Test the drop_from_u_dir functionality. """

import os
import sys
import time
import unittest
from binascii import hexlify

import hashlib
from rnglib import SimpleRNG
from nlhtree import NLHTree, NLHLeaf
from xlattice import HashTypes
from xlattice.u import UDir, DirStruc

if sys.version_info < (3, 6):
    # pylint: disable=unused-import
    import sha3     # monkey-patches hashlib
    assert sha3     # prevent flakes warning


class TestDropFromU(unittest.TestCase):
    """ Test the drop_from_u_dir functionality. """

    def setUp(self):
        self.rng = SimpleRNG(time.time())

    def tearDown(self):
        pass

    def populate_tree(self, tree, data_path, u_dir, hashtype):
        """
        Generate nnn and nnn unique random values, where nnn is at least 16.
        """
        nnn = 16 + self.rng.next_int16(16)
        # DEBUG
        # print("nnn = %d" % nnn)
        # EnnnD

        values = []
        hashes = []
        for count in range(nnn):
            # generate datum ------------------------------
            datum = self.rng.some_bytes(32 + self.rng.next_int16(32))
            values.append(datum)

            # generate hash = bin_key ----------------------
            if hashtype == HashTypes.SHA1:
                sha = hashlib.sha1()
            elif hashtype == HashTypes.SHA2:
                sha = hashlib.sha256()
            elif hashtype == HashTypes.SHA3:
                sha = hashlib.sha3_256()
            elif hashtype == HashTypes.BLAKE2B:
                sha = hashlib.blake2b(digest_size=32)
            else:
                raise NotImplementedError
            sha.update(datum)
            bin_key = sha.digest()
            hex_key = sha.hexdigest()
            hashes.append(bin_key)

            # write data file -----------------------------
            file_name = 'value%04d' % count
            path_to_file = os.path.join(data_path, file_name)
            with open(path_to_file, 'wb') as file:
                # DEBUG
                # print("writing %s to %s" % (hex_key, path_to_file))
                # END
                file.write(datum)

            # insert leaf into tree -----------------------
            # path_from_top = os.path.join(top_name, file_name)
            leaf = NLHLeaf(file_name, bin_key, hashtype)
            tree.insert(leaf)

            # DEBUG
            # print("  inserting <%s %s>" % (leaf.name, leaf.hex_hash))
            # END

            # write data into uDir ------------------------
            u_dir.put_data(datum, hex_key)
        return values, hashes

    def generate_udt(self, struc, hashtype):
        """
        Generate under ./tmp a data directory with random content,
        a uDir containing the same data, and an NLHTree that matches.

        uDir has the directory structure (DIR_FLAT, DIR16x16, DIR256x256,
        etc requested.  Hashes are SHA1 if using SHA1 is True, SHA256
        otherwise.

        values is a list of binary values, each the content of a file
        under dataDir.  Each value contains a non-zero number of bytes.

        hashes is a list of the SHA hashes of the values.  Each hash
        is a binary value.  If using SHA1 it consists of 20 bytes.

        return uPath, data_path, tree, hashes, values
        """

        # make a unique U directory under ./tmp/
        os.makedirs('tmp', mode=0o755, exist_ok=True)
        u_root_name = self.rng.next_file_name(8)
        u_path = os.path.join('tmp', u_root_name)
        while os.path.exists(u_path):
            u_root_name = self.rng.next_file_name(8)
            u_path = os.path.join('tmp', u_root_name)

        # DEBUG
        # print("u_root_name = %s" % u_root_name)
        # END

        # create uDir and the NLHTree
        u_dir = UDir(u_path, struc, hashtype)
        self.assertTrue(os.path.exists(u_path))

        # make a unique data directory under tmp/
        data_tmp = self.rng.next_file_name(8)
        tmp_path = os.path.join('tmp', data_tmp)
        while os.path.exists(tmp_path):
            data_tmp = self.rng.next_file_name(8)
            tmp_path = os.path.join('tmp', data_tmp)

        # dataDir must have same base name as NLHTree
        top_name = self.rng.next_file_name(8)
        data_path = os.path.join(tmp_path, top_name)
        os.makedirs(data_path, mode=0o755)

        # DEBUG
        # print("data_tmp = %s" % data_tmp)
        # print("top_name = %s" % top_name)
        # print('data_path = %s' % data_path)
        # END

        tree = NLHTree(top_name, hashtype)
        values, hashes = self.populate_tree(tree, data_path, u_dir, hashtype)
        return u_path, data_path, tree, hashes, values

    # ---------------------------------------------------------------

    def do_test_with_ephemeral_tree(self, struc, hashtype):
        """
        Generate a tmp/ subdirectory containing a quasi-random data
        directory and corresponding uDir and NLHTree serialization.

        We use the directory strucure (struc) and hash type (hashtype)
        indicated, running various consistency tests on the three.
        """

        u_path, data_path, tree, hashes, values = self.generate_udt(
            struc, hashtype)

        # DEBUG
        # print("TREE:\n%s" % tree)
        # END
        # verify that the dataDir matches the nlhTree
        tree2 = NLHTree.create_from_file_system(data_path, hashtype)
        # DEBUG
        # print("TREE2:\n%s" % tree2)
        # END
        self.assertEqual(tree2, tree)

        nnn = len(values)             # number of values present
        hex_hashes = []
        for count in range(nnn):
            hex_hashes.append(hexlify(hashes[count]).decode('ascii'))

        ndxes = [ndx for ndx in range(nnn)]  # indexes into lists
        self.rng.shuffle(ndxes)         # shuffled

        kkk = self.rng.next_int16(nnn)   # we will drop this many indexes

        # DEBUG
        # print("dropping %d from %d elements" % (kkk, nnn))
        # END

        drop_me = ndxes[0:kkk]        # indexes of values to drop
        keep_me = ndxes[kkk:]         # of those which should still be present

        # construct an NLHTree containing values to be dropped from uDir
        clone = tree.clone()
        for count in keep_me:
            name = 'value%04d' % count
            clone.delete(name)     # the parameter is a glob !

        # these values should be absent from q: they won't be dropped from uDir
        for count in keep_me:
            name = 'value%04d' % count
            xxx = clone.find(name)
            self.assertEqual(len(xxx), 0)

        # these values shd still be present in clone: they'll be dropped from
        # UDir
        for count in drop_me:
            name = 'value%04d' % count
            xxx = clone.find(name)
            self.assertEqual(len(xxx), 1)

        # the clone subtree contains those elements which will be dropped
        # from uDir
        unmatched = clone.drop_from_u_dir(u_path)               # was unmatched

        # DEBUG
        # for x in unmatched:  # (relPath, hash)
        #    print("unmatched: %s %s" % (x[0], x[1]))
        # END
        self.assertEqual(len(unmatched), 0)

        u_dir = UDir(u_path, struc, hashtype)
        self.assertTrue(os.path.exists(u_path))

        # these values should still be present in uDir
        for count in keep_me:
            hex_hash = hex_hashes[count]
            self.assertTrue(u_dir.exists(hex_hash))

        # these values should NOT be present in UDir
        for count in drop_me:
            hex_hash = hex_hashes[count]
            self.assertFalse(u_dir.exists(hex_hash))

    def test_with_ephemeral_tree(self):
        """
        Generate tmp/ subdirectories containing a quasi-random data
        directory and corresponding uDir and NLHTree serialization,
        using various directory structures and hash types.
        """
        for struc in DirStruc:
            for hashtype in HashTypes:
                self.do_test_with_ephemeral_tree(struc, hashtype)


if __name__ == '__main__':
    unittest.main()
