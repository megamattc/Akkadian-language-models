import pandas as pd
import ipywidgets as widgets
import zipfile
import json
from tqdm.auto import tqdm
import os
import sys
import utils
from collections import Counter

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

saaVolume = 'saa05'


#Get data from all SAA subprojects

projects = widgets.Textarea(
    value="saao/saa01,saao/saa02,saao/saa03,saao/saa04,saao/saa05,saao/saa06,saao/saa07,saao/saa08,saao/saa09,saao/saa10,saao/saao11,saao/saa12,saao/saa13,saao/saa14,saao/saa15,saao/saa16,saao/saa17,saao/saa18,saao/saa19,saao/saa20,saao/saa21",
    placeholder='saao/saa05,saao/saa13,saao/saa15,saao/saa16,saao/saa17,saao/saa18,saao/saa19,saao/saa21',
    description='Projects:',
)

print("projects")
print(projects)

project_list = utils.format_project_list(projects.value)
project_list = utils.oracc_download(project_list)

print("project_list")
print(project_list)

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
