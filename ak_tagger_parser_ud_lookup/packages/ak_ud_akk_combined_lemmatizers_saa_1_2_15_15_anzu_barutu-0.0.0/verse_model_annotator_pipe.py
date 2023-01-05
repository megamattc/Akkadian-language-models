import spacy
import ak_ud_akk_combined_lemmatizers_saa_1_2_15_15_anzu_barutu as akkModel
import pandas
import os, glob
import json
from spacy.language import Language

import spacy_conll

#Define a helper function that converts conllu files output by the conllu_formatter module to conllu files readable by Inception as one sentence. It takes input string 'lines' containing the Akkadian text in initial conllu format, and returns a list of lines in final conllu format

def conllu_convert(lines):

    numLines = len(lines)
    currentEmptyLineNumber = 0
    emptyLineCounter = 0

    finalConlluLines = []

    #print("numLines")
    #print(numLines)

    for index in range(0,numLines):
        lineArray = lines[index].split('\t')
        #print(lineArray)
        #print("Line number:")
        #print(index+1)
        #print("Length of lineArray")
        #print(len(lineArray))
        if len(lineArray) == 1: #If we encounter an empty line
            #print("Empty line")
            #print(lineArray)
            currentEmptyLineNumber = index+1 #Set currentEmptyLineNumber = number of current line we are on
            #print("CurrentEmptyLineNumber")
            #print(currentEmptyLineNumber)
            #print("emptyLineCounter")
            #print(emptyLineCounter)
            emptyLineCounter = emptyLineCounter+1 #Keep track of how many empty lines we have encountered up till now
        
        elif len(lineArray) != 10: #If we are on a 'deficient' line, count as empty line and skip
            #print("Encountering deficient line")
            #print(index+1)
            currentEmptyLineNumber = index+1
            emptyLineCounter = emptyLineCounter+1
            continue
        else: #We are on a contentful line
            #print("We are in contentful line")
            stripedLine = lines[index].strip() #We need to get rid of final newline character, which is adjacent to final column element
            lineArray = stripedLine.split('\t')
        
            if emptyLineCounter == 0: #If we are in first block (i.e. no previous empty lines), no need to update lines
                #print('\t'.join(lineArray), file=file2) #Print new line to output file
                finalConlluLines.append('\t'.join(lineArray))
                
            else:  #If we are not in first block
                #print("We are not in first block")
                oldHead = int(lineArray[6]) #Convert head value to integer
                oldDeprel = lineArray[7] #Deprel value
                oldID = int(lineArray[0]) ##Convert head value to integer
                newID = str(oldID+currentEmptyLineNumber-emptyLineCounter) #Shift ID 
                newHead = str(oldHead+currentEmptyLineNumber-emptyLineCounter) #Shift head

                if oldHead == 0: #If we encounter root node
                    lineArray[0] = newID
                    lineArray[6] = "_" #Set head and deprel to _
                    lineArray[7] = "_"

                    finalConlluLines.append('\t'.join(lineArray))
                    #print('\t'.join(lineArray), file=file2) #Print output
                else:
                    lineArray[0] = newID
                    lineArray[6] = newHead

                    finalConlluLines.append('\t'.join(lineArray))
                    #print('\t'.join(lineArray), file=file2) #Print output
    return finalConlluLines

#Now define spacy language model

nlp = akkModel.load()

#We do not load the fst_checker component into the pipeline in this script


#Add conllu formatter

nlp.add_pipe("conll_formatter", last=True)

#Directories for input text files and where to store final conllu output

inputPath = './remainder'

outputPathFinal = './conllu_output_final/'

#Clean out contents of intermediate and final directories, which are probably filled with conllu files from last usage of this script

dir = outputPathFinal
for f in os.listdir(dir):
    os.remove(os.path.join(dir, f))

conlluChunks = []


#Get all .txt files in input directory, apply spacy nlp model to get doc files, convert doc file to final conllu format and store in directory given by outputPathFinal

for filename in glob.glob(os.path.join(inputPath, '*.txt')):
   with open(os.path.join(os.getcwd(), filename), 'r') as inputFile:
   
       inputFileName = os.path.basename(inputFile.name)
       #print(inputFileName)
       inputFileBase = os.path.splitext(inputFileName)[0]
       #print(inputFileBase)
       outputFileNameFinal = outputPathFinal+inputFileBase+'_lookup.conllu'
       #print(outputFileNameIntermediate)
       outputFileFinal = open(outputFileNameFinal, 'w')
       #print("Hello", file=outputFileFinal)

       conlluChunks = []

       #lines = inputFile.readlines()
       #print(lines)
       line = inputFile.read() #Get lines from input .conllu file.
       lines = line.split("\n")
       docs = []
       for line in lines:
           line = line + " " #IT IS VERY IMPORTANT TO HAVE THIS SPACE (OR ANY WHITESPAE) AT THE END OF EACH TEXT LINE, BEFORE FEEDING INTO THE PIPELINE. THE CONLL-CONVERTER NEEDS IT.
           doc = nlp(line)
           docs.append(doc)

       #docs = nlp.pipe(lines)
       print(docs)

       #print("Got to doc._.conll_str")

       #Each doc should represent one line in the text
       for doc in docs:
           try:
               print("doc._.conll")
               print(doc._.conll_str)
               conlluCell = doc._.conll_str.rstrip("\n")
               print("conlluCell")
               print(conlluCell)
               conlluBlock = conllu_convert(conlluCell.split("\n"))
               print("conlluBlock:")
               print(conlluBlock)
               print(type(conlluBlock))
               conlluChunks.append(conlluBlock)  # Store line processed as conllu file (here meaning list of lines equalling such file) in array
           except:
               print("Failed at doc:")
               print(doc._.conll_str)

       #Now sew up the conllu chunks, leaving two lines with # and empty line between them.
       print("conlluChunks")
       print(conlluChunks)

       for conlluBlock in conlluChunks:
           print("conlluBlock:")
           print(conlluBlock)
           # Add separators
           print("\n#\n#", file=outputFileFinal)
           for line in conlluBlock:
               print(line, file=outputFileFinal)



