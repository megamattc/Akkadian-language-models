import math

#Check conllu file by producing new conllu file with proportional interval [q-p] (0=< p,q <= 1) of original conllu file, which can then be fed into Inception.

inputFile = open("akk_riao-ud-testRenumbered.conllu", 'r')
outputFile = open("test.conllu", 'w')

lines = inputFile.readlines()

q=0.00
p=1.00

minLineNum = math.floor(q*len(lines))
maxLineNum = math.floor(p*len(lines))

for index in range(minLineNum,maxLineNum):
    line = lines[index].rstrip('\n')
    #print(line)
    print(line, file=outputFile)

print("q, p are "+str(q) + "," + str(p))
print("Printed lines " + str(minLineNum) + " to " + str(maxLineNum))

#We may need to print some extra lines to finish off the current text the above for loop stopped on. Otherwise the conllu file may be incomplete.

appendCounter = maxLineNum

while appendCounter != len(lines): 

        lineArray = lines[appendCounter].rstrip('\n').split('\t') #Get next line after we stopped from above

        #print(lineArray)
        
        if ((len(lineArray) > 0) and (("#" in lineArray[0]) == False)): #If that line is not empty and isn't a comment line,
                print(lines[appendCounter].rstrip('\n'), file=outputFile)
                appendCounter = appendCounter+1
        else:
            break #Otherwise stop outputting
        
print("Continued down to line "+str(appendCounter))
