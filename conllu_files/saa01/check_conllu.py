#Checks for conllu well-formedness.
#Reports if non-comment, non-empty line has less than 10 tab-sep fields,
#if syntactic dep col is wrong
#if morph string is not well-formed

import sys

filename = sys.argv[1]

inputFile = open(filename,'r')

lines = inputFile.readlines()

for i in range(0,len(lines)):
    line = lines[i]
    lineArray = line.rstrip("\n").split("\t")

    if not line.isspace():
        #First check if there are ten tab separated fields in non-empty lines and non-comment fields
        if line[0] == '#':
            continue

        if len(lineArray) != 10:
            print(f'Line {str(i)}: {line} has less than 10 tab-sep fields')
            
        #Also check if position '7'=syntactic dependencies, is either _ or an integer (often the case that positions 7,8 mixed up)
        if len(lineArray) >=6 and lineArray[6] != "_":

            if not lineArray[6].isdigit():
                print(str(i) + ": " + line)
                

        #Check that the morphological parse string is well-formed, provided it exists
        if len(lineArray) >= 5 and lineArray[5] != "_":
            morph_str = lineArray[5]
            morph_array = morph_str.split('|')
            for pair in morph_array:
                if pair == "":
                    print(f'Line {str(i)} has bad morph string: {morph_str}')
                
                pair_elements = pair.split("=")

                if len(pair_elements) != 2:
                    print(f'Line {str(i)} has bad morph string: {morph_str}')

        #Check to make sure no fields are empty strings
        for element in lineArray:
            if element == "":
                print(f'Line {str(i)} has bad field: {line}')
            
