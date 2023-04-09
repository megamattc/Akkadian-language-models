import json, csv

input_file = open("Oracc_lemmas_partial_aligned.csv",newline='',mode='r')
output_file = open("FrameLemmas.csv",mode='w',encoding='utf-8')

csv_reader = csv.DictReader(input_file,fieldnames=["form","pos","sense","lu"])
#print(csv_reader)
lines = []

for row in csv_reader:
    lines.append(row)

for row in lines:
    print("Row:")
    print(row)

    if row["lu"] == "LU":
        print("Found LU")
        form = row["form"]
        pos = row["pos"]
        sense = row["sense"]

        entry = form + "," + pos + "," + sense

        match_check = False



        for row2 in lines:
            #print("Checking row2:")
            #print(row2)
            #If there is another row matching form and pos but not sense
            if (form == row2["form"]) and not (pos == row2["pos"] and sense == row2["sense"]):
                print("Have partial match")
                entry = form + "," + row2["pos"] + "," + row2["sense"]
                print(entry,file=output_file)

                match_check = True

        if match_check == False:
            print(entry,file=output_file)







