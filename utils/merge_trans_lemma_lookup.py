import json

#Specify transliteration lemma dictionaries to merge
fileName1 = "akt_trans_lemma_lookup_1_5_15_anzu.json"
fileName2 = "akt_trans_lemma_lookup_saa02.json"

#Specify output dictionary
outputFile = open("akt_trans_lemma_lookup_1_2_5_15_anzu_barutu.json", 'w')

file1 = open(fileName1, 'r')
file2 = open(fileName2, 'r')


lemmaDic1 = json.load(file1)
lemmaDic2 = json.load(file2)

lemmaDic1.update(lemmaDic2)

print(lemmaDic1,file=outputFile)
