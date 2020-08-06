"""
This script takes as input a single rtl file and generates the map of
Function name vs [syscalls invoked]

python parse_rtl_for_syscall.py <rtl_file>

"""

import sys
              
def parseRTL(outputFileName):
    FnSysCallMap = {}
    FnRTLStringsMap = {}
    f = open(outputFileName)
    FnName = ""
    for line in f:
        if ";; Function" in line:
            # New function
            splitted = line.split()
            FnName = splitted[2]
            FnSysCallMap[FnName] = set()
            FnRTLStringsMap[FnName] = []
        else:
            if FnName != "":
                FnRTLStringsMap[FnName].append(line)
        
    f.close()

    for fn in FnRTLStringsMap:
        rtlstrings = FnRTLStringsMap[fn]
        for i in range(len(rtlstrings)):
            line = rtlstrings[i]
            if "asm" in line and "syscall" in line:
                virreg = "" # The virtual reg that stores the operand to syscall
                syscallnum = "" # The syscall num
                si = False
                di = False
                # Look forward for the reg:SI (Single Integer)
                for j in range(3):
                    nextline = rtlstrings[i+j]
                    if "reg:SI" in nextline:
                        # extract the virtual reg num
                        virreg = nextline.split()[1]
                        si = True
                        break
                    elif "reg:DI" in nextline:
                        virreg = nextline.split()[1]
                        di = True
                        break

                if virreg == "":
                    sys.stderr.write("Couldn't find vir reg to syscall for  : " + fn + ": " +outputFileName +"\n");
                    continue

                # If argument found, look backwards for the "(set (reg:SI <arg>" pattern
                for j in range(10):
                    prevline = rtlstrings[i-j]
                    if si:
                        if "(set (reg:SI "+virreg in prevline:
                            # Look at the next line
                            nextline = rtlstrings[i-j+1]
                            if "const_int" in nextline:
                                syscallnum = nextline.split()[1]
                            break
                    if di:
                        if "(set (reg:DI "+virreg in prevline:
                            # Look at the next line
                            nextline = rtlstrings[i-j+1]
                            if "const_int" in nextline:
                                syscallnum = nextline.split()[1]
                            break

                if syscallnum == "":
                    sys.stderr.write("Couldn't find constant int value stored to vir reg for" + fn + ": " +outputFileName +"\n")
                    continue

                # Store it
                FnSysCallMap[fn].add(syscallnum)
    for fn in FnSysCallMap:
        for syscall in FnSysCallMap[fn]:
            print fn, " : syscall(", syscall, ")"



if __name__ ==  "__main__":
    parseRTL("/mnt/Projects/container-debloating/container-debloating/glibc/build/nptl/pthread_rwlock_tryrdlock.c.192r.expand")
