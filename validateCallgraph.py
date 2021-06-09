import os, sys, subprocess, signal
import logging
import optparse

sys.path.insert(0, './python-utils/')

import util
import graph
import binaryAnalysis

def isValidOpts(opts):
    if not opts.callgraphorig or not opts.callgraphnew or not opts.binpathorig or not opts.binpathnew:
        print("All options --callgraph-orig, --callgraph-new, --binpath-orig and --binpath-new should be provide")
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

    parser.add_option("", "--callgraph-orig", dest="callgraphorig", default=None, nargs=1,
                      help="Original callgraph to analyze")

    parser.add_option("", "--separator-orig", dest="separatororig", default="->", nargs=1,
                      help="Separator for original callgraph")

    parser.add_option("", "--binpath-orig", dest="binpathorig", default=None, nargs=1,
                      help="Path to original binary to analyze")

    parser.add_option("", "--callgraph-new", dest="callgraphnew", default=None, nargs=1,
                      help="New callgraph to analyze")

    parser.add_option("", "--separator-new", dest="separatornew", default="->", nargs=1,
                      help="Separator for new callgraph")

    parser.add_option("", "--binpath-new", dest="binpathnew", default=None, nargs=1,
                      help="Path to new binary to analyze")

    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False,
                      help="Debug enabled/disabled")

    (options, args) = parser.parse_args()
    if isValidOpts(options):
        rootLogger = setLogPath("extractunidentifiedsyscalls.log")

        '''
        1. Extract list of exported functions from new callgraph
        2. Extract list of syscalls reachable from those functions
        3. Extract list of exported functions from orig callgraph
        4. Extract list of syscalls reachable from those functions
        5. Compare the two lists
        '''

        syscallList = list()

        i = 0
        while i < 400:
            syscallList.append("syscall(" + str(i) + ")")
            syscallList.append("syscall(" + str(i) + ")")
            syscallList.append("syscall ( " + str(i) + " )")
            syscallList.append("syscall( " + str(i) + " )")
            i += 1


        exportedFuncs = util.extractExportedFunctionsWithNm(options.binpathorig, rootLogger)
        myGraph = graph.Graph(rootLogger)
        myGraph.createGraphFromInput(options.callgraphorig, options.separatororig)

        reachableSyscallsOrig = set()
        for exportedFunc in exportedFuncs:
            rootLogger.debug("iterating over exported function: %s", exportedFunc)
            leaves = myGraph.getLeavesFromStartNode(exportedFunc, syscallList, list())
            for leaf in leaves:
                if ( leaf.startswith("syscall") ):
                    leaf = leaf.replace("syscall", "")
                    leaf = leaf.replace("(", "")
                    leaf = leaf.replace(")", "")
                    syscallNum = int(leaf.strip())
                    reachableSyscallsOrig.add(syscallNum)


        exportedFuncs = util.extractExportedFunctionsWithNm(options.binpathnew, rootLogger)
        myGraph = graph.Graph(rootLogger)
        myGraph.createGraphFromInput(options.callgraphnew, options.separatornew)

        reachableSyscallsNew = set()
        for exportedFunc in exportedFuncs:
            rootLogger.debug("iterating over exported function: %s", exportedFunc)
            leaves = myGraph.getLeavesFromStartNode(exportedFunc, syscallList, list())
            for leaf in leaves:
                if ( leaf.startswith("syscall") ):
                    leaf = leaf.replace("syscall", "")
                    leaf = leaf.replace("(", "")
                    leaf = leaf.replace(")", "")
                    syscallNum = int(leaf.strip())
                    reachableSyscallsNew.add(syscallNum)

        rootLogger.info("len(syscalls-orig): %d, len(syscalls-new): %d", len(reachableSyscallsOrig), len(reachableSyscallsNew))
        rootLogger.info("syscalls-orig: %s\n", str(reachableSyscallsOrig))
        rootLogger.info("syscalls-new: %s\n", str(reachableSyscallsNew))

        rootLogger.info("syscalls-new - syscalls-orig: %s", str(set(reachableSyscallsNew-reachableSyscallsOrig)))
        rootLogger.info("syscalls-orig - syscalls-new: %s", str(set(reachableSyscallsOrig-reachableSyscallsNew)))
