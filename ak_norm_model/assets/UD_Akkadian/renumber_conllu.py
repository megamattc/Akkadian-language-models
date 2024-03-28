import os
import re
import sys

inputFileNameBase = os.path.splitext(sys.argv[1])[0]
outputFileName = inputFileNameBase+"Renumbered.conllu"

inputFile = open(inputFileNameBase+".conllu", 'r')
outputFile = open(outputFileName, 'w')

lines = inputFile.readlines()

blockDict = {}
index = 0

while index < len(lines): #Split lines up according to empty line, i.e. separate texts, and put them into dictionary keyed by index of first line in text (including header)
    currentBlock = []

    while (index < len(lines)) and (lines[index].rstrip('\n') != "") == True: #We have not yet reached the end of a block 
        currentBlock.append(lines[index])
        index = index+1

    blockDict.update({index-len(currentBlock):currentBlock})
    index = index+1

#print(blockDict.keys())

for key in sorted(blockDict.keys()): #Go through keys in sorted order, so output texts are in same order as original
    currentBlock = blockDict[key]
    textBlock = currentBlock[2:len(currentBlock)+1] #Cut out first two lines, which are header
    textBlockLength = len(textBlock)

    sequentialArray = list(range(1,textBlockLength+1)) #Create array wholes values are sequence 1...textBlockLength

    blockIDArray = []

    print(currentBlock[0].rstrip(), file=outputFile) #First print header of current text to output file
    print(currentBlock[1].rstrip(), file=outputFile)
    
    for index in range(0,textBlockLength): #Get ID's of all tokens in text
        ID = int(textBlock[index].split('\t')[0])
        blockIDArray.append(ID)


    sequentialIDDict = dict(zip(sequentialArray,blockIDArray)) #Zip the two arrays to create dictionary whose keys are sequential integers, values ID's of tokens in text
    #print(sequentialIDDict)
    

    headColumn = [] #Array to contain values of head column
    IDColumn = [] #ditto for ID column
    
    for index in range(0,textBlockLength): #Get head values from column index 6, ID values from column index 0
        currentLine = textBlock[index]
        currentLineArray = currentLine.split('\t')
        headColumn.append(currentLineArray[6]) #Storing head, ID values as strings
        IDColumn.append(currentLineArray[0])

        
    for key in sorted(sequentialIDDict.keys()): #For each key in sequentialIDDict, i.e. for each integer in 1...textBlockLength, replace a head value equal to sequentialIDDict[key] with its corresponding key, and ditto for ID column
        for i in range(0,len(headColumn)):
            if headColumn[i] == str(sequentialIDDict[key]):
                headColumn[i] = str(key) #Relabel entry in head column
                print("replacing head")
            if IDColumn[i] == str(sequentialIDDict[key]):
                IDColumn[i] = str(key) #Relabel entry in head column
                print("replacing ID")
                
    for index in range(0, textBlockLength): #Finally, reconstruct each line of the text with new ID, head values
        currentLine = textBlock[index]
        currentLineArray = currentLine.split('\t')
        currentLineArray[0] = IDColumn[index] #Replace ID, head values in original text, 
        currentLineArray[6] = headColumn[index]

        outputLine = '\t'.join(currentLineArray)

        print(outputLine.rstrip(), file=outputFile) #Print output

    print("",file=outputFile) #Put newline after every text line in original
