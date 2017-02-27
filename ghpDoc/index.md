<h1 class="libTop">nlhtree_py</h1>

## Data Structure

This project is a Python3 implementation of the NLHTree, a data structure
defined
[here](https://jddixon.github.io/xlattice/nlhTree.html)
in some detail.

The NLHTree represents a directory structure as
an indented list.  Directory names appear alone on a line; files
in a given directory are listed at an indent of one space below
the directory name, with the file name followed by the
Secure Hash Algoritm hash of the file contents,
[SHA1](https://en.wikipedia.org/wiki/SHA-1) or
[SHA256](https://en.wikipedia.org/wiki/SHA-2)
as appropriate.  These are printed as 40 or 64 hexadecimal digits
respectively.

What follows is an NLHTree representing the directory `dataDir`.

    dataDir
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

This has two data files in `dataDir/`, `data1` and `data2`.  Each
of these is followed by its 20-byte/160-bit SHA1 hash in hexadecimal form.
The file names are indented one space more than the directory name.

There are also four subdirectories, `subDir1`, `subDir2`, `subDir3`,
and `subDir4`.  These are at the same indent as the two data files.
Files with the subdirectories and indented one space more.

## Use in BuildLists

The NLHTree is used in the
[BuildList](https://jddixon.github.com/xlattice/buildList.html);
it this context it is prefixed with a title, RSA public key, and
timestamp and then optionally digitally signed.  If signed it can
be used to guarantee the integrity of a file system.  That is, it
can be used to detect any modifications to an existing directory
structure.  Alternatively, it can be used to reconstruct a file
system in systems such as distributed version control systems,
with the content key used to guarantee that the files retrieved
are identical to those in the original form of the directory structure.

As an example, this is the BuildList of a similar directory structure:

-----BEGIN RSA PUBLIC KEY-----
MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQCzxJ0l1e898G/gBB9zBWUoQ7uw
8C2Z6OTMJeXrNcTR2ZW7IIMevzYHeR26w+k54Roiv4Oec1uGGom4I7TSxF1QCmfG
PDaWgvzE4mmwbPCiiYt6cl/y7paG00709ZnbNBjbaaS2Y3gWN+HwiBcENyNrX29i
P3aQwEB1RNVW8r+SIQIDAQAB
-----END RSA PUBLIC KEY-----
sample build list
2016-09-11 23:13:36
# BEGIN CONTENT #
dataDir
 data1 32056bdf38bed17ab7f2bfb37421fa5f4caade71
 data2 80b3b965bdfde312a4eeacc87c42f2a68ad1c7d8
 subDir1
  data11 ca83a024cf4bb9c503f89c86b8819e012d64212d
  data12 da39a3ee5e6b4b0d3255bfef95601890afd80709
 subDir2
 subDir3
  data31 e5ea2d73b3801b38e2add428fa98219c48c69e93
 subDir4
  subDir41
   subDir411
    data31 c4d1f005f36404cf15a00ce00d9a136a35409bc4
# END CONTENT #

SuJvEG5zYe5SAnYEHynZXvjIPdY/Fr792ltnwJyPxyg2QO+GCrSfepXnNeIUMJtG5c4zamqsijFZYuAuuhIHCxM1sLcEM5PVNmU/cJT9BLWI952bAqqcB+qaWRcDdSt/tQKZCvzeujZTCa9MsbygN2Wo+ToaIv6dkB21WufyRSs=

The RSA private key corresponding to the public part of the key at the
top of the BuildList is used to generate the digital signature at the
bottom.  Given these two bits of information, the public key and the
digital signature, anyone can verify that the BuildList has not been
tampered with.

## Utilities

### nlh_check_in_data_dir

    usage: nlh_check_in_data_dir [-h] [-b LIST_FILE] [-d DATA_DIR] [-j] [-T] [-V]
                                 [-1] [-2] [-3] [-u U_PATH] [-v]

    list any files in the NLHTree not present in the directory,

    optional arguments:
      -h, --help            show this help message and exit
      -b LIST_FILE, --list_file LIST_FILE
                            where to write listing (default = list.nlh)
      -d DATA_DIR, --data_dir DATA_DIR
                            path to data directory
      -j, --just_show       show options and exit
      -T, --testing         this is a test run
      -V, --show_version    print the version number and exit
      -1, --using_sha1      using the 160-bit SHA1 hash
      -2, --using_sha2      using the 256-bit SHA2 (SHA256) hash
      -3, --using_sha3      using the 256-bit SHA3 (Keccak-256) hash
      -u U_PATH, --u_path U_PATH
                            path to uDir
      -v, --verbose         be chatty

### nlh_check_in_u_dir

    usage: nlh_check_in_u_dir [-h] [-b LIST_FILE] [-j] [-T] [-V] [-1] [-2] [-3]
                              [-u U_PATH] [-v]

    given a project directory, write an NLHTree while backing the project up to U

    optional arguments:
      -h, --help            show this help message and exit
      -b LIST_FILE, --list_file LIST_FILE
                            where to write listing (default = list.nlh)
      -j, --just_show       show options and exit
      -T, --testing         this is a test run
      -V, --show_version    print the version number and exit
      -1, --using_sha1      using the 160-bit SHA1 hash
      -2, --using_sha2      using the 256-bit SHA2 (SHA256) hash
      -3, --using_sha3      using the 256-bit SHA3 (Keccak-256) hash
      -u U_PATH, --u_path U_PATH
                            path to uDir
      -v, --verbose         be chatty

### nlh_populate_data_dir

    usage: nlh_populate_data_dir [-h] [-b LIST_FILE] [-j] [-p PATH] [-T] [-V] [-z]
                                 [-1] [-2] [-3] [-u U_PATH] [-v]

    given an NLHTree and U, recreate the corresponding data directory

    optional arguments:
      -h, --help            show this help message and exit
      -b LIST_FILE, --list_file LIST_FILE
                            where to write listing (default = list.nlh)
      -j, --just_show       show options and exit
      -p PATH, --path PATH  path to data directory
      -T, --testing         this is a test run
      -V, --show_version    print the version number and exit
      -z, --dont_do_it      don't actually do anything, just say what you would do
      -1, --using_sha1      using the 160-bit SHA1 hash
      -2, --using_sha2      using the 256-bit SHA2 (SHA256) hash
      -3, --using_sha3      using the 256-bit SHA3 (Keccak-256) hash
      -u U_PATH, --u_path U_PATH
                            path to uDir
      -v, --verbose         be chatty

### nlh_save_to_u_dir

    usage: nlh_save_to_u_dir [-h] [-b LISTFILE] [-d DATADIR] [-j] [-T] [-V] [-z]
                             [-1] [-2] [-3] [-u U_PATH] [-v]

    given a project directory, write an NLHTree while backing the project up to U

    optional arguments:
      -h, --help            show this help message and exit
      -b LISTFILE, --listFile LISTFILE
                            where to write listing (default = list.nlh)
      -d DATADIR, --dataDir DATADIR
                            path to data directory
      -j, --justShow        show options and exit
      -T, --testing         this is a test run
      -V, --showVersion     print the version number and exit
      -z, --dontDoIt        don't actually do anything, just say what you would do
      -1, --using_sha1      using the 160-bit SHA1 hash
      -2, --using_sha2      using the 256-bit SHA2 (SHA256) hash
      -3, --using_sha3      using the 256-bit SHA3 (Keccak-256) hash
      -u U_PATH, --u_path U_PATH
                            path to uDir
      -v, --verbose         be chatty

## Project Status

A good beta.  All tests succeed.

