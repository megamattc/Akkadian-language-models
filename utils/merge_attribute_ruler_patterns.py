import json, sys
import tqdm


#Merge attributes of a form, where we have to be careful b/c the same key in the two dicts can have different values (e.g. "NOUN" and "N" for "POS", or the "MORPH" entry)
def merge_attrs(attrDict1: dict, attrDict2: dict):

    #Test: for now, just use |
    keys1 = attrDict1.keys()
    keys2 = attrDict2.keys()

    mergeDict = {}

    totalKeys = list(set(list(keys1)+list(keys2)))

    for key in totalKeys:

        if key not in keys1:
            mergeDict.update({key:attrDict2[key]})
        elif key not in keys2:
            mergeDict.update({key:attrDict1[key]})
        #If key is common to both entries and is a MORPH key, combine all morphological features from both entries
        elif key == "MORPH":
            #For now, we only care if a form has two specifications for UFeats
            list1 = attrDict1[key].split("|")
            list2 = attrDict2[key].split("|")

            combList = list(set(list1+list2))

            combStr = "|".join(combList)

            mergeDict.update({key:combStr})
        #Else for some other type of key we have not yet dealt with common to both entries, take only first entry for now (NB: This includes for instance cases where one entry has
        #"TAG" = "V" and the other "TAG" = "VERB". Currently we take from only  the first comparandum
        else:
            mergeDict.update({key:attrDict1[key]})



    return mergeDict



inputFileName1 = "attribute_ruler_patterns_1_2_5_9_15_anzu_barutu_rinap4.json" #File names of input attribute ruler files
inputFileName2 = "attribute_ruler_patterns_1_2_5_9_15_anzu_barutu_rinap4.json"

outputFileName = "attribute_ruler_patterns_1_2_5_9_15_anzu_barutu_rinap4.json" #File name of output attribute ruler file

inputFile1 = open(inputFileName1, 'r')
attributeList1 = json.load(inputFile1)

inputFile2 = open(inputFileName2, 'r')
attributeList2 = json.load(inputFile2)

outputFile = open(outputFileName, 'w')
attributeList3 = []

mergeCounter = 0 #Keep track of number of merges

for patternPair1 in attributeList1:
    pattern1 = patternPair1["patterns"]
    patternDic1 = pattern1[0][0]  # We are assuming here that there is only one pattern dictionary in each pattern:attr pair
    #print("patternDic1")
    #print(patternDic1)
    attrsDic1 = patternPair1["attrs"]
    #print("attrsDic1")
    #print(attrsDic1)

    matchFound = False #Marker to keep track if patternPair1 has matched against something in attributeList2


    for patternPair2 in attributeList2:
        pattern2 = patternPair2["patterns"]
        patternDic2 = pattern2[0][0]
        attrsDic2 = patternPair2["attrs"]

        #print("patternDic2")
        #print(patternDic2)
        #print("attrsDic2")
        #print(attrsDic2)

        #If pattern dictionaries match, merge the attributes and append to output attribute list
        if patternDic1 == patternDic2:
            mergeAttrsDic = merge_attrs(attrsDic1,attrsDic2)
            attributeList3.append({"patterns":pattern1,"attrs":mergeAttrsDic})

            print("patternDic1")
            print(patternDic1)
            print("attrsDic1")
            print(attrsDic1)
            print("attrsDic2")
            print(attrsDic2)
            print("mergeAttrDic")
            print(mergeAttrsDic)

            mergeCounter += 1
            matchFound = True #Indicate match found

            #Remove the common pattern pair from second input attribute lists after adding it to the output attribute list
            attributeList2.remove(patternPair2)

    #If patternPair1 didn't match anything in attributeList2, add it to output attribute list
    if matchFound == False:
        attributeList3.append(patternPair1)

#Finally, add remaining patternPairs from attributeList2 to output attribute list after common ones have been merged and added to output and removed from atrributeList2
for patternPair2 in attributeList2:
    attributeList3.append(patternPair2)

print(attributeList3, file=outputFile)
print("Made " + str(mergeCounter) + " merges")



