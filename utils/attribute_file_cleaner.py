import json

def add_form_to_dict(formDict: dict,form: str, attrDict: dict):
    keys = formDict.keys()
    if form not in keys:
        formDict.update({form:attrs})
    else:
        formAttrDic = formDict[form]
        formDict[form] = merge_attrs(formAttrDic,attrDict)

    return formDict

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
        #Else for some other type of key we have not yet dealt with common to both entries, take only first entry for now
        else:
            mergeDict.update({key:attrDict1[key]})



    return mergeDict





fileName = "attribute_ruler_patterns.json"
file = open(fileName, 'r')
attributeList = json.load(file)

outputFileName = 'att_ruler_patterns_combined.json'
outputFile = open(outputFileName, 'w')

transLemmaFileName = 'ak_transliteration_lookup_saa05.json'
transLemmaFile = open(transLemmaFileName, 'r')

transLemmaDict = json.load(transLemmaFile)

intermediateFormDict = {}

for patternPair in attributeList:

   patterns = patternPair["patterns"]
   attrs = patternPair["attrs"]

   patternDic = patterns[0][0] #Up till now, attribute_ruler_patterns have only one entry in this list

   orth = patternDic["ORTH"]

   if isinstance(orth,str):
       add_form_to_dict(intermediateFormDict,orth,attrs)
   elif isinstance(orth,dict):
       #If ORTH has multiple entries
       orthList = orth["IN"]

       for form in orthList:
           add_form_to_dict(intermediateFormDict,form,attrs)


outputList = []

for form in intermediateFormDict.keys():
    patternPair = {"patterns": [[{"ORTH": form}]]}
    #print("Before:")
    #print(patternPair)
    attributePair = {"attrs": intermediateFormDict[form]}

    patternPair.update(attributePair)

    outputList.append(patternPair)

print(outputList, file=outputFile)



