import pandas as pd
import ipywidgets as widgets
import zipfile
import json
from tqdm.auto import tqdm
import os
import sys
import utils
from collections import Counter

def parsejson(text, meta_d):
    lemmas = []
    for JSONobject in text["cdl"]:

        #Since cdl key appears after node, type info in a JSON object, we need to have this first clause before the recusive condition
        if JSONobject["node"] == "c" and JSONobject["type"] == "sentence" and "label" in JSONobject:
            meta_d["chunk"] = JSONobject["label"] #Get chunk name from 'label' key when appearing with node:c, type:sentence

        elif "label" in JSONobject:
            meta_d["label"] = JSONobject['label']   # `label` is the line number; it stays constant until
                                                    # the process move to a new line

        if "cdl" in JSONobject:
            lemmas.extend(parsejson(JSONobject, meta_d))

        if JSONobject.get("type") == "field-start": # this is for sign lists, identifying fields such as
            meta_d["field"] = JSONobject["subtype"]  # sign, pronunciation, translation.
        elif JSONobject.get("type") == "field-end":
            meta_d.pop("field", None)                           # remove the key "field" to prevent it from being copied 
                                                              # to all subsequent lemmas (which may not have fields)
        if "f" in JSONobject:
            lemma = JSONobject["f"]
            lemma["id_word"] = JSONobject["ref"]
            lemma['label'] = meta_d["label"]
            lemma["id_text"] = meta_d["id_text"]
            if "field" in meta_d:
                lemma["field"] = meta_d["field"]
            #If the lemma is embedded in a text chunk, copy over that chunk's label from meta_d
            #if meta_d["chunk"] != None:
            lemma["chunk"] = meta_d["chunk"]
            #print("Got chunk:" + meta_d["chunk"])
            #print("Got label:" + meta_d["label"])
            #print("form")
            #print(lemma["form"])

            lemmas.append(lemma)
        elif JSONobject.get("strict") == "1":      # horizontal ruling on tablet; or breakage
            lemma = {}
            lemma['extent'] = JSONobject['extent']
            lemma['scope'] = JSONobject['scope']
            lemma['state'] = JSONobject['state']
            lemma["id_word"] = JSONobject["ref"]
            lemma["id_text"] = meta_d["id_text"]
            lemmas.append(lemma)
    return lemmas

util_dir = os.path.abspath('../utils')

sys.path.append(util_dir)

os.makedirs('jsonzip', exist_ok = True)
os.makedirs('output', exist_ok = True)

oraccVolume = 'rinap4' #Short name of oracc project
oraccProject = 'rinap/' + oraccVolume #Full name of oracc project

lemmaLookupFileName = 'ak_norm_lemma_lookup_' + oraccVolume + '.json' #Name of file for lemma list
attributeLookupFileName = 'attribute_ruler_patterns_' + oraccVolume + '.json' #Name of file for attribute list
translitLookupFileName = 'akt_trans_lemma_lookup_'+oraccVolume+'.json'

#Get data only from one project (MO: I don't understand what 'placeholder' does - one should be able to use this to process all volumes at once )

projects = widgets.Textarea(
    value=oraccProject,
    placeholder='',
    description='Projects:',
)


print(projects)

project_list = utils.format_project_list(projects.value)
project_list = utils.oracc_download(project_list)


meta_d = {"label": None, "id_text": None,"chunk":None} #"Chunk" key keeps track of which text chunk an item is in, where a chunk consists of a number of complete sentences.

lemm_l = [] # initiate the list that will hold all the lemmatization data of all texts in all requested projects
for project in project_list:
    file = f'jsonzip/{project.replace("/", "-")}.zip'
    try:
        zip_file = zipfile.ZipFile(file)       # create a Zipfile object
    except:
        errors = sys.exc_info() # get error information
        print(file), print(errors[0]), print(errors[1]) # and print it
        continue
    files = zip_file.namelist()     # list of all the files in the ZIP
    files = [name for name in files if "corpusjson" in name and name[-5:] == '.json']                                                                                                  #that holds all the P, Q, and X numbers.
    for filename in tqdm(files, desc = project):       #iterate over the file names
        id_text = project + filename[-13:-5] # id_text is, for instance, blms/P414332
        meta_d["id_text"] = id_text
        try:
            text_json_string = zip_file.read(filename).decode('utf-8')         #read and decode the json file of one particular text
            data_json = json.loads(text_json_string)                # make it into a json object (essentially a dictionary)
            lemm_l.extend(parsejson(data_json, meta_d))     # and send to the parsejson() function
        except:
            e = sys.exc_info() # get error information
            print(filename), print(e[0]), print(e[1]) # and print it
    zip_file.close()


