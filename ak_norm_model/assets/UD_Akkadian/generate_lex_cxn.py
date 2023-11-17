import os
from collections import Counter
import sys

verb_feat_list = [
    "Tense",
    "Person",
    "Gender",
    "Case",
    "VerbForm",
    "Mood",
    "VerbStem",
    "SubSuff",
    "Subordinative",
    "Ventive",
    "Question",
    "Focus",
    "VerbSuffNum",
    "VerbSuffGen",
    "VerbSuffPer",
    "Dialect"
]

noun_feat_list = [
    "Gender",
    "Case",
    "Number",
    "Focus",
    "PossSuffGen",
    "PossSuffNum",
    "PossSuffPer",
    "NounBase",
    "Question",
    "Dialect"
]

syn_dep_types = ['obj','iobj','obl','mark','advmod','ccomp','discourse','cop','csubj','dep','dislocated','fixed','advcl',
                 'cc','nmod','nsubj','acl','orphan','parataxis','root','vocative','xcomp']

def get_feature_value_pairs(morph_str: str) -> dict:
    feat_dict = {}

    #Check if morph_str actually has feature-value pairs
    if "=" not in morph_str:
        return feat_dict
    morph_array = morph_str.split("|")
    for pair_str in morph_array:

        (feature,value) = (pair_str.split("=")[0],pair_str.split("=")[1])
        feat_dict[feature] = value

    return feat_dict

#Fill out set of keys of a feature dictionary of verb and set values to "NULL"
def fill_out_dict(feat_dict: dict,pos_list: list) -> dict:
    feat_dict_keys = feat_dict.keys()
    for key in pos_list:
        if key not in feat_dict_keys:
            feat_dict[key] = "NULL"

    return feat_dict


#Concatenates all the files in input directory and adds a comment line before each one of the pnumber

input_dirs = sys.argv[1:len(sys.argv)]
cwd = os.getcwd()

#input_path = os.path.join(cwd,input_dir)

#print(input_path)
outputFileName = "akk_verb_cxn.lisp"
outputFileNameVerbValency = "akk_verb_valency.csv"
outputFileNameNoun = "akk_noun_cxn.lisp"


output_file_verb = open(outputFileName,'w',encoding="utf-8")
output_file_valency = open(outputFileNameVerbValency,'w',encoding="utf-8")
output_file_noun = open(outputFileNameNoun,'w',encoding="utf-8")


verb_dict = {}
noun_dict = {}
master_valency_dict = {}

for input_dir in input_dirs:
    for path, dirs, filenames in os.walk(os.path.join(cwd,input_dir)):
        print("path")
        print(path)
        for filename in filenames:
            print(filename)
            if not (filename.endswith('.conllu')):
                print("skipping")
                continue

            file_with_path = os.path.join(path, filename)
            file = open(file_with_path, 'r', encoding="utf-8")

            file_lines = file.readlines()

            #Dictionary to check for arguments of verb
            valency_dict = {}

            #Run through lines first time to process all lexical items
            for line in file_lines:
                line_array = line.rstrip().split("\t")

                #Check if line is a conllu line
                if len(line_array) != 10:
                    continue

                ud_pos = line_array[3]
                oracc_pos = line_array[4]
                morph_str = line_array[5]
                form =line_array[1]
                lemma = line_array[2]
                index = line_array[0]

                if ud_pos == "VERB":
                    #print(morph_str)
                    feat_dict = get_feature_value_pairs(morph_str)
                    verb_dict[(form,lemma)] = fill_out_dict(feat_dict,verb_feat_list)
                    valency_dict[index] = [lemma]

                if ud_pos == "NOUN":
                    feat_dict = get_feature_value_pairs(morph_str)
                    noun_dict[(form, lemma)] = fill_out_dict(feat_dict,noun_feat_list)

            # Run through lines second time to check for arguments of verbs
            for line in file_lines:
                line_array = line.rstrip().split("\t")

                # Check if line is a conllu line
                if len(line_array) != 10:
                    continue


                syn_dep = line_array[6]
                syn_type = line_array[7]

                if syn_dep in valency_dict.keys():
                    valency_dict[syn_dep].append(syn_type)

            for index in valency_dict.keys():
                l = valency_dict[index]
                v = l[0]
                #print("v")
                #print(v)
                if v not in master_valency_dict.keys():
                    master_valency_dict[v] = []

                for i in range(1,len(l)):
                    master_valency_dict[v].append(l[i])

