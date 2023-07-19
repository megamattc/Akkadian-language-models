import os
import re
import sys
import json
import csv

input_dir = "sparql_query_data"
cwd = os.getcwd()
input_path = os.path.join(cwd,input_dir)

input_file_name1 = "letter_metadata.csv"
input_file1 = open(input_file_name1,'r',encoding="utf-8")
metadata_reader = csv.DictReader(input_file1)
metadata_reader_header = metadata_reader.fieldnames

output_file_name = "letter_metadata.csv"
output_file = open(output_file_name,'w',newline='',encoding="utf-8")

header_row = ["url","ancient_author","ancient_recipient","date","provenience","ruler","genre","dialect","sender_loc"]

writer = csv.DictWriter(output_file,fieldnames=header_row)


#Write header row of output file
writer.writeheader()

#print(input_path)
oracc_str = "http://oracc.org/" #Base url string


for path, dirs, filenames in os.walk(input_path):
    #print("path")
    #print(path)
    for filename in filenames:
        print("Processing catalogue: " + filename)

        file_with_path = os.path.join(path, filename)
        print(file_with_path)
        file = open(file_with_path, 'r', encoding="utf-8")

        sparql_reader = csv.DictReader(file)
        sparql_reader_header = sparql_reader.fieldnames






            writer.writerow({"url":url,"ancient_author":ancient_author,"date":date,"provenience":provenience,"ruler":ruler,"genre":genre,"sender_loc":sender_loc,"dialect":dialect,"ancient_recipient":ancient_recipient})



