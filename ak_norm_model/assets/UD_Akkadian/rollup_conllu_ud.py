#This version of rollup_conllu is for processing conllu files meant for UD website. It differs from the standard rollup_conllu in generating a sent-id line.

import os
import re
import sys
import json

#Concatenates all the files in input directory and adds a comment line before each one of the pnumber

input_dir = sys.argv[1]
cwd = os.getcwd()
input_path = os.path.join(cwd,input_dir)

#print(input_path)
outputFileName = "akk_mcong-ud-" + input_dir + ".conllu"
lines = []

#Open json dict of all Pnums used to train model plast 200 texts of SAA 10, wih keys the Pnums and values the url of text in oracc, containing project name
project_dict_filename = "project_names_dict.json" #json for project file names relative to Pnums
project_file_dict_file = open(project_dict_filename,'r',encoding="utf-8")
project_file_dict = json.load(project_file_dict_file)

output_file = open(outputFileName,'w',encoding="utf-8")

for path, dirs, filenames in os.walk(os.path.join(cwd,input_dir)):
    print("path")
    print(path)
    for filename in filenames:
        print(filename)
        file_url = ""

        if re.findall(r'[P|Q][0-9]{6}',filename):
            print("Found pnum")

            file_with_path = os.path.join(path, filename)
            print(file_with_path)
            file_pnum = re.findall(r'[P|Q][0-9]{6}',filename)[0]

            print("Pnum")
            print(file_pnum)

            if file_pnum in project_file_dict.keys():
                file_url = project_file_dict[file_pnum]

            file = open(file_with_path,'r',encoding="utf-8")

            file_lines = file.readlines()

            #new_group = [f'#{file_pnum}']
            new_group = []

            # If we have url associated with text's pnum, print it for the first sentence
            if file_url != "":
                sent_id = file_url.replace("http://","")
                sent_id = sent_id.replace("/","_")
                sent_id = "# sent-id = " + sent_id
                line2 = sent_id
                new_group.append(line2)  # Add url f text in Oracc with project name

            for i in range(0,len(file_lines)-1):
                line = file_lines[i]
                #If we transition from empty line to text line (whether commented line or no), add commented p-num (for sentences in conllu file beyond the first)
                if line.isspace() and not file_lines[i+1].isspace():
                    #line = "\n"+"#" + filename
                    #new_group.append(line)
                    #If we have url associated with text's pnum
                    if file_url != "":
                        line2 = "\n" + "#" + file_url
                        new_group.append(line2) #Add url f text in Oracc with project name

                else:
                    new_group.append(line.rstrip())

            #new_group.extend(file_lines)
            new_group.append("\n")

            lines.extend(new_group)

for line in lines:
    print(line,file=output_file)