words_df = pd.DataFrame(lemm_l).fillna('')
# replace NaN (Not a Number) with empty string
#print(words_df["cf"])

findreplace = {' ' : '-', ',' : ''}
words_df = words_df.replace({'gw' : findreplace, 'sense' : findreplace}, regex = True)
#print(words_df)

#Take only the linguistic norm without word sense or POS
#words_df["lemma"] = words_df["cf"] + '[' + words_df["gw"] + ']' + words_df["pos"]
words_df["lemma"] = words_df["cf"]

words_df.loc[words_df["cf"] == "" , 'lemma'] = words_df['form'] + '[NA]NA'
words_df.loc[words_df["pos"] == "n", 'lemma'] = words_df['form'] + '[]NU'
#print(words_df[['norm', 'lemma']])




#Make dictionary out of (form, lemma) pairs from words_df
#Note here we are making the choice to have our keys be transliteration forms, not normalized forms

lemmaOutputDic = {}
for index in words_df.index:
    lemmaOutputDic.update({words_df["norm"][index]: words_df["lemma"][index]})


#print (form, lemma) pairs to JSON file
    
savefile =  open(lemmaLookupFileName,'w')
print(lemmaOutputDic, file=savefile)



#Print out dictionary of transliteration forms and their normalization

translitOutputDic = {}

for index in words_df.index:
    norm = words_df["norm"][index]
    form = words_df["form"][index]

    #If a form has no norm (e.g. 'x' or 'x+x', use form for the norm
    if norm == '':
        translitOutputDic.update({form:form})
    else:
        translitOutputDic.update({form:norm})

savefile = open(translitLookupFileName,'w')
print(translitOutputDic, file=savefile)


#Conversion dictionary between Oracc pos terms and UD.
posLabelDic = {"AN":"PROPN","CN":"PROPN","DN":"PROPN","EN":"PROPN","FN":"PROPN","GN":"PROPN","LN":"PROPN","MN":"PROPN","ON":"PROPN","PN":"PROPN","QN":"PROPN","RN":"PROPN","SN":"PROPN","TN":"PROPN","YN":"PROPN","WN":"PROPN","AJ":"ADJ","AV":"ADV","NU":"NUM","CNJ":"CONJ","DET":"DET","J":"INTJ","N":"NOUN","PP":"PRON","V":"VERB","IP":"PRON","DP":"DET","MOD":"PART","PRP":"ADP","QP":"PRON","RP":"PRON","REL":"PRON","SBJ":"SCONJ","XP":"PRON","u":"X","n":"NUM","X":"X","NN":"NN","":""}

demPronList = ["annû","ullû","annītu","annūti","annūtu","ammūti","ammūte","annî"]
negList = ["lā","ai","ul"]


#AttributeRulerList which will contain all the pattern-attribute pairs for all forms from the Oracc project
attrRulerList = []

for index in words_df.index:
    #If the token has no normalization (e.g. an x), skip
    if words_df["norm"][index] == '':
        continue

    #Otherwise, take the token and define its coarse and fine pos
    norm = words_df["norm"][index]
    lemma = words_df["lemma"][index]
    finePosType = words_df["pos"][index]
    tokenAttrDic = {}
    #print(lemma)
    #print(finePosType)
    # There are some exceptions/manual relabelings necessary between Oracc/UD

    #Reassign fine pos of ša when used in noun construct from Oracc's DET to PRP (this preserves category relation ADP > PRP)
    if lemma == "ša" and finePosType == "DET":
        tokenAttrDic.update({"POS": "ADP"})
        tokenAttrDic.update({"TAG": "PRP"})
    #Reassign coarse pos of demonstrative pronouns like annû to determiners
    elif lemma in demPronList:
        tokenAttrDic.update({"POS": "DET"})
        tokenAttrDic.update({"TAG": "DP"})
    #Reassign coarse/fine pos of šumma from Oracc's MOD/MOD (modal) to UD SCONJ/Oracc's SBJ (subordinating conjunction)
    elif lemma == "šumma":
        tokenAttrDic.update({"POS": "SCONJ"})
        tokenAttrDic.update({"TAG": "SBJ"})
    #Reassign lā from MOD/MOD to PART/NEG
    elif lemma in negList:
        tokenAttrDic.update({"POS": "PART"})
        tokenAttrDic.update({"TAG": "NEG"})
    #Otherwise, no substitution needed
    else:
        tokenAttrDic.update({"POS":posLabelDic[finePosType]})
        tokenAttrDic.update({"TAG": finePosType})

    patternPair = {"patterns": [[{"ORTH": norm}]]}
    attributePair = {"attrs": tokenAttrDic}
    # Add the two by adjoining second to the first
    patternPair.update(attributePair)
    # Add result to dictionary with key given by the lemma
    attrRulerList.append(patternPair)