print(len(master_valency_dict.keys()))

#Now print out cxn file for verbs

processed_lemmas = set()

for entry in verb_dict.keys():

    (form,lemma) = entry
    #print("entry")
    #print(entry)
    feat_dict = verb_dict[entry]
    transitive_info = "unknown"

    #Get valency info for lemma of verb
    if lemma in master_valency_dict.keys():
        valency_info = master_valency_dict[lemma]
    else:
        valency_info = []
        master_valency_dict[lemma] = valency_info


    if 'obj' in valency_info:
        transitive_info = "transitive"

    else:
        transitive_info = "intransitive"

    master_valency_dict[lemma].append(transitive_info)

    output_str = f'(def-fcg-cxn {form}-cxn\n' \
                 f'\t((?{form}-word\n' \
                 f'\t\t(args (?x ?y))\n' \
                 f'\t\t(sem-cat\n' \
                 f'\t\t\t(sem-class relation)\n' \
                 f'\t\t)\n' \
                 f'\t\t(syn-cat\n' \
                 f'\t\t\t(lex-class verb)\n' \
                 f'\t\t\t(type {transitive_info})\n' \
                 f'\t\t\t(lemma {lemma})\n' \
                 f'\t\t\t(tense {feat_dict["Tense"]})\n' \
                 f'\t\t\t(person {feat_dict["Person"]})\n' \
                 f'\t\t\t(gender {feat_dict["Gender"]})\n' \
                 f'\t\t\t(mood {feat_dict["Mood"]})\n' \
                 f'\t\t)\n' \
                 f'\t)\n' \
                 f'\t<-\n' \
                 f'\t(?{form}-word\n' \
                 f'\t\t(HASH meaning ((do ?x ?y)))\n' \
                 f'\t\t--\n' \
                 f'\t\t(HASH form ((string ?{form}-word "{form}"))))))\n'

    print(output_str,file=output_file_verb)


for entry in noun_dict.keys():

    (form,lemma) = entry
    #print("entry")
    #print(entry)
    feat_dict = noun_dict[entry]

    output_str = f'(def-fcg-cxn {form}-cxn\n' \
                 f'\t((?{form}-word\n' \
                 f'\t\t(args (?x))\n' \
                 f'\t\t(sem-cat\n' \
                 f'\t\t\t(sem-class physical-object)\n' \
                 f'\t\t\t(focus {feat_dict["Focus"]})\n' \
                 f'\t\t)\n' \
                 f'\t\t(syn-cat\n' \
                 f'\t\t\t(lex-class noun)\n' \
                 f'\t\t\t(lemma {lemma})\n' \
                 f'\t\t\t(case {feat_dict["Case"]})\n' \
                 f'\t\t\t(noun-base {feat_dict["NounBase"]})\n' \
                 f'\t\t\t(gender {feat_dict["Gender"]})\n' \
                 f'\t\t\t(number {feat_dict["Number"]})\n' \
                 f'\t\t\t(focus {feat_dict["Focus"]})\n' \
                 f'\t\t\t(poss-suff-num {feat_dict["PossSuffNum"]})\n' \
                 f'\t\t\t(poss-suff-gen {feat_dict["PossSuffGen"]})\n' \
                 f'\t\t\t(poss-suff-per {feat_dict["PossSuffPer"]})\n' \
                 f'\t\t\t(question {feat_dict["Question"]})\n' \
                 f'\t\t)\n' \
                 f'\t)\n' \
                 f'\t<-\n' \
                 f'\t(?{form}-word\n' \
                 f'\t\t(HASH meaning (({lemma} ?x)))\n' \
                 f'\t\t--\n' \
                 f'\t\t(HASH form ((string ?{form}-word "{form}"))))))\n'

    print(output_str,file=output_file_noun)


#Print header for verb table
h = 'verb'

for i in range(0,len(syn_dep_types)):
    h = h + "\t" + syn_dep_types[i]


print(h,file=output_file_valency)

for verb in master_valency_dict.keys():
    valency_info = master_valency_dict[verb]

    valency_type = "unknown"
    counts = Counter(valency_info)


    if "transitive" in valency_info:
        valency_type = "transitive"
    elif "intransitive" in valency_info:
        valency_type = "intransitive"

    #Start of string
    s = verb

    for rel in syn_dep_types:
        s = s + "\t" + str(counts[rel])

    print(s, file=output_file_valency)








