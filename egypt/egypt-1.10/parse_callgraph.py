"""
This script parses the output of the egypt script.
Generate the output, by doing something like --
find . -name "*.expand" | xargs ./egypt > <filename>

Then run this script as
python parse_callgraph.py <filename>
"""

import sys
callerCalleeMap = {}
calleeCallerMap = {}

def sanitize(instr):
    outstr = ""
    for s in instr:
        if s == ';':
            continue
        if s == '"':
            continue
        outstr += s
    return outstr

def printForwardCallGraph():
    for caller in callerCalleeMap:
        if len(callerCalleeMap[caller]) == 0:
            print (caller + " : " )
        for callee in callerCalleeMap[caller]:
            print( caller + " : " + callee)
            
def parseEgyptOutput(outputFileName):
    f = open(outputFileName)
    for line in f:
        line = line.strip()
        if "{" in line:
            continue
        if "}" in line:
            continue
        if "->" not in line:
            splitted = line.split()
            caller = sanitize(splitted[0])
            if caller not in callerCalleeMap:
                callerCalleeMap[caller] = []
            continue; # doesn't describe an edge
        splitted = line.split()
        caller = sanitize(splitted[0])
        callee = sanitize(splitted[2])
        if caller not in callerCalleeMap:
            callerCalleeMap[caller] = []
        callerCalleeMap[caller].append(callee)
        if callee not in calleeCallerMap:
            calleeCallerMap[callee] = []
        calleeCallerMap[callee].append(caller)
    f.close()

if __name__ == "__main__":
    parseEgyptOutput("/tmp/egypt.final.callgraph")
    print("////OUTPUT/////")
    printForwardCallGraph()
