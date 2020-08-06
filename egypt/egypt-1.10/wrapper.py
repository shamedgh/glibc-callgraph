"""
The wrapper that puts together the call graph with the syscall info

python wrapper.py <egyptoutputfile> <file_containing_list_of_expand_files>

"""

import sys
import parse_callgraph as cg
import parse_rtl_for_syscall as rtl
import parse_make_log as make
import parse_weak_alias as wa
import parse_version_compat_symbols as vc


if len(sys.argv) != 8:
    print "Usage: "
    print "python wrapper.py egyptoutputfile expandfiles makefile caliases version_symfile compat_symfile strong_aliases"
    sys.exit(1)

egyptOutputFile = sys.argv[1]
expandFiles = sys.argv[2]
makeFile = sys.argv[3]
caliases = sys.argv[4]
verfile = sys.argv[5]
compatfile = sys.argv[6]
strongaliases = sys.argv[7]

cg.parseEgyptOutput(egyptOutputFile)
cg.printForwardCallGraph()
f = open(expandFiles)
for line in f:
    line = line.strip()
    rtl.parseRTL(line)
make.parseMakeLog(makeFile)
wa.parseWeakAlias(caliases)
wa.parseWeakAlias(strongaliases)
vc.parseVerCompatSyms(compatfile, verfile)
