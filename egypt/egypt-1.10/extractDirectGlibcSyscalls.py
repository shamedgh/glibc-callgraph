import os, sys, subprocess, signal
import logging
import optparse

sys.path.insert(0, './python-utils/')

import util
import graph
import binaryAnalysis

def isValidOpts(opts):
    if not opts.callgraph or not opts.binpath:
        print("Both --callgraph and --binpath should be provide")
        return False
    return True


def setLogPath(logPath):
    """
    Set the property of the logger: path, config, and format
    :param logPath:
    :return:
    """
    if os.path.exists(logPath):
        os.remove(logPath)

    rootLogger = logging.getLogger("coverage")
    if options.debug:
        logging.basicConfig(filename=logPath, level=logging.DEBUG)
        rootLogger.setLevel(logging.DEBUG)
    else:
        logging.basicConfig(filename=logPath, level=logging.INFO)
        rootLogger.setLevel(logging.INFO)

#    ch = logging.StreamHandler(sys.stdout)
    consoleHandler = logging.StreamHandler()
    rootLogger.addHandler(consoleHandler)
    return rootLogger
#    rootLogger.addHandler(ch)

if __name__ == '__main__':
    """
    Find system calls for function
    """
    usage = "Usage: %prog -c <Callgraph> -s <Separator in callgraph file llvm=-> glibc=: > -f <Function name>"

    parser = optparse.OptionParser(usage=usage, version="1")

    parser.add_option("", "--callgraph", dest="callgraph", default=None, nargs=1,
                      help="Callgraph to analyze")

    parser.add_option("", "--separator", dest="separator", default="->", nargs=1,
                      help="Callgraph to analyze")

    parser.add_option("", "--binpath", dest="binpath", default=None, nargs=1,
                      help="Path to binary to analyze")

    parser.add_option("", "--output", dest="output", default=None, nargs=1,
                      help="Add new edges for unidentified system calls to output file")

    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False,
                      help="Debug enabled/disabled")

    (options, args) = parser.parse_args()
    if isValidOpts(options):
        rootLogger = setLogPath("extractunidentifiedsyscalls.log")

        '''
        1. Extract list of exported functions
        2. Extract list of syscalls reachable from those functions
        3. Extract list of syscalls invoked directly
        4. Generate list of unidentified system calls
        5. Add direct edges to those system calls to all exported functions
        '''

        syscallList = list()

        i = 0
        while i < 400:
            syscallList.append("syscall(" + str(i) + ")")
            syscallList.append("syscall(" + str(i) + ")")
            syscallList.append("syscall ( " + str(i) + " )")
            syscallList.append("syscall( " + str(i) + " )")
            i += 1


        exportedFuncs = util.extractExportedFunctionsWithNm(options.binpath, rootLogger)
        myGraph = graph.Graph(rootLogger)
        myGraph.createGraphFromInput(options.callgraph, options.separator)

        reachableSyscalls = set()
        for exportedFunc in exportedFuncs:
            rootLogger.debug("iterating over exported function: %s", exportedFunc)
            leaves = myGraph.getLeavesFromStartNode(exportedFunc, syscallList, list())
            for leaf in leaves:
                if ( leaf.startswith("syscall") ):
                    leaf = leaf.replace("syscall", "")
                    leaf = leaf.replace("(", "")
                    leaf = leaf.replace(")", "")
                    syscallNum = int(leaf.strip())
                    reachableSyscalls.add(syscallNum)

        rootLogger.debug("callgraphSyscalls: %s", str(reachableSyscalls))

        myBinary = binaryAnalysis.BinaryAnalysis(options.binpath, rootLogger)
        directSyscallSet, successCount, failedCount = myBinary.extractDirectSyscalls()

        missedSyscallSet = set(directSyscallSet-reachableSyscalls)

        if ( not options.output ):
            rootLogger.info("directSyscalls-callgraphSyscalls = %s", str(missedSyscallSet))
        else:
            outputFile = open(options.output, 'w')
            for exportedFunc in exportedFuncs:
                for missedSyscall in missedSyscallSet:
                    if ( missedSyscall < 1000 ):
                        missedSyscall = "syscall ( " + str(missedSyscall) + " )"
                        #rootLogger.info(exportedFunc + options.separator + missedSyscall)
                        outputFile.write(exportedFunc + options.separator + missedSyscall + "\n")
                        outputFile.flush()
            outputFile.close()
                    
