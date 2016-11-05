# nlhtree_py

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

## On-line Documentation

More information on the **nlhtree_py** project can be found
[here](https://jddixon.github.io/nlhtree_py)
