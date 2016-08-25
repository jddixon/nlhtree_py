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

## Project Status

A good beta.  All tests succeed.

## On-line Documentation

More information on the **nlhtree_py** project can be found
[here](https://jddixon.github.io/nlhtree_py)
