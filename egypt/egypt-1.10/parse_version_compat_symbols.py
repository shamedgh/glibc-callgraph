"""
Glibc defines version_symbols and compat_symbols which are basically aliases.
First generate that the files -
find /mnt/Projects/container-debloating/container-debloating/glibc/glibc-2.23 -name "*.c" -o -name "*.h" | xargs awk '/versioned_symbol/,/)/'  > versioned_symbols
find /mnt/Projects/container-debloating/container-debloating/glibc/glibc-2.23 -name "*.c" -o -name "*.h" | xargs awk '/compat_symbol/,/)/'  > compat_symbols
A row looks like --
__dyn_atexit, atexit
where atexit is a synonym for __dyn_atext

Usage:
    python parse_version_compat_symbols.py <filename>
"""

import sys
import re

def sanitize(instr):
    outstr = ""
    for s in instr:
        if s == "<":
            continue
        if s == ">":
            continue
        if s == ":":
            continue
        if s == "'":
            continue
        if s == ";":
            continue
        if s == "(":
            continue
        if s == ")":
            continue
        if s == ",":
            continue
        if s == "\\":
            continue
        if s == '\n':
            continue
        outstr += s
    return outstr

def decimalify(token):
    number = ""
    intnum = -1
    if token[0] == "$":
        number = token[1:]
    try:
        intnum = int(number, 16)
    except ValueError:
        pass
    return intnum

"""
for line in f:
    splitted = line.split(',')
    if len(splitted) < 2:
        continue
    orig = sanitize(splitted[0])
    alias = sanitize(splitted[1])
    print alias, " : " , orig
"""
def parseVerCompatSyms(compatFile, versionedFile):
    f = open(compatFile)
    lines = []
    for line in f:
        lines.append(line)
    linestr = ''.join(lines)

    for line in re.split('compat_symbol', linestr):
        # Replace multiple whitespace with single 
        line = ' '.join(line.split()) 
        splitted = line.split(',')
        if len(splitted) < 3:
            continue
        orig = sanitize(splitted[1])
        alias = sanitize(splitted[2])
        print alias, " : ", orig
    f.close()

    f = open(versionedFile)
    lines = []
    for line in f:
        lines.append(line)
    linestr = ''.join(lines)
    for line in re.split('versioned_symbol', linestr):
        # Replace multiple whitespace with single 
        line = ' '.join(line.split())
        splitted = line.split(',')
        if len(splitted) < 3:
            continue
        orig = sanitize(splitted[1])
        alias = sanitize(splitted[2])
        print alias, " : ", orig
    f.close()

if __name__ == "__main__":
    parseVerCompatSyms('compat_symbols', 'versioned_symbols')
