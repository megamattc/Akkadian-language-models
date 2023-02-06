import json

#Specify which dictionaries to merge

fileName1 = "ak_lemma_lookup_1_2_5_9_15_anzu_barutu_riao.json"
fileName2 = "ak_lemma_lookup_rinap4.json"

outputFile = open("ak_lemma_lookup_1_2_5_9_15_anzu_barutu_riao_rinap4.json", 'w')


file1 = open(fileName1, 'r')
file2 = open(fileName2, 'r')


lemmaDic1 = json.load(file1)
lemmaDic2 = json.load(file2)

lemmaDic1.update(lemmaDic2)

print(lemmaDic1,file=outputFile)
