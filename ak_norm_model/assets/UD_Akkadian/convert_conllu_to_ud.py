import os
import re
import sys
import json
import csv

input_dir = sys.argv[1] #Directory of conllu files to convert (dev, train, test)
cwd = os.getcwd()
input_path = os.path.join(cwd,input_dir)

output_dir = input_dir + "_ud"
output_path = os.path.join(cwd,output_dir)

for path, dirs, filenames in os.walk(input_path):
    #print("path")
    #print(path)
    for filename in filenames:
        print("Processing file: " + filename)
        file_prefix, file_ext = os.path.splitext(filename)

        #Process only .conllu files
        if file_ext != ".conllu":
            continue

        file_prefix_new = file_prefix+"_converted"
        filename_new = file_prefix_new+file_ext

        file_input_with_path = os.path.join(input_path, filename)
        file_output_with_path = os.path.join(output_path,filename_new)
        print(file_input_with_path)
        print(file_output_with_path)
        file_input = open(file_input_with_path, 'r', encoding="utf-8")
        file_output = open(file_output_with_path,'w',encoding='utf-8')

        lines = file_input.readlines()

        for i in range(0,len(lines)):

            line = lines[i]
            #Replace Tense=Perf -> Aspect=Perf
            line = line.replace("Tense=Perf","Aspect=Perf")

            #Replace VerbForm=Imp -> VerbForm=Fin|Mood=Imp
            line = line.replace("VerbForm=Imp","VerbForm=Fin|Mood=Imp")

            #VerbForm=Prec -> VerbForm=Fin|Mood=Prec
            line = line.replace("VerbForm=Prec","VerbForm=Fin|Mood=Prec")

            #Not certain if there are any vetitives recorded in the corpus, but...
            line = line.replace("VerbForm=Vetitive","VerbForm=Fin|Mood=Imp|Polarity=Neg")

            #Statives
            line = line.replace("VerbForm=Stat","Aspect=Imp")

            #Replace ROOT -> root
            line = line.replace("ROOT", "root")

            #Now for nominal possessive features. Here we need to convert to 'layered features' as described at https://universaldependencies.org/u/overview/feat-layers.html

            line = line.replace("PossSuffGen","Gender[psor]")
            line = line.replace("PossSuffNum", "Number[psor]")
            line = line.replace("PossSuffPer", "Person[psor]")

            #Prepositional suffixes, converted to feature layer of 'obj'

            line = line.replace("PrepSuffGen", "Gender[prep]")
            line = line.replace("PrepSuffNum", "Number[prep]")
            line = line.replace("PrepSuffPer", "Person[prep]")

            #Verbal suffixes, which for NA and(?) NB, mark only oblique objects (acc/dat)

            line = line.replace("VerbSuffGen", "Gender[obj]")
            line = line.replace("VerbSuffNum", "Number[obj]")
            line = line.replace("VerbSuffPer", "Person[obj]")

            #Yes/No Questions -> Interrogative mood

            line = line.replace("Question=Yes", "Mood=Int")

            #Predicative suffixes on nouns

            line = line.replace("PredSuffGen", "Gender[pred]")
            line = line.replace("PredSuffNum", "Number[pred]")
            line = line.replace("PredSuffPer", "Person[pred]")


            #Focus -> MaParticle
            line = line.replace("Focus", "MaParticle")



            #Reorganize morphological features to be alphabetical
            lineArray = line.split("\t")
            if len(lineArray) == 10:
                morph = lineArray[5]
                morphArray = morph.split("|")
                morphArray.sort()
                morph_new = "|".join(morphArray)
                lineArray[5] = morph_new

                #Handle 'x' tokens and other fragments with null head, deprel by making them all root nodes
                head = lineArray[6]
                deprel = lineArray[7]
                if head == "_" and deprel == "_":
                    #Check line counter is not at beginning of file
                    if i > 0:
                        previous_line = lines[i-1]
                        previous_line_array = previous_line.split("\t")
                        if len(previous_line_array) == 10:
                            previous_line_index = previous_line_array[0]
                            head = previous_line_index
                            deprel = "dep"

                            lineArray[6] = head
                            lineArray[7] = deprel

                line_new = "\t".join(lineArray)
                line = line_new

            #Print to new file, removing newline character of input line
            print(line.rstrip(),file=file_output)

        file_input.close()
        file_output.close()








