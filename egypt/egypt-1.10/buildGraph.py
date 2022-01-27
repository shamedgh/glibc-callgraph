import os, sys, subprocess, signal
import logging
import optparse
import time

sys.path.insert(0, './python-utils/')

import util

def isValidOpts(opts):
    """
    Check if the required options are sane to be accepted
        - Check if the provided files exist
        - Check if two sections (additional data) exist
        - Read all target libraries to be debloated from the provided list
    :param opts:
    :return:
    """
    if ( not options.buildpath or 
         not options.srcpath or 
         not options.buildlogpath or 
         not options.libcpath ):
        parser.error("Options --buildpath, --srcpath, --buildlogpath and --libcpath should be provided.")
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
    Build Glibc callgraph
    """
    usage = ""

    parser = optparse.OptionParser(usage=usage, version="1")

    parser.add_option("", "--srcpath", dest="srcpath", default=None, nargs=1,
                      help="Absolute path to glibc src path")

    parser.add_option("", "--buildpath", dest="buildpath", default=None, nargs=1,
                      help="Absolute path to glibc build path (built with CFLAGS=-fdump-rtl-expand flag)")

    parser.add_option("", "--buildlogpath", dest="buildlogpath", default=None, nargs=1,
                      help="Absolute path to glibc build log path")

    parser.add_option("", "--libcpath", dest="libcpath", default=None, nargs=1,
                      help="Absolute path to glibc .so file")

    parser.add_option("-d", "--debug", dest="debug", action="store_true", default=False,
                      help="Debug enabled/disabled")

    (options, args) = parser.parse_args()
    if isValidOpts(options):
        rootLogger = setLogPath("buildgraph.log")


        rtlFilePaths = "/tmp/expand.files"
        #1. find PATH_TO_BUILD/ -name "*.expand" > tmp
        findRtlFileCmd = "find {} -name \"*.expand\" > {}"
        cmd = findRtlFileCmd.format(options.buildpath, rtlFilePaths)
        returncode, out, err = util.runCommand(cmd)
        if ( returncode != 0 ):
            rootLogger.error("Error find RTL files: %s", err)
            sys.exit(-1)

        #2.1. ./egypt -include-external `cat tmp` > initial.part1.cfg
        egyptOutPath1 = "/tmp/egypt.part1.callgraph"
        egyptCmd = "./egypt -include-external `cat {}` > {}"
        cmd = egyptCmd.format(rtlFilePaths, egyptOutPath1)
        returncode, out, err = util.runCommand(cmd)
        if ( returncode != 0 ):
            rootLogger.error("Error running egypt cmd: %s", err)
            sys.exit(-1)

        #2.2. ./egypt.modified -include-external `cat tmp` > initial.part2.cfg
        egyptOutPath2 = "/tmp/egypt.part2.callgraph"
        egyptCmd = "./egypt.modified -include-external `cat {}` > {}"
        cmd = egyptCmd.format(rtlFilePaths, egyptOutPath2)
        returncode, out, err = util.runCommand(cmd)
        if ( returncode != 0 ):
            rootLogger.error("Error running egypt.modified cmd: %s", err)
            sys.exit(-1)

        #3. build egypt final callgraph
        #cat initial.part1.cfg > initial.cfg
        #cat initial.part2.cfg >> initial.cfg
        egyptOutPath = "/tmp/egypt.callgraph"
        touchOutputCmd = "touch {}; cat /dev/null > {}"
        cmd = touchOutputCmd.format(egyptOutPath, egyptOutPath)
        returncode, out, err = util.runCommand(cmd)
        if ( returncode != 0 ):
            rootLogger.error("Error running touch and emptying file: %s", err)
            sys.exit(-1)

        catCmd = "cat {} >> {}"
        cmd = catCmd.format(egyptOutPath1, egyptOutPath)
        returncode, out, err = util.runCommand(cmd)
        if ( returncode != 0 ):
            rootLogger.error("Error running cat: %s", err)
            sys.exit(-1)

        cmd = catCmd.format(egyptOutPath2, egyptOutPath)
        returncode, out, err = util.runCommand(cmd)
        if ( returncode != 0 ):
            rootLogger.error("Error running cat: %s", err)
            sys.exit(-1)

        #4. python2.7 parse_callgraph_wrapper.py initial.cfg > initial.cleaned.cfg
        #egyptFinalOutPath = "/tmp/egypt.final.callgraph"
        #cleanEgyptGraphCmd = "python2.7 parse_callgraph_wrapper.py {} > {}"
        #cmd = cleanEgyptGraphCmd.format(egyptOutPath, egyptFinalOutPath)
        #returncode, out, err = util.runCommand(cmd)
        #if ( returncode != 0 ):
        #    rootLogger.error("Error running parse_callgraph_wrapper: %s", err)
        #    sys.exit(-1)

        #5. find weak/strong/versioned/compat symbols
        #find . -name "*.c" -o -name "*.h" | xargs grep "weak_alias" | awk '{print $2 $3}' 
        weakAliasFile = "/tmp/glibc.weak.alias"
        findCmd = "find {} -name \"*.c\" -o -name \"*.h\" | xargs grep \"weak_alias\" | awk '{{print $2 $3}}' > {}"
        cmd = findCmd.format(options.srcpath, weakAliasFile)
        returncode, out, err = util.runCommand(cmd)
        if ( returncode != 0 ):
            rootLogger.error("Error finding weak aliases: %s", err)
            sys.exit(-1)

        #find . -name "*.c" -o -name "*.h" | xargs grep "strong_alias" | awk '{print $2 $3}'
        strongAliasFile = "/tmp/glibc.strong.alias"
        findCmd = "find {} -name \"*.c\" -o -name \"*.h\" | xargs grep \"strong_alias\" | awk '{{print $2 $3}}' > {}"
        cmd = findCmd.format(options.srcpath, strongAliasFile)
        returncode, out, err = util.runCommand(cmd)
        if ( returncode != 0 ):
            rootLogger.error("Error finding strong aliases: %s", err)
            sys.exit(-1)

        #find . -name "*.c" -o -name "*.h" | xargs awk '/versioned_symbol \(/,/;/'
        versionAliasFile = "/tmp/glibc.version.alias"
        findCmd = "find {} -name \"*.c\" -o -name \"*.h\" | xargs awk '/versioned_symbol \(/,/;/' > {}"
        cmd = findCmd.format(options.srcpath, versionAliasFile)
        returncode, out, err = util.runCommand(cmd)
        if ( returncode != 0 ):
            rootLogger.error("Error finding version aliases: %s", err)
            sys.exit(-1)

        #find . -name "*.c" -o -name "*.h" | xargs awk '/compat_symbol \(/,/;/'
        compatAliasFile = "/tmp/glibc.compat.alias"
        findCmd = "find {} -name \"*.c\" -o -name \"*.h\" | xargs awk '/compat_symbol \(/,/;/' > {}"
        cmd = findCmd.format(options.srcpath, compatAliasFile)
        returncode, out, err = util.runCommand(cmd)
        if ( returncode != 0 ):
            rootLogger.error("Error finding compat aliases: %s", err)
            sys.exit(-1)

        #6. final wrapper to build final callgraph (without unreachable syscalls)
        #python2.7 wrapper.py glibc.2.33/initial.all.cfg glibc.2.33/all.expand.files ~/library-debloating/libsrccodes/glibc/build/build.log glibc.2.33/weakalias glibc.2.33/versioned_symbols glibc.2.33/compat_symbols glibc.2.33/strongalias >> glibc.2.33/wrapper.out.new
        finalCallgraph = "glibc.callgraph"
        buildGraphCmd = "python2.7 wrapper.py {} {} {} {} {} {} {} > {}"
        cmd = buildGraphCmd.format(egyptOutPath, rtlFilePaths, options.buildlogpath, weakAliasFile, versionAliasFile, compatAliasFile, strongAliasFile, finalCallgraph)
        returncode, out, err = util.runCommand(cmd)
        if ( returncode != 0 ):
            rootLogger.error("Error running final wrapper: %s", err)
            sys.exit(-1)


        #7. add missing syscalls as callee for all exported functions
        #python2.7 extractDirectGlibcSyscalls.py -callgraph ~/confine/libc-callgraphs/glibc.callgraph --binpath /lib/x86_64-linux-gnu/libc.so.6 --separator : --output tmp.cfg
        directPath = "/tmp/glibc.missing"
        addDirectCmd = "python2.7 extractDirectGlibcSyscalls.py --callgraph {} --binpath {} --separator : --output {}"
        cmd = addDirectCmd.format(finalCallgraph, options.libcpath, directPath)
        returncode, out, err = util.runCommand(cmd)
        if ( returncode != 0 ):
            rootLogger.error("Error running direct syscall script: %s", err)
            sys.exit(-1)

        #cat tmp.cfg  >> glibc.2.33/wrapper.out.new
        finalCmd = "cat {}  >> {}"
        cmd = finalCmd.format(directPath, finalCallgraph)
        returncode, out, err = util.runCommand(cmd)
        if ( returncode != 0 ):
            rootLogger.error("Error running cat: %s", err)
            sys.exit(-1)
