# nlhtree_py

An NLH Tree is a data structure in which each node consists of a pair:
a name and either a list of such pairs or a hash.  All of the hashes
in the tree have the same number of bits, either 160 (for an SHA1 hash)
or 256 (for an SHA2 hash).

All names in the tree must be valid file names.  For the moment, this
will be understood to include letters, both upper and lower case, 
digits, the dash ('-'), and the underscore ('_').  It excludes spaces
and line breaks (CR=13 and LF=10).  

The topmost node in the tree is a pair of the first type and belongs to the
NLHTree class.  It consists of a name and a list of NLHNodes, where an
NLHNode is either an NLHTree or an NLFLeaf.  The list of nodes is sorted
by name.

All intermediate nodes in the tree are also instances of the NLHTree 
class and so consist of a name and a sorted list.

Leaf nodes in the tree, instances of the NLHLeaf class, consist of a valid 
name and a hash.  Once formed an NLHLeaf is immutable in the sense that 
its fields cannot be changed.  If it is in an NLHTree has references to 
it.  It it is removed from the tree and there are no other references to 
it, it will eventually be destroyed by the Python garbage collector.

NLHTrees are useful in building and editing MerkleTrees.  A MerkleTree
is a recursive data structure like an NLHTree.  Each node in the tree is 
named and has a hash.  If the node is a MerkleLeaf, the hash typically
represents the SHA1 or SHA2 hash of the contents of a file associated
with the name.  If the
node is a MerkleTree, the hash is the hash of the hashes of its 
contituent nodes.  The Secure Hash Algorithm (SHA) hashes are 
cryptographically secure and so guaraantee the integrity of the data 
structure: no element can be changed without invalidating all hashes above it.
While this property is quite valuable, it also makes editing a MerkleTree 
very expensive.  Generally speaking, it will be cheaper to convert the 
MerkleTree to an NLHTree, edit that, and then conveft the NLHTree back to
a MerkleTree.
