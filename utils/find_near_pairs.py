import re
import os
import csv
import sys

inputFileName = "Bodypart_constructions_saa10_13_16_17_18_19_21_augmented_summarized2.csv"

inputFile = open(inputFileName, 'r')

#header_row = ["tlemma+rlemma+slemma","ruler","Count"]
#reader = csv.DictReader(inputFile,fieldnames=header_row)

lines = inputFile.readlines()

for i in range(1,len(lines)-1):
    line = lines[i]
    form, ruler, count = line.split(",")
    verb_form, pp_form, bp_form = form.split("+")
    for j in range(i+1,len(lines)-1):
        new_line = lines[j]
        new_form, new_ruler, new_count = new_line.split(",")
        new_verb_form, new_pp_form, new_bp_form = new_form.split("+")

        if verb_form != new_verb_form:
            break
        #ruler == "Tiglath-piles"
        elif pp_form == new_pp_form and bp_form != new_bp_form and ruler != new_ruler:
            print("Line1: " + line.rstrip())
            print("Line2: " + new_line)

        elif pp_form != new_pp_form and bp_form == new_bp_form and ruler != new_ruler:
            print("Line1: " + line.rstrip())
            print("Line2: " + new_line)


