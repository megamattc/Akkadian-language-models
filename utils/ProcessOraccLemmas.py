
import json

input_file = open("gloss-akk-rinap.json",mode='r',encoding='utf-8')
output_file = open("gloss-akk-rinap.csv",mode='w',encoding='utf-8')


glossary = json.load(input_file)

entries_list = glossary["entries"]

final_glossary = []

for entry in entries_list:
    headword = entry["cf"]
    guideword = entry["gw"]
    pos = entry["pos"]
    senses = []
    senses_pos = []

    for sense in entry["senses"]:
        dict = {"mng":sense["mng"],"pos":sense["pos"]}
        senses.append(dict)

    dict = {"headword":headword,"guideword":guideword,"pos":pos,"senses":senses}

    final_glossary.append(dict)

for entry in final_glossary:
    sense_str = ""
    for sense in entry["senses"]:
        sense_str = sense_str + "," + sense["mng"]

    row = entry["headword"] + "," + entry["pos"] + "," + sense_str

    print(row,file=output_file)