savefile =  open(attributeLookupFileName,'w')
print(attrRulerList, file = savefile)

#Now create JSON file that stores, for each token, the coarse pos and fine pos labels of that PN. The format of the JSON file is a list of dictionaries, each dictionary being a key-value (pattern, attrs) representing a PN and its attributes. It is meant to be compatible with the file attribute_ruler_patterns.json, which is part of the spacy AttributeRuler pipeline component that provides attributes to a token.

PNAttrOutputList = []

for index in words_df.index:
    #print(words_df["pos"][index])
    pos_entry = words_df["pos"][index]
    if pos_entry in PNList:
        pn_entry = {}
        pn_entry.update({"patterns":[[{"ORTH":words_df["norm"][index]}]]})
        pn_entry.update({"attrs":{"POS":"PROPN","TAG":pos_entry}})
        PNAttrOutputList.append(pn_entry)

#Print to JSON file
savefile =  open('ak_pn_attributes.json','w')
print(PNAttrOutputList, file=savefile)






#Create transliterated text files, with one line per verse line separated by newline

#First get line info
#words_df['id_line'] = [int(wordid.split('.')[1]) for wordid in words_df['id_word']]
#print(words_df['id_line'])
#lines = words_df.groupby([words_df['id_text'], words_df['id_line'], words_df['label']]).agg({
#        'norm1': ' '.join,
#    }).reset_index()

#Now construct the transliterated texts

#Construct the transliterated texts

#texts_translit = words_df.groupby([words_df['id_text']]).agg({'form': ' '.join,
# }).reset_index()

texts_translit = words_df.groupby([words_df['id_text'], words_df['chunk']]).agg({
        'form': ' '.join,
    }).reset_index()

PNumSet = set()

for idx, Q in enumerate(texts_translit["id_text"]):
    PNumSet.add(Q[-7:])

PNumList = list(PNumSet)

os.makedirs('output_translit', exist_ok = True)

for PNum in PNumList:
    savefile = f'{PNum}.txt'
    with open(f'output_translit/{savefile}', 'w', encoding="utf-8") as w:
        text_frame = texts_translit[texts_translit["id_text"].str.contains(PNum)]

        with open(f'output_translit/{savefile}', 'w', encoding="utf-8") as w:
            text_frame["form"].to_csv(w, index = False, header=False)

#Create normalized text files, with one line per verse line separated by newline

#Get the normalized texts

words_df["norm1"] = words_df["norm"]
words_df.loc[words_df["norm1"] == "" , 'norm1'] = words_df['form']

#Get line info
words_df['id_line'] = [int(wordid.split('.')[1]) for wordid in words_df['id_word']]
#print(words_df['id_line'])
#lines = words_df.groupby([words_df['id_text'], words_df['id_line'], words_df['label']]).agg({
#        'norm1': ' '.join,
#    }).reset_index()

texts_norm = words_df.groupby([words_df['id_text'],words_df['chunk']]).agg({
        'norm1': ' '.join,
    }).reset_index()

#print(texts_norm["id_text"])

PNumSet = set()

os.makedirs('output_norm', exist_ok = True)

for idx, Q in enumerate(texts_norm["id_text"]):
    PNumSet.add(Q[-7:])

PNumList = list(PNumSet)

for PNum in PNumList:
    savefile = f'{PNum}.txt'
    with open(f'output_norm/{savefile}', 'w', encoding="utf-8") as w:
        text_frame = texts_norm[texts_norm["id_text"].str.contains(PNum)]

        with open(f'output_norm/{savefile}', 'w', encoding="utf-8") as w:
            text_frame["norm1"].to_csv(w, index = False, header=False)
