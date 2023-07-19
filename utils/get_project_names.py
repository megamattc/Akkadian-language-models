import os
import re
import sys
import json

#Concatenates all the files in input directory and adds a comment line before each one of the pnumber

input_dir = "corpusjson"
cwd = os.getcwd()
input_path = os.path.join(cwd,input_dir)

#print(input_path)
outputFileName = "project_names_dict.json"
oracc_str = "http://oracc.org/" #Base url string
new_dict = {} #Dictionary to be printed to output

output_file = open(outputFileName,'w',encoding="utf-8")

for path, dirs, filenames in os.walk(input_path):
    print("path")
    print(path)
    for filename in filenames:
        print("Processing: " + filename)

        file_with_path = os.path.join(path, filename)
        print(file_with_path)
        file = open(file_with_path, 'r', encoding="utf-8")

        file_dict = json.load(file)


        project_name = file_dict["project"]


        #If the project is tcma, its Pfiles are under 'proxies', and we currently want only the tcma/assur files
        if project_name == "tcma":
            members = file_dict["proxies"]
            for file in members.keys():
                new_dict.update({file:oracc_str + members[file] + "/" + file})

        #Otherwise, the other projects have Pfiles under 'members', and project name is just value of 'project'
        else:
            members = file_dict["members"]
            for file in members.keys():

                new_dict.update({file:oracc_str + project_name + "/" + file})


print(new_dict,file=output_file)



