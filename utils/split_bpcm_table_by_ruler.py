import os
import re
import sys
import json
import csv

#Concatenates all the files in input directory and adds a comment line before each one of the pnumber

input_file_name = "Bodypart_constructions_saa10_13_16_17_18_19_21_augmented.csv"
input_file = open(input_file_name,'r',newline='',encoding="utf-8")


output_file_name = "Bodypart_constructions_saa10_13_16_17_18_19_21_augmented_split.csv"
output_file = open(output_file_name,'w',newline='',encoding="utf-8")
header_row = ["tlemma","rlemma","slemma","date","dialect","oolemma","dolemma","tidx","sidx","ridx","ooidx","doidx","ruler",
                    "Tiglath-pileser III","Sargon II","Sennacherib","Esarhaddon","Ashurbanipal","Sîn-šarru-iškun",
                    "tword","sword","rword","ooword","doword","Bad_analysis","etype","ootype","dotype","pcom","sennum","tnum","Translation","Speaker","Addressee","Sender","Recipient","Rhetorical_mode","Verb_metaphor_status","Verb_metonymy_status","PP_type","PP_metaphor_status","PP_metonymy_status","Notes","designation","ancient_author","ancient_recipient","provenience","genre","sender_loc"]

reader = csv.DictReader(input_file,fieldnames=header_row)

writer = csv.DictWriter(output_file,fieldnames=header_row)


#Write header row of output file
#writer.writeheader()



for row in reader:

    if row["ruler"] == "Esarhaddon or Ashurbanipal":
        row["Esarhaddon"] = "x"
        row["Ashurbanipal"] = "x"

    elif row["ruler"] == "Sargon II or Sennacherib":
        row["Sargon II"] = "x"
        row["Sennacherib"] = "x"

    elif row["ruler"] == "Tiglath-pileser III or Sargon II":
        row["Sargon II"] = "x"
        row["Tiglath-pileser III"] = "x"

    else:
        ruler_name = row["ruler"]
        print("Ruler_name: " + ruler_name)
        if ruler_name in row.keys():
            row[ruler_name] = "x"

    writer.writerow(row)



