from argparse import ArgumentParser
import io
import json
import logging
import zipfile
from collections import Counter
from typing import Dict, Set
import requests
from bs4 import BeautifulSoup
import os
import re
import glob
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import ipywidgets as widgets
import sys
import utils





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



output_dir = "output_texts_partial"

res = requests.get('http://oracc.museum.upenn.edu/projects.json')
projects_list = json.loads(res.content)['public']

#utils.oracc_download(projects_list, server="penn")

#This is a partial list of public oracc projects, cutting out things that are all sumerian or which shouldn't be part of the training data (e.g. lexical lists)
projects_list_partial = ['aemw', 'aemw/alalakh/idrimi', 'aemw/amarna', 'aemw/ugarit', 'akklove', 'amgg', 'ario', 'armep', 'arrim', 'asbp', 'asbp/ninmed', 'asbp/rlasb', 'atae', 'atae/assur', 'atae/burmarina', 'atae/durkatlimmu', 'atae/durszarrukin', 'atae/guzana', 'atae/huzirina', 'atae/imgurenlil', 'atae/kalhu', 'atae/kunalia', 'atae/mallanate', 'atae/marqasu', 'atae/nineveh', 'atae/samal', 'atae/szibaniba', 'atae/tilbarsip', 'atae/tuszhan', 'babcity', 'blms', 'btmao', 'btto', 'cams', 'cams/akno', 'cams/anzu', 'cams/barutu', 'cams/etana', 'cams/gkab', 'cams/ludlul', 'cams/selbi', 'cams/tlab', 'caspo', 'caspo/akkpm', 'ccpo', 'cmawro', 'cmawro/cmawr1', 'cmawro/cmawr2', 'cmawro/cmawr3', 'cmawro/maqlu', 'contrib', 'contrib/amarna', 'contrib/lambert', 'ctij', 'dccmt', 'doc', 'dsst', 'glass', 'hbtin', 'lacost', 'lovelyrics', 'neo', 'nere', 'nimrud', 'oimea', 'pnao', 'qcat', 'riao', 'ribo', 'ribo/bab7scores', 'ribo/babylon10', 'ribo/babylon2', 'ribo/babylon3', 'ribo/babylon4', 'ribo/babylon5', 'ribo/babylon6', 'ribo/babylon7', 'ribo/babylon8', 'ribo/sources', 'rimanum', 'rinap', 'rinap/rinap1', 'rinap/rinap2', 'rinap/rinap3', 'rinap/rinap4', 'rinap/rinap5', 'rinap/rinap5p1', 'rinap/scores', 'rinap/sources', 'saao', 'saao/aebp', 'saao/knpp', 'saao/saa01', 'saao/saa02', 'saao/saa03', 'saao/saa04', 'saao/saa05', 'saao/saa06', 'saao/saa07', 'saao/saa08', 'saao/saa09', 'saao/saa10', 'saao/saa11', 'saao/saa12', 'saao/saa13', 'saao/saa14', 'saao/saa15', 'saao/saa16', 'saao/saa17', 'saao/saa18', 'saao/saa19', 'saao/saa20', 'saao/saa21', 'saao/saas2', 'suhu', 'tcma', 'tsae', 'xcat']

