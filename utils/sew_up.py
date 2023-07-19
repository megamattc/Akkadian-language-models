import re

#Script which will 'sew up' a conllu file split up into many sentences into a file with one single sentence

import os
import re
import sys

inputFileNameBase = os.path.splitext(sys.argv[1])[0]
outputFileName = inputFileNameBase+"Sewnup.conllu"

inputFile = open(inputFileNameBase+".conllu", 'r')
outputFile = open(outputFileName, 'w')

lines = inputFile.readlines()

index = 0 #Keeps track of line in original conllu file
token_counter = 0 #Keeps track of how many tokens are in the text
block_counter = 0  # Keeps track of how many lines are in the current sentence
offset = 0 #Keeps track of how much to adjust a given line in original file based on all the accumulated sentences prior

#saa_pattern = re.compile(r"saao|saa[0-9]{1,2}|/|P[0-9]{6}]") #Regex for initial saao tokens

#Print two initial comment lines
print("#\n#",file=outputFile)

while index < len(lines):
    line = lines[index]
    #If we have come upon a comment line right after an empty line, i.e. starting a new sentence,
    #add number of lines in previous block to offset counter, reset block counter
    if "#" in line and index-1 > 0 and lines[index-1].isspace():
        offset = offset + block_counter
        block_counter = 0 #Restart block counter
        index = index + 1
        continue
    #Else, if we still have comment line or other blank line, or match saa header info, just continue
    elif "#" in line or line.isspace() or re.match(r"saao|saa[0-9]{1,2}|/|P[0-9]{6}]",line) or re.match(r"tcma|assur|/|[Pp][0-9]{6}",line):
        index = index + 1
        continue

    #Otherwise we are dealing with sentence line
    else:
        line_array = line.rstrip("\n").split("\t")
        line_array[0] = str(int(line_array[0]) + offset)

        #If there is a number in slot 7, adjust it by offset
        if line_array[6].isdigit():
            line_array[6] = str(int(line_array[6]) + offset)

        block_counter = block_counter + 1
        index = index + 1
        token_counter = token_counter + 1

    line_adjusted = "\t".join(line_array)
    print(line_adjusted,file=outputFile)
    print("Token_counter: " + str(token_counter))

