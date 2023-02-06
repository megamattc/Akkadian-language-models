import json, sys


#List of Oracc+UD POS/TAG labels for later adjustment of TAG label to Oracc format
nounList = ["NOUN","N"]
verbList = ["VERB", "V"]
adjList = ["ADJ","AJ"]
prepList = ["ADP","PRP"]
advList = ["ADV","AV"]

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
        #Adjust TAG labels to Oracc format
        elif key == "TAG":
            if attrDict1["TAG"] in nounList and attrDict2["TAG"] in nounList:
                mergeDict.update({key:"N"})
            if attrDict1["TAG"] in verbList and attrDict2["TAG"] in verbList:
                mergeDict.update({key: "V"})
            if attrDict1["TAG"] in adjList and attrDict2["TAG"] in adjList:
                mergeDict.update({key: "AJ"})
            if attrDict1["TAG"] in prepList and attrDict2["TAG"] in prepList:
                mergeDict.update({key: "PRP"})
            if attrDict1["TAG"] in advList and attrDict2["TAG"] in advList:
                mergeDict.update({key: "AV"})
        #If key is common to both entries and is a MORPH key, combine all morphological features from both entries
        elif key == "MORPH":
            #For now, we only care if a form has two specifications for UFeats
            list1 = attrDict1[key].split("|")
            list2 = attrDict2[key].split("|")

            combList = list(set(list1+list2))

            combStr = "|".join(combList)

            mergeDict.update({key:combStr})
        #Else for some other type of key we have not yet dealt with common to both entries, take only first entry for now
        else:
            mergeDict.update({key:attrDict1[key]})



    return mergeDict

#Merges two pattern pairs using the above function. It assumes the 'keys' of both arguments are equal

def merge_patternPair(patternPair1: dict, patternPair2: dict) -> dict:

    #First check arguments have same keys. If not, return empty dictionary
    if not are_equal_patternPair(patternPair1, patternPair2):
        #print("Patterns are not equal")
        return {}

    else:
        pattern = patternPair1["patterns"]

        attr = merge_attrs(patternPair1["attrs"],patternPair2["attrs"])

    return {"patterns":pattern,"attrs":attr}




#Checks if two pattern pairs are 'equal', meaning their patterns match (basically ORTH, other features) and their POS, TAG labels in attrs.
def are_equal_patternPair(patternPair1: dict, patternPair2: dict) -> bool:

    #Get components
    pattern1 = patternPair1["patterns"]
    patternDic1 = pattern1[0][0]  # We are assuming here that there is only one pattern dictionary in each pattern:attr pair
    attrsDic1 = patternPair1["attrs"]

    pattern2 = patternPair2["patterns"]
    patternDic2 = pattern2[0][0]
    attrsDic2 = patternPair2["attrs"]

    #Set POS, TAG labels to string meaning 'not present' for now
    pos1 = pos2 = "N/A"
    tag1 = tag2 = "N/A"

    keys1 = attrsDic1.keys()
    keys2 = attrsDic2.keys()

    if "POS" in keys1:
        pos1 = attrsDic1["POS"]
    if "POS" in keys2:
        pos2 = attrsDic2["POS"]
    if "TAG" in keys1:
        tag1 = attrsDic1["TAG"]
    if "TAG" in keys2:
        tag2 = attrsDic2["TAG"]

    if patternDic1 == patternDic2 and pos1 == pos2 and tag1 == tag2:
        return True
    else:
        return False

def in_keys(patternPair1: dict, attributeList: list) -> bool:

    if attributeList == []:
        return False
    else:
        for patternPair2 in attributeList:
            if are_equal_patternPair(patternPair1,patternPair2):
                return True

        return False


def get_unique_patternPairs(attributeList: list) -> list:

    attributeListUnique = []

    for patternPair in attributeList:
        if attributeListUnique == []:
            attributeListUnique.append(patternPair)
        elif in_keys(patternPair, attributeListUnique):
            continue

        else:
            attributeListUnique.append(patternPair)

    return attributeListUnique

def merge_into_attributeList(attributeList1: list, patternPair2: dict) -> list:

    attributeList2 = [] #The output list we will return. Note that we assume attributeList1 already has unique 'keys'

    merged = False #Token to see if patternPair2 has been merged into attributeList1

    for patternPair1 in attributeList1:
        if are_equal_patternPair(patternPair1,patternPair2):
            patternPair3 = merge_patternPair(patternPair1, patternPair2)

            attributeList2.append(patternPair3)

            merged = True

        else:
            attributeList2.append(patternPair1)

    if merged == False:
        attributeList2.append(patternPair2)

    return attributeList2



inputFileName1 = sys.argv[1] #File name of input attribute ruler file

outputFileName = sys.argv[2] #File name of output attribute ruler file

inputFile1 = open(inputFileName1, 'r')
attributeList1 = json.load(inputFile1)

outputFile = open(outputFileName, 'w')
#attributeSet2 = set()
attributeList2 = []

#Get list of unique pattern pairs from attribute list, where equality means their 'keys' match a la above

attributeList1Unique = get_unique_patternPairs(attributeList1)

for patternPair1 in attributeList1Unique:

    for patternPair2 in attributeList1:

        if are_equal_patternPair(patternPair1,patternPair2):
            patternPair3 = merge_patternPair(patternPair1,patternPair2)
            attributeList2 = merge_into_attributeList(attributeList2,patternPair3)


print(attributeList2, file=outputFile)




