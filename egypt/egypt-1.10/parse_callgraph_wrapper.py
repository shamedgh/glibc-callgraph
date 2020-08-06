"""
The wrapper that cleans the egypt call graph output

python wrapper.py <egyptoutputfile>

"""

import sys
import parse_callgraph as cg

if len(sys.argv) != 2:
    print "Usage: "
    print "python wrapper.py egyptoutputfile"
    sys.exit(1)

egyptOutputFile = sys.argv[1]

cg.parseEgyptOutput(egyptOutputFile)
cg.printForwardCallGraph()
