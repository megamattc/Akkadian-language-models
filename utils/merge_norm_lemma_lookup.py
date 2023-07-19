import json

#Specify which dictionaries to merge

fileName1 = "ak_norm_lemma_lookup_1_2_5_9_10_13_15_16_17_18_19_21_anzu_barutu_riao_rinap4_tcma-assur.json"
fileName2 = "ak_norm_lemma_lookup_saa08.json"

outputFile = open("ak_norm_lemma_lookup_1_2_5_8_9_10_13_15_16_17_18_19_21_anzu_barutu_riao_rinap4_tcma-assur.json", 'w')


file1 = open(fileName1, 'r')
file2 = open(fileName2, 'r')


lemmaDic1 = json.load(file1)
lemmaDic2 = json.load(file2)

lemmaDic1.update(lemmaDic2)

print(lemmaDic1,file=outputFile)
