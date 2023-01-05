import json

#Helper function to check if lemma is already in the attribute_ruler_patterns.json file

def isInAttributeArray(AttributeArray, lemma):
    foundLemma = False
    #print("Lemma is")
    #print(lemma)
    for dictionary in AttributeArray:
        patternKey = dictionary["patterns"]
        #print("patternKey")
        #print(patternKey)
        #print(patternKey)
        orthoDict = patternKey[0][0]
        orthoEntry = orthoDict["ORTH"]

        if isinstance(orthoEntry, str):
            #print("Checking string")
            #print(orthoEntry)
            if lemma is orthoEntry:
                print("Found lemma in string")
                foundLemma = True
                break
        if isinstance(orthoEntry, dict):
            #print("Checking dict")
            #print(orthoEntry)

            inArray = orthoEntry["IN"]
            #print("inArray")
            #print(inArray)
            if lemma in inArray:
                foundLemma = True
                print("Found lemma in dict")
                break

    return foundLemma

#Read in dictionary of pos tags from input file and print out attribute file to a new json file

posFile = open("ak_upos_lookup.json", 'r')
preexistingFile = open("attribute_ruler_patterns.json", 'r')
finalOutputFile = open("attribute_final.json", 'w')

preexistingArray = json.load(preexistingFile)
posDict = json.load(posFile)

outputArray = []



for lemma in posDict.keys():

    if not isInAttributeArray(preexistingArray,lemma):
        entryDict = {}
        entryDict.update({"patterns": [[{"ORTH": lemma}]]})
        entryDict.update({"attrs": {"POS": posDict[lemma]}})
        outputArray.append(entryDict)
    if isInAttributeArray(preexistingArray,lemma):
        print("Found item")

print(preexistingArray+outputArray, file=finalOutputFile)


