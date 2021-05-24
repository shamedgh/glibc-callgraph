import sys

inputFile = open(sys.argv[1], 'r')
outputFile = open(sys.argv[2], 'w')

inputLine = inputFile.readline()

funcToBbCountDict = dict()
while ( inputLine ):
    filePath = inputLine.strip()
    print("parsing cfg file: " + filePath)
    cfgFile = open(filePath, 'r', errors='replace')
    cfgLine = cfgFile.readline()
    functionName = ""
    while ( cfgLine ):
        cfgLine = cfgLine.strip()

        # extract function name. example: ;; Function __statvfs 
        if ( cfgLine.startswith(";; Function") ):
            splittedCfgLine = cfgLine.split()
            if ( len(splittedCfgLine) >= 3 ):
                functionName = splittedCfgLine[2]
                #print("functionName: " + functionName)

        # extract basic block count. example: ;;  nodes: 0 1 2 3 4 5 6 7 8
        if ( cfgLine.startswith(";;  nodes: 0") ):
            splittedCfgLine = cfgLine.split()
            bbCount = len(splittedCfgLine)-3
            if ( functionName != "" ):
                funcToBbCountDict[functionName] = bbCount
                functionName = ""
            else:
                print ("Problem parsing file: " + filePath + " function is empty" + " in line: " + cfgLine)

        cfgLine = cfgFile.readline()
    cfgFile.close()
    inputLine = inputFile.readline()

inputFile.close()

for functionName, bbCount in funcToBbCountDict.items():
    outputFile.write(functionName + ":" + str(bbCount) + "\n")
    outputFile.flush()
outputFile.close()
