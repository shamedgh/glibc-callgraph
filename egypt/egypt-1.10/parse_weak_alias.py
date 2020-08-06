"""
Takes as input a text file containing the objdump output of libc.so
Parses each line looking for the start of a new function.
Then goes through the function body, looking for a syscall.
If it finds a syscall, looks at the preceding instruction to figure out the 
syscall number.
It stores the function name and the syscall number/s to a FnSyscallsMap.

Usage:
    objdump -d <pathoflibc>/libc.so > <filename>
    python parse_libc.py <filename>
"""

import sys

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

def parseWeakAlias(outputFileName):
    f = open(outputFileName)
    obj = []
    for line in f:
        splitted = line.split(',')
        if len(splitted) < 2:
            continue
        orig = sanitize(splitted[0])
        alias = sanitize(splitted[1])
        print alias, " : " , orig
    f.close()

