import pandas as pd
import ipywidgets as widgets
import zipfile
import json
from tqdm.auto import tqdm
import os
import sys
import utils
from collections import Counter
import pprint

def parse_text_json(text, id_text):
    lemmas = []
    for JSONobject in text["cdl"]:
        if "cdl" in JSONobject: 
            lemmas.extend(parse_text_json(JSONobject, id_text))
        if "f" in JSONobject:
            lemm = JSONobject["f"]
            lemm["id_text"] = id_text
            lemmas.append(lemm)
    return lemmas

util_dir = os.path.abspath('../utils')

sys.path.append(util_dir)

os.makedirs('jsonzip', exist_ok = True)
os.makedirs('output', exist_ok = True)

saaVolume = 'saa'

pnTokenizerFileName = 'ak_pn_for_tokenizer_' + saaVolume + '.json' #Name of file for tokens of PN's to be incorporated into tokenizer_exception
lemmaLookupFileName = 'ak_lemma_lookup_' + saaVolume + '.json' #Name of file for lemma list
attributeLookupFileName = 'attribute_ruler_patterns_' + saaVolume + '.json' #Name of file for attribute list
verbCountFileName = 'ak_verb_count.txt'
newVerbFormsFileName = 'ak_new_verb_norms.json'

#Get data from list of projects (MO: I don't understand what 'placeholder' does - one should be able to use this to process all saa volumes at once )

projects = widgets.Textarea(
    value='saao/saa01,saao/saa02,saao/saa05,saao/saa13,saao/saa15,saao/saa16,saao/saa17,saao/saa18,saao/saa19,saao/saa21',
    placeholder='saao/saa05,saao/saa13,saao/saa15,saao/saa16,saao/saa17,saao/saa18,saao/saa19,saao/saa21',
    description='Projects:',
)


print(projects)

project_list = utils.format_project_list(projects.value)
project_list = utils.oracc_download(project_list)



lemm_l = [] # initiate the list that will hold all the lemmatization data of all texts in all requested projects
for project in project_list:
    file = f"jsonzip/{project.replace('/', '-')}.zip"
    try:
        zip_file = zipfile.ZipFile(file)       # create a Zipfile object
    except:
        errors = sys.exc_info() # get error information
        print(file), print(errors[0]), print(errors[1]) # and print it
        continue
        
    files = zip_file.namelist()     # list of all the files in the ZIP
    files = [name for name in files if "corpusjson" in name and name[-5:] == '.json']  

    for filename in tqdm(files, desc=project):  #iterate over the file names
        id_text = project + filename[-13:-5] # id_text is, for instance, blms/P414332
        try:
            text = zip_file.read(filename).decode('utf-8')         #read and decode the json file of one particular text
            data_json = json.loads(text)                # make it into a json object (essentially a dictionary)
            lemm_l.extend(parse_text_json(data_json, id_text))               # and send to the parsejson() function
        except:
            errors = sys.exc_info() # get error information
            print(filename), print(errors[0]), print(errors[1]) # and print it
    zip_file.close()


word_df = pd.DataFrame(lemm_l).fillna('')
# replace NaN (Not a Number) with empty string
#print(word_df)

findreplace = {' ' : '-', ',' : ''}
word_df = word_df.replace({'gw' : findreplace, 'sense' : findreplace}, regex = True)
#print(word_df)

#Take only the linguistic norm without word sense or POS
#word_df["lemma"] = word_df["cf"] + '[' + word_df["gw"] + ']' + word_df["pos"]
word_df["lemma"] = word_df["cf"]

word_df.loc[word_df["cf"] == "" , 'lemma'] = word_df['form'] + '[NA]NA'
word_df.loc[word_df["pos"] == "n", 'lemma'] = word_df['form'] + '[]NU'
#print(word_df[['norm', 'lemma']])

#Make dictionary out of (form, lemma) pairs from word_df
#Note here we are making the choice to have our keys be transliteration forms, not normalized forms

