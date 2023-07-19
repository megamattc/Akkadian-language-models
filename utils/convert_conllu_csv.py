import csv
import json
import pandas as pd
import os, sys
import re





header_row_input = ["index","form","lemma","UPOS","XPOS","morphology","head_index","syn_dep","8","9"]
header_row_output = ["LID","pnum","ppos","label","index","form","lemma","UPOS","XPOS","morphology","head_index","syn_dep","8","9"]



conllu_data_dir = "./conllu_files_output"
count_file_name = "line_count.csv"

output_file_name = "conllu_data.tsv"

output_file = open(output_file_name,'w',newline='',encoding="utf-8")
writer = csv.DictWriter(output_file, delimiter="\t",fieldnames=header_row_output)

# Write header row of output file
writer.writeheader()

#Get list of input conllu files
#input_file_list =

#count_file = open(count_file_name,'r',encding="utf-8")
count_df = pd.read_csv(count_file_name,names=["index","ppos","label"])


for path, dir, input_file_list in os.walk(conllu_data_dir):
    for input_file_name in input_file_list:
        #Check if file is conllu
        if "conllu" in input_file_name:

            pnum = re.search(r'[PQ][0-9]{6}',
                             input_file_name.split(".")[0]).group()  # A few files are not named with Pnum
            # print("pnum")
            # print(pnum)

            input_file = open(os.path.join(path, input_file_name), 'r', encoding="utf-8")

            reader = csv.DictReader(input_file, fieldnames=header_row_input, delimiter="\t")

            for row in reader:
                # If we have comment line, skip
                if "#" in row["index"]:
                    # print("Comment line, skipping")
                    continue

                try:
                    # print("row")
                    # print(row)
                    index = int(row["index"]) - 1
                    # print("index: " + str(index))
                    # Comparison must have 'index' as integer
                    labels_df = count_df.loc[
                        (count_df["index"] == index) & (count_df["ppos"].str.contains(pnum, case=False))]
                    ppos = labels_df.iloc[0]["ppos"]
                    label = labels_df.iloc[0]["label"]

                    # print("labels_df")
                    # print(labels_df)

                    row.update({"pnum": pnum, "ppos": ppos, "label": label})
                    # print("new row")
                    # print(row)

                    writer.writerow(row)

                except:
                    # print("Row")
                    # print(row)
                    e = sys.exc_info()  # get error information
                    print(input_file_name)  # and print it
                    print(e)
                    # print("index")
                    # print(index)
                    # print("labels_df")
                    # print(labels_df)



















