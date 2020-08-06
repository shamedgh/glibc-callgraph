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

FnNameBodyMap = {}
FnSysCallMap = {}

def sanitizeFnName(instr):
    outstr = ""
    for s in instr:
        if s == "<":
            continue
        if s == ">":
            continue
        if s == ":":
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

def extractNum(ins):
    num = -1
    split = ins.split()
    for i in range(len(split)):
        if split[i] == "mov":
            # Next token should be src,dest
            srcdst = split[i+1].split(",")
            src = srcdst[0]
            dst = srcdst[1]
            if dst == "%rax" or dst == "%eax" or dst == "%rcx" or dst == "%ecx":
                num = decimalify(src)
         
    return num


def parseObjdump(outputFileName):
    f = open(outputFileName)
    fnName = ""
    for line in f:
        if "<" in line and ">:" in line:
            # Most likely new function start
            namesplit = line.split()
            fnName = sanitizeFnName(namesplit[1])
            FnNameBodyMap[fnName] = []
            FnSysCallMap[fnName] = []
            continue
        if fnName != "":
            FnNameBodyMap[fnName].append(line)
    f.close()

    # For each function
    for fnName in FnNameBodyMap:
        body = FnNameBodyMap[fnName]
        for i in range(len(body)):
            line = body[i]
            if "syscall" in line and "0f 05" in line :
                # Check the past three lines for the value of the rax register
                num = extractNum(body[i-1])
                if num == -1:
                    num = extractNum(body[i-2])
                elif num == -1:
                    num = extractNum(body[i-3])
                if num == -1:
                    sys.stderr.write("Can't reason about syscall in function:" + fnName + " in line: " + line +" \n")
                else:
                    FnSysCallMap[fnName].append(num)

    for fnName in FnSysCallMap:
        for syscall in FnSysCallMap[fnName]:
            print fnName, " : syscall ", syscall

parseObjdump(sys.argv[1])