lemmaOutputDic = {}
for index in word_df.index:
    lemmaOutputDic.update({word_df["norm"][index]: word_df["lemma"][index]})


#print (form, lemma) pairs to JSON file
    
savefile =  open(lemmaLookupFileName,'w')
print(lemmaOutputDic, file=savefile)


#Append to PNOutputSet only norms for proper nouns. This will be used to create tokenizer exceptions for the Akkadian language class's tokenizer_exceptions.py file.

PNOutputSet = set()
PNList = ["AN","CN","DN","EN","FN","GN","LN","MN","ON","PN","QN","RN","SN","TN","WN","YN"]

for index in word_df.index:
    #print(word_df["pos"][index])

    if word_df["pos"][index] in PNList and "-" in word_df["norm"][index]:
        PNOutputSet.add(word_df["norm"][index])

#Now construct string of tokenizer exceptions using set of PN lemmas, and print to output file

PNOutputString = ''

for element in PNOutputSet:
    entry = "'"+element+"'"+':'+"[{ORTH:"+"'"+element+"'}],\n"
    PNOutputString = PNOutputString+entry

#Print to JSON file
savefile =  open(pnTokenizerFileName,'w')
print(PNOutputString, file=savefile)

#Now group all the verbs together by lemma and count how many forms there are for each lemma
#But don't count norms we already have morphological information for from the previous attribute_ruler_patterns.json file

#So first get set of exceptional verb norms

attributeRulerPatternFile = open('attribute_ruler_patterns.json','r')
attributeRulerList = json.load(attributeRulerPatternFile)

verbFormExceptionSet = set()

for dictionary in attributeRulerList:
    #IF we already have morphology info for a given form, add it to list of exceptions
    if "VERB" in dictionary["attrs"].values() and "MORPH" in dictionary["attrs"].keys():
        pattern = dictionary["patterns"]
        orth = pattern[0][0]
        #If X = orth["ORTH"], then X is either a string (representing a verb norm) or of the form "IN":[....], where [....] is a list of verb forms with the same lemm
        X = orth["ORTH"]
        if type(X) == list:
            for item in list:
                verbFormExceptionSet.add(item.strip('\"'))
        elif type(X) == str:
            verbFormExceptionSet.add(X.strip('\"'))
#print("VerbFormExceptionSet")
#print(verbFormExceptionSet)

#Now gather the verbs together by lemma, not including norms from the excluded set above
verbFormDic = {}
verbCountDic = {}
totalCountDic = {}
#outputCountDic = {}

for index in word_df.index:
    #print(word_df["pos"][index])
    if word_df["pos"][index] == "V":
        norm = word_df["norm"][index]
        lemma = word_df["lemma"][index]
        #Check if we already have morphological info on this norm
        if norm in verbFormExceptionSet:
            continue

        if lemma not in verbFormDic.keys():
            verbFormDic[lemma] = [norm] #Assign list to each lemma instead of dic to keep track of how many of each norm there are
        else:
            verbFormDic[lemma].append(norm)
print("verbFormDic")
print(verbFormDic)
#Now do counting of items
for lemma in verbFormDic.keys():
    countDic = Counter(verbFormDic[lemma])
    #print(countDic)
    #verbCountDic[lemma] = countDic
    totalCountDic[(countDic.total(),lemma)] = countDic



#print this out to a file

savefile =  open(verbCountFileName,'w')

for (count,lemma) in sorted(totalCountDic.keys(), reverse=True):
    print(lemma + ":" + str(count), file=savefile)
    print(totalCountDic[(count,lemma)], file=savefile)


#Also produce file with just the lemmas and new verb norms in the format of attribute file, so we can add morphology for hand chosen entries quickly and merge it with attribute_ruler_patterns.json
#We won't systematically annotate the new verb norms for morphology (just frequent items), so we still need the systematic attribute file produced later on below

verbAttrRulerDic = {}

