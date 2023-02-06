import json

translitFile = open('ak_transliteration_lookup_saa01.json','r')
attributeFile = open('attribute_dictionary_transliteration.json','w')


translitDic = json.load(translitFile)
attributeOutputList = []

for translitToken in translitDic.keys():
    patternPair = {"patterns": [[{"ORTH": translitToken}]]}
    attributePair = {"attrs": {"NORM": translitDic[translitToken]}}

    patternPair.update(attributePair)
    attributeOutputList.append(patternPair)

print(attributeOutputList,file=attributeFile)