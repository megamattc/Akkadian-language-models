import os
import re
import sys
import json
import csv
import pandas as pd

#Concatenates all the files in input directory and adds a comment line before each one of the pnumber

input_file_name = "Bodypart_constructions_saa10_13_16_17_18_19_21_augmented_split_nox.csv"
input_file = open(input_file_name,'r',newline='',encoding="utf-8")
header_row = ["tlemma","rlemma","slemma","date","dialect","oolemma","dolemma","tidx","sidx","ridx","ooidx","doidx","ruler",
                    "Tiglath-pileser III","Sargon II","Sennacherib","Esarhaddon","Ashurbanipal","Sîn-šarru-iškun",
                    "tword","sword","rword","ooword","doword","Bad_analysis","etype","ootype","dotype","pcom","sennum","tnum","Translation","Speaker","Addressee","Sender","Recipient","Rhetorical_mode","Verb_metaphor_status","Verb_metonymy_status","PP_type","PP_metaphor_status","PP_metonymy_status","Notes","designation","ancient_author","ancient_recipient","provenience","genre","sender_loc"]



output_file_name1 = "Bodypart_constructions_saa10_13_16_17_18_19_21_augmented_summarized1.csv"
output_file_name2 = "Bodypart_constructions_saa10_13_16_17_18_19_21_augmented_summarized2.csv"


df = pd.read_csv(input_file_name)

#Filter out Bad_analysis == x

df[df["Bad_analysis"] != "x"]

dfc_long = df.value_counts(["tlemma","rlemma","slemma","ruler","Rhetorical_mode","Verb_metaphor_status","PP_type","PP_metaphor_status","PP_metonymy_status"])
dfc_short = df.value_counts(["tlemma","rlemma","slemma","ruler"])

#dfc_short = dfc_short.sort_values(level=["tlemma","slemma","rlemma","dialect","ruler"],ascending=(True,True,True,True,True))

dfc_long.to_csv(output_file_name1)
dfc_short.to_csv(output_file_name2)
#Write header row of output file
#writer.writeheader()