#FYI, this is the current list of public oracc projects
#projects_list = ['adsd', 'adsd/adart1', 'adsd/adart2', 'adsd/adart3', 'adsd/adart5', 'adsd/adart6','aemw', 'aemw/alalakh/idrimi', 'aemw/amarna', 'aemw/ugarit', 'akklove', 'amgg', 'ario', 'armep', 'arrim', 'asbp', 'asbp/ninmed', 'asbp/rlasb', 'atae', 'atae/assur', 'atae/burmarina', 'atae/durkatlimmu', 'atae/durszarrukin', 'atae/guzana', 'atae/huzirina', 'atae/imgurenlil', 'atae/kalhu', 'atae/kunalia', 'atae/mallanate', 'atae/marqasu', 'atae/nineveh', 'atae/samal', 'atae/szibaniba', 'atae/tilbarsip', 'atae/tuszhan', 'babcity', 'blms', 'btmao', 'btto', 'cams', 'cams/akno', 'cams/anzu', 'cams/barutu', 'cams/etana', 'cams/gkab', 'cams/ludlul', 'cams/selbi', 'cams/tlab', 'caspo', 'caspo/akkpm', 'ccpo', 'cdli', 'ckst', 'cmawro', 'cmawro/cmawr1', 'cmawro/cmawr2', 'cmawro/cmawr3', 'cmawro/maqlu', 'contrib', 'contrib/amarna', 'contrib/lambert', 'ctij', 'dcclt', 'dcclt/ebla', 'dcclt/jena', 'dcclt/nineveh', 'dcclt/signlists', 'dccmt', 'doc', 'dsst', 'ecut', 'eisl', 'epsd2', 'etcsri', 'glass', 'hbtin', 'lacost', 'lovelyrics', 'neo', 'nere', 'nimrud', 'obel', 'obmc', 'obta', 'ogsl', 'oimea', 'pnao', 'qcat', 'riao', 'ribo', 'ribo/bab7scores', 'ribo/babylon10', 'ribo/babylon2', 'ribo/babylon3', 'ribo/babylon4', 'ribo/babylon5', 'ribo/babylon6', 'ribo/babylon7', 'ribo/babylon8', 'ribo/sources', 'rimanum', 'rinap', 'rinap/rinap1', 'rinap/rinap2', 'rinap/rinap3', 'rinap/rinap4', 'rinap/rinap5', 'rinap/rinap5p1', 'rinap/scores', 'rinap/sources', 'saao', 'saao/aebp', 'saao/knpp', 'saao/saa01', 'saao/saa02', 'saao/saa03', 'saao/saa04', 'saao/saa05', 'saao/saa06', 'saao/saa07', 'saao/saa08', 'saao/saa09', 'saao/saa10', 'saao/saa11', 'saao/saa12', 'saao/saa13', 'saao/saa14', 'saao/saa15', 'saao/saa16', 'saao/saa17', 'saao/saa18', 'saao/saa19', 'saao/saa20', 'saao/saa21', 'saao/saas2', 'suhu', 'tcma', 'tsae', 'xcat']


lemm_l = []  # initiate the list that will hold all the lemmatization data of all texts in all requested projects
for project in projects_list_partial:

    try:

        project_json_path = Path(os.path.join(os.getcwd(), f"output_oracc/{project}/corpusjson"))
        print("project_directory_path")
        print(project_json_path)

        files = [x for x in project_json_path.iterdir() if x.is_file()]

        for file in tqdm(files, desc=project):  # iterate over the file names
            filename = file.name
            id_text = project + filename[-13:-5]  # id_text is, for instance, blms/P414332
            try:
                text = open(file, 'r')  # read and decode the json file of one particular text
                data_json = json.load(text)  # make it into a json object (essentially a dictionary)
                lemm_l.extend(parse_text_json(data_json, id_text))  # and send to the parsejson() function
            except:
                errors = sys.exc_info()  # get error information
                print(filename), print(errors[0]), print(errors[1])  # and print it

    except:
        print(sys.exc_info())

print("Constructing pandas data frame")

word_df = pd.DataFrame(lemm_l).fillna('')

# replace NaN (Not a Number) with empty string
print("Replacing punctuation marks")

findreplace = {' ': '-', ',': ''}
word_df = word_df.replace({'gw': findreplace, 'sense': findreplace}, regex=True)
# print(word_df)

# Take only the linguistic norm without word sense or POS
# word_df["lemma"] = word_df["cf"] + '[' + word_df["gw"] + ']' + word_df["pos"]
word_df["lemma"] = word_df["cf"]

word_df.loc[word_df["cf"] == "", 'lemma'] = word_df['form'] + '[NA]NA'
word_df.loc[word_df["pos"] == "n", 'lemma'] = word_df['form'] + '[]NU'
# print(word_df[['norm', 'lemma']])


# Now get the normalized texts

word_df["norm1"] = word_df["norm"]
word_df.loc[word_df["norm1"] == "", 'norm1'] = word_df['form']

texts_norm = word_df.groupby([word_df['id_text']]).agg({
    'norm1': ' '.join,
}).reset_index()

for idx, Q in enumerate(texts_norm["id_text"]):
    savefile = f'{Q[-7:]}.txt'
    with open(f'{output_dir}/{savefile}', 'w', encoding="utf-8") as w:
        texts_norm.iloc[idx].to_csv(w, index=False, header=False)

