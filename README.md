# glibc-callgraph

The scripts in this repository can be used to create a call graph for glibc.

The scripts for generating the callgraph and a readme on how to use them can be found in the egypt folder.

## Utilities

There is a script available in this root folder which can be used to compare two glibc callgraphs.
These callgraphs could be for two different glibc versions or two different gcc versions.
It can be used to validate whether or not both callgraphs can reach the same set of system calls starting from all their exported symbols. Mostly to be used for debugging purposes.
To use this script you can use the following command:

```
python3.7 validateCallgraph.py --callgraph-new <GLIBC_DIR1>/glibc.2.31.callgraph --binpath-new <GLIBC_DIR1>/libc-2.31.so.6 --separator-new : --callgraph-orig <GLIBC_DIR2>/glibc.23.callgraph --binpath-orig <GLIBC_DIR2>/libc.so.6 --separator-orig :
```

Parameters:

--callgraph-new: path to the new glibc callgraph
--binpath-new: path to the new glibc shared object file
--separator-new: the separator used to separate the caller and callee in the new callgraph
--callgraph-old: path to the old glibc callgraph
--binpath-old: path to the old glibc shared object file
--separator-old: the separator used to separate the caller and callee in the old callgraph
