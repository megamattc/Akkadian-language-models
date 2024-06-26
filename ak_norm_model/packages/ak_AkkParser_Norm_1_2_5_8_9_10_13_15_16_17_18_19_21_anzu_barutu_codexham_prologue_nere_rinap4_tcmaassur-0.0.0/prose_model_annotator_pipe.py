import spacy
import ak_AkkParser_Norm_1_2_5_8_9_10_13_15_16_17_18_19_21_anzu_barutu_codexham_prologue_nere_rinap4_tcmaassur as akkModel
import pandas
import os, glob, sys
import json
from spacy.language import Language

import spacy_conll

#Define a helper function that converts conllu files output by the conllu_formatter module to conllu files readable by Inception as one sentence. It takes input string 'lines' containing the Akkadian text in initial conllu format, produces output file 'file2' in final conllu format

def conllu_convert(lines, file2):

    numLines = len(lines)
    currentEmptyLineNumber = 0
    emptyLineCounter = 0


    for index in range(0,numLines-1):
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
                print('\t'.join(lineArray), file=file2) #Print new line to output file

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
                    print('\t'.join(lineArray), file=file2) #Print output
                else:
                    lineArray[0] = newID
                    lineArray[6] = newHead
                    print('\t'.join(lineArray), file=file2) #Print output

#Now define spacy language model

nlp = akkModel.load()


#Add conllu formatter
nlp.add_pipe("conll_formatter", last=True)

#Directories for input text files and where to store final conllu output

#inputPath = './remainder'
folder = sys.argv[1]
inputPath = './' + 'remainder_' + sys.argv[1]
outputPathIntermediate = './conllu_output_intermediate_' + folder + '/'
outputPathFinal = './conllu_output_final_' + folder + '/'

#Get all .txt files in input directory, apply spacy nlp model to get doc files, convert doc file to intermediate conllu format and store in directory given by outputPathIntermediate

for filename in glob.glob(os.path.join(inputPath, '*.txt')):
   with open(os.path.join(os.getcwd(), filename), 'r') as inputFile:
   
       inputFileName = os.path.basename(inputFile.name)
       print(inputFileName)
       inputFileBase = os.path.splitext(inputFileName)[0]
       #print(inputFileBase)
       outputFileNameIntermediate = outputPathIntermediate+inputFileBase+'_intermediate.conllu'
       #print(outputFileName)
       outputFileIntermediate = open(outputFileNameIntermediate, 'w')
       #print("Hello", file=outputFileNameIntermediate)

       #lines = inputFile.readlines() #Get lines from input .txt file. There should just be two lines, the header with saao info, then the entire Akkadian text as one line.

       line = inputFile.read()  # Process lines in a way that avoids turning blank lines, other anomalies into problems for Inception
       lines = line.split("\n")
       lines = [line for line in lines if (not line.isspace() and line != "")]

       for line in lines:
           if "saao" in line:
               print("Found saao in line:")
               print(line)
               continue #Skip header line with saao info
           else:
               print("Line is")
               print(line)
               line = line + " " #Important to avoid parsing errors later

               try:
                    doc = nlp(line)
                    #print("doc._.conll_str")
                    #print(doc._.conll_str)
                    print(doc._.conll_str, file=outputFileIntermediate)
               except Exception as error:
                   print("Could not process line: ",error)


# Convert intermediate conllu files to final conllu format acceptable to Inception

for filename in glob.glob(os.path.join(outputPathIntermediate, '*.conllu')):
   with open(os.path.join(os.getcwd(), filename), 'r') as inputFile:
   
       inputFileName = os.path.basename(inputFile.name)
       print(inputFileName)
       inputFileBase = os.path.splitext(inputFileName)[0]
       print(inputFileBase)
       inputFileBaseWithoutIntermediate = inputFileBase.split("_intermediate")[0] #Get ride of _intermediate substring in file name
       outputFileNameFinal = outputPathFinal+inputFileBaseWithoutIntermediate+'lookup.conllu'
       print(outputFileNameFinal)
       outputFileFinal = open(outputFileNameFinal, 'w')


       lines = inputFile.readlines() #Read in intermediate conllu file as list of lines

       conllu_convert(lines, outputFileFinal) #Convert intermediate conllu file
   
