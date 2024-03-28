import sys

filename = sys.argv[1]

inputFile = open(filename,'r')

lines = inputFile.readlines()

for i in range(0,len(lines)):
    line = lines[i]
    lineArray = line.rstrip("\n").split("\t")

    if not line.isspace():
        #First check if there are ten tab separated fields in non-empty lines
        if len(lineArray) != 10:
            print(str(i) + ": " + line)
            continue
        #Also check if position '7'=syntactic dependencies, is either _ or an integer (often the case that positions 7,8 mixed up)
        if lineArray[6] != "_":

            if not lineArray[6].isdigit():
                print(str(i) + ": " + line)
                continue
