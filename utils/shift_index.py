import os
import re
import sys

inputFileNameBase = os.path.splitext(sys.argv[1])[0]
outputFileName = inputFileNameBase+"_shifted.conllu"

inputFile = open(inputFileNameBase+".conllu", 'r')
outputFile = open(outputFileName, 'w')

lines = inputFile.readlines()

shift = 1 #Amount to shift index of lines and head index by (can be negative)

for index in range(0,len(lines)):
    line = lines[index].rstrip("\n")
    if line.isspace() or line == "":
        print("Line at index " + str(index) + " is space")
        print(line,file=outputFile)
    else:

        line_array = line.split("\t")
        if line_array[0].isdigit():
            line_array[0] = str(int(line_array[0]) + shift)
        if line_array[6].isdigit():
            line_array[6] = str(int(line_array[6]) + shift)

        print("\t".join(line_array),file=outputFile)

        #except:
        #    print("Could not split and replace line:")
        #    print(line)
        #    print(line,file=outputFile)