for lemma in verbFormDic.keys():
    for norm in verbFormDic[lemma]:

        patternPair = {"patterns": [[{"ORTH": norm}]]}
        print("Before:")
        print(patternPair)
        attributePair = {"attrs": {"POS":"VERB","TAG":"VERB","MORPH": ""}}
        # Add the two by adjoining second to the first
        patternPair.update(attributePair)
        print("After:")
        print(patternPair)
        # Add result to dictionary with key given by the lemma
        verbAttrRulerDic.update({norm: patternPair})

#Output as attribute file
print(verbAttrRulerDic)


verbAttrRulerList = []

for norm in verbAttrRulerDic.keys():
    verbAttrRulerList.append(verbAttrRulerDic[norm])

savefile =  open(newVerbFormsFileName,'w')
print(json.dumps(verbAttrRulerList), file = savefile)

#Conversion dictionary between Oracc pos terms and UD.
posLabelDic = {"AN":"PROPN","CN":"PROPN","DN":"PROPN","EN":"PROPN","FN":"PROPN","GN":"PROPN","LN":"PROPN","MN":"PROPN","ON":"PROPN","PN":"PROPN","QN":"PROPN","RN":"PROPN","SN":"PROPN","TN":"PROPN","YN":"PROPN","WN":"PROPN","AJ":"ADJ","AV":"ADV","NU":"NUM","CNJ":"CONJ","DET":"DET","J":"INTJ","N":"NOUN","PP":"PRON","V":"VERB","IP":"PRON","DP":"DET","MOD":"PART","PRP":"ADP","QP":"PRON","RP":"PRON","REL":"PRON","SBJ":"SCONJ","XP":"PRON","u":"X","n":"NUM","X":"X","NN":"NN"}

demPronList = ["annû","ullû","annītu","annūti","annūtu","ammūti","ammūte","annî"]
negList = ["lā","ai","ul"]


#AttributeRulerList which will contain all the pattern-attribute pairs for all forms from the Oracc project
attrRulerList = []

for index in word_df.index:
    #If the token has no normalization (e.g. an x), skip
    if word_df["norm"][index] == '':
        continue

    #Otherwise, take the token and define its coarse and fine pos
    norm = word_df["norm"][index]
    lemma = word_df["lemma"][index]
    finePosType = word_df["pos"][index]
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
        tokenAttrDic.update({"TAG": "SCONJ"})
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

for index in word_df.index:
    #print(word_df["pos"][index])
    pos_entry = word_df["pos"][index]
    if pos_entry in PNList:
        pn_entry = {}
        pn_entry.update({"patterns":[[{"ORTH":word_df["norm"][index]}]]})
        pn_entry.update({"attrs":{"POS":"PROPN","TAG":pos_entry}})
        PNAttrOutputList.append(pn_entry)

#Print to JSON file
savefile =  open('ak_pn_attributes.json','w')
print(PNAttrOutputList, file=savefile)

#Now create JSON file for Oracc pos tags (i.e. fine pos tages) in corpus.
POSOutputList = []
for index in word_df.index:
    pair = {word_df["norm"][index]: word_df["pos"][index]}
    if pair not in POSOutputList:
        POSOutputList.append(pair)
    #POSOutputDic.update({word_df["norm"][index]: word_df["pos"][index]})


#print (lemma, pos) pairs to JSON file
    
savefile =  open('akk_upos_lookup_'+saaVolume+'.json','w')
print(POSOutputList, file=savefile)

#Now get the normalized texts

word_df["norm1"] = word_df["norm"]
word_df.loc[word_df["norm1"] == "" , 'norm1'] = word_df['form']

texts_norm = word_df.groupby([word_df['id_text']]).agg({
        'norm1': ' '.join,
    }).reset_index()

for idx, Q in enumerate(texts_norm["id_text"]):
    savefile =  f'{Q[-7:]}.txt'
    with open(f'output/{savefile}', 'w', encoding="utf-8") as w:
        texts_norm.iloc[idx].to_csv(w, index = False, header=False)
