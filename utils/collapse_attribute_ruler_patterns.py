#I believe this is the older of the attribute file cleaner scripts [MO 5/28/2023]

import json, sys




inputFileName1 = "attribute_ruler_patterns_1_2_5_9_13_15_anzu_barutu_rinap4_tcma-assur.json" #File name of input attribute ruler file

outputFileName = "attribute_ruler_patterns_1_2_5_9_13_15_anzu_barutu_rinap4_tcma-assur_new.json" #File name of output attribute ruler file

inputFile1 = open(inputFileName1, 'r')
attributeList1 = json.load(inputFile1)

outputFile = open(outputFileName, 'w')
#attributeSet2 = set()
attributeList2 = list(set(attributeList1))


print(attributeList2, file=outputFile)




