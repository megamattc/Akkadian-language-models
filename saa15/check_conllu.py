import sys

filename = sys.argv[1]

inputFile = open(filename,'r')

lines = inputFile.readlines()

for i in range(0,len(lines)):
    line = lines[i]
    lineArray = line.rstrip("\n").split("\t")

    if len(lineArray) != 10 and not line.isspace():
        print(str(i) + ": " + line)
