import os
import re
import sys

inputFileNameBase = os.path.splitext(sys.argv[1])[0]
inputFilePNum = re.findall(r'[XPQ][0-9]{6}',inputFileNameBase)[0]
outputFileName = inputFileNameBase+"Numbered.conllu"

inputFile = open(inputFileNameBase+".conllu", 'r')
outputFile = open(outputFileName, 'w')

lines = inputFile.readlines()

sentence_counter = 0

for line in lines:
    
    if "# text = " in line:
        new_line = f'# sent_id = {inputFilePNum}-{str(sentence_counter)}\n' + line
        new_line = new_line.rstrip("\n")
        sentence_counter = sentence_counter + 1
        print(new_line,file=outputFile)

    else:
        print(line.rstrip("\n"),file=outputFile)