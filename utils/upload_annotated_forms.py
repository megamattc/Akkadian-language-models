from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator import wbi_login, datatypes, WikibaseIntegrator
from wikibaseintegrator.models import Reference, References, Form, Sense
from wikibaseintegrator.models.qualifiers import Qualifiers
from wikibaseintegrator.wbi_enums import ActionIfExists
import logging
import csv
import json
import requests
import sys,time
from SPARQLWrapper import SPARQLWrapper, JSON
from datetime import datetime
import re



def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


#Function to convert Oracc label to dict of strings usable by wikidata
def convert_label(label : str) -> dict:

    line_num = ""
    surface = ""
    column = ""

    # If we can't identify line number, leave it as empty string
    if re.search(r'\d+[\']{0,1}',label):
        line_num = re.findall(r'\d+[\']{0,1}',label)[0]

    if "r.e." in label:
        surface = "Q117828432"
    elif "l.e." in label:
        surface = "Q117828447"
    elif "t.e." in label:
        surface = "Q117828457"
    elif "b.e." in label:
        surface = "Q117828465"
    elif "r " in label:
        surface = "Q117828332"
    elif "o " in label:
        surface = "Q117828351"
    elif re.search(r'[v|i|x]{1,}',label):
        column = re.findall(r'[v|i|x]{1,}',label)[0]
   
   

    return {"surface":surface, "column":column, "line_num":line_num}

#Function to convert pnum to url pointing to cdli page if it is Pnum, just a filename of form Qnum.json if it is Qnum
#Return value is dict {"url":url,"filename_archive":filename_archive}
def convert_pnum(pnum : str) -> dict:
    url_dict = {"url":"","filename_archive":""}
    url = ""
    filename_archive = ""
    #If we have a Pnum and not Qnum, we know it has a page in cdli
    if re.search(r'P[0-9]{6}',pnum):
        pnum2 = re.findall(r'[0-9]{6}',pnum)[0]
        url = "https://cdli.mpiwg-berlin.mpg.de/artifacts/" + pnum2
        url_dict["url"] = url

    elif re.search(r'Q[0-9]{6}',pnum):
        filename_archive = pnum + ".json"
        url_dict["filename_archive"] = filename_archive

    return url_dict


#Function for sifting through the variety of xpos labels in the data and dealing only with a few
def convert_xpos(label : str) -> str:
    if label in ["Quotative","REL","NEG","XP","QP"]:
        return gram_dict[label]
    else:
        return ""

#Similar for upos, save with reference to lexcat_dict
def convert_upos(label : str) -> str:
    if label in lexcat_dict.keys():
        return lexcat_dict[label]
    else:
        return ""

#Used to convert morphological analysis as UD string into a list of strings reflecting wikidata grammatical categories
def convert_morphology(upos : str, xpos : str, morph : str) -> list[str]:

    feature_list = []
    morph_array = morph.split("|")
    #print("morph_array")
    #print(morph_array)
    #print("upos")
    #print(upos)
    #For nouns, adverbs, adjectives, pronouns, particles, use one dict
    if upos in [noun,adverb,adjective,pronoun,particle,propn]:
        for pair in morph_array:
            if pair in ud_nom_adj_adv_dict.keys():
                #print("In convert_morphology, adding pair:")
                #print(pair)
                #print("Value")
                #print(ud_nom_adj_adv_dict[pair])
                feature_list.append(ud_nom_adj_adv_dict[pair])

    #If verb is non-stative
    if upos == verb and not ("VerbForm=Stat" in morph_array):
        for pair in morph_array:
            if pair in ud_verb_dict.keys():
                #print("In convert_morphology, adding pair:")
                #print(pair)
                #print("Value")
                #print(ud_verb_dict[pair])
                feature_list.append(ud_verb_dict[pair])

    # If verb is stative
    if upos == verb and "VerbForm=Stat" in morph_array:
        for pair in morph_array:
            if pair in ud_stat_dict.keys():
                #print("In convert_morphology, adding pair:")
                #print(pair)
                feature_list.append(ud_stat_dict[pair])

    #Some other random combinations

    if upos == pronoun and xpos == rel_pronoun:
        feature_list.append(rel_pronoun)

    if upos == particle and xpos == negation:
        feature_list.append(negation)

    if upos == particle and xpos == quotative:
        feature_list.append(quotative)

    #print("feature_list")
    #print(feature_list)
    return feature_list


#Used to check if a lexeme has a given form with morphological analysis and citation features (col, lin num, surface, filename, url)
def find_form(lexeme,form : str, upos: str, xpos: str, morph : str,colu:str, lin_num:str,sur:str,fi:str,ur:str) -> dict:

    found = False
    for form_dic in lexeme.forms.get_json():
        #print("lexeme.forms.get_json()")
        print(lexeme.forms.get_json())
        if akkadian_in_latin_script_misx in form_dic["representations"]:
            form_value = form_dic["representations"][akkadian_in_latin_script_misx]["value"]
            grammatical_features = form_dic["grammaticalFeatures"]
            print("form_value: " + form_value)
            print("form: " + form)
            print("Set from converting ud feature string in current row: ")
            print(set(convert_morphology(upos, xpos, morph)))
            print("Set from grammatical_features of form under given lemma: ")
            print(set(grammatical_features))
            if form == form_value and set(convert_morphology(upos, xpos, morph)) == set(grammatical_features):
                c = "" #Column
                l = "" #Line num
                s = "" #Surface
                f = "" #Filename
                u = "" #Ext_url
                claims_dict = form_dic["claims"]

                if column in claims_dict.keys():
                    claim_dict = claims_dict[column][0]
                    c = claim_dict["mainsnak"]["datavalue"]["value"]
                if line_num in claims_dict.keys():
                    claim_dict = claims_dict[line_num][0]
                    l = claim_dict["mainsnak"]["datavalue"]["value"]
                if filename_archive_prop in claims_dict.keys():
                    claim_dict = claims_dict[filename_archive_prop][0]
                    f = claim_dict["mainsnak"]["datavalue"]["value"]
                if ext_url in claims_dict.keys():
                    claim_dict = claims_dict[ext_url][0]
                    u = claim_dict["mainsnak"]["datavalue"]["value"]
                if hassurface in claims_dict.keys():
                    claim_dict = claims_dict[hassurface][0]
                    print("claims_dict[hassurface]")
                    print(claims_dict[hassurface])
                    print("claim_dict")
                    print(claim_dict)
                    s = claim_dict["mainsnak"]["datavalue"]["value"]["id"]

                if [c,l,f,u,s] == [colu,lin_num,fi,ur,sur]:
                    print("In find_form, found match between existing form and proposed form")
                    found = True

                    return form_dic

                    #break


    #return found
    return


ud_nom_adj_adv_dict = {
    "Gender=Masc":"Q499327",
    "Gender=Fem":"Q1775415",
    "Number=Sing":"Q110786",
    "Number=Plur":"Q146786",
    "Number=Dual":"Q110022",
    "Person=1":"Q21714344",
    "Person=2":"Q51929049",
    "Person=3":"Q51929074",
    "Case=Nom":"Q131105",
    "Case=Gen":"Q146233",
    "Case=Acc":"Q146078",
    "Case=Loc":"Q202142",
    "Case=Ter":"Q74701",
    "NounBase=Free":"Q117777474",
    "NounBase=Bound":"Q1641446",
    "PossSuffGen=Masc":"Q69761633",
    "PossSuffGen=Fem":"Q69761768",
    "PossSuffGen=Com":"Q117796237",
    "PossSuffPer=1":"Q71470598",
    "PossSuffPer=2":"Q71470837",
    "PossSuffPer=3":"Q71470909",
    "PossSuffNum=Plur":"Q78191289",
    "PossSffNum=Sing":"Q78191294",
    "Focus=Yes":"Q117824243",
    "Question=Yes":"Q117824263",
    "VerbForm=Inf":"Q179230"
}

ud_verb_dict = {
    "Gender=Masc":"Q117795175",
    "Gender=Fem":"Q117795184",
    "Gender=Com":"Q117795196",
    "Number=Sing":"Q117795205",
    "Number=Plur":"Q117795217",
    "Number=Dual":"Q117795221",
    "Person=1":"Q117795114",
    "Person=2":"Q117795140",
    "Person=3":"Q117795156",
    "VerbSuffGen=Masc":"Q117797702",
    "VerbSuffGen=Fem":"Q117797703",
    "VerbSuffGen=Com":"Q117797704",
    "VerbSuffPer=1":"Q117797699",
    "VerbSuffPer=2":"Q117797700",
    "VerbSuffPer=3":"Q117797701",
    "VerbSuffNum=Sing":"Q117797705",
    "VerbSuffNum=Plur":"Q117797706",
    "VerbSuffNum=Dual":"Q117797707",
    "Ventive=Yes":"Q2513026",
    "Question=Yes":"Q117824263",
    "Focus=Yes":"Q117824243",
    "Tense=Pres":"Q192613",
    "Tense=Past":"Q1994301",
    "Tense=Perf":"Q625420",
    "VerbForm=Fin":"Q2166170",
    "Mood=Ind":"Q682111",
    "Mood=Imp":"Q22716",
    "Mood=Vet":"Q22716",
    "Mood=Prec":"Q117824584",
    "Subordinative=Yes":"Q117824471",
    "SubSuff=Yes":"Q117824501"

}

ud_stat_dict = {
    "Gender=Masc":"Q117797711",
    "Gender=Fem":"Q117797712",
    "Gender=Com":"Q117797713",
    "Number=Sing":"Q117797714",
    "Number=Plur":"Q117797715",
    "Number=Dual":"Q117797716",
    "Person=1":"Q117797708",
    "Person=2":"Q117797709",
    "Person=3":"Q117797710",
    "Subordinative=Yes":"Q117824471",
    "SubSuff=Yes":"Q117824501",
    "Ventive=Yes":"Q2513026",
    "Question=Yes":"Q117824263",
    "Focus=Yes":"Q117824243",
}




query = """
SELECT DISTINCT
  ?lexeme ?lemma
  ?lexical_category ?lexical_categoryLabel
WITH {
  SELECT ?lexeme ?lemma ?lexical_category WHERE {
    ?lexeme a ontolex:LexicalEntry ;
            dct:language wd:Q35518 ; 
            wikibase:lemma ?lemma ;
            wikibase:lexicalCategory ?lexical_category .
            
    
    FILTER(lang(?lemma)="mis-x-q113819406")
    
  }
  LIMIT 10000
} AS %results
WHERE {
  INCLUDE %results
  OPTIONAL {        
    ?lexical_category rdfs:label ?lexical_categoryLabel .
    FILTER (LANG(?lexical_categoryLabel) = "en")
  }
  # SERVICE does not work!?
  # SERVICE wikibase:label { bd:serviceParam wikibase:language "en" . }
}
  
  """


endpoint_url = "https://query.wikidata.org/sparql"

results = get_results(endpoint_url, query)

wikidata_lexemes = {}

#No go through the list of lexemes from wikidata and make a dictionary based on LID, lexcat, and transcription lemma
#to check against the spreadsheet of forms to be input

for result in results["results"]["bindings"]:
    #print("Result:")
    #print(result)
    value = result["lexeme"]["value"] #URL + LID of lexeme
    lexcat = result["lexical_category"]["value"] #URL + QID of lexeme
    lemma = result["lemma"]["value"] #Lemma (as normalization)

    lid = value.split("/")[-1]


    if lemma in wikidata_lexemes.keys():

        wikidata_lexemes[lemma].append((lid, lexcat, value)) #Format of 3-tuple (lexcat = UPOS, value = lemma)

    else:
        wikidata_lexemes[lemma] = []
        wikidata_lexemes[lemma].append((lid, lexcat, value))




    #print(result)

    #wikidata_lexemes.update({lemma:{"lid":lid,"lexcat":lexcat,"root":root}})

print("wikidata_lexemes")
print(wikidata_lexemes)




#lexcat QID's
verb="Q24905"
verb_phrase = "Q1778442"
noun="Q1084"
adjective="Q34698"
propn="Q147276"
adverb = "Q380057"
numeral = "Q63116"
preposition = "Q4833830"
determiner = "Q576271"
subconj = "Q11655558" #Subordinating conjunction
conj = "Q36484"
particle = "Q184943"
pronoun = "Q36224"
rel_pronoun = "Q1050744"
negation = "Q1478451"
quotative = "Q117824666"

#Other QID's
akkadian_language= "Q35518"
sumerian_language = "Q36790"
akkadian_in_latin_script_misx = "mis-x-Q113819406"
akkadian_in_cuneiform_script_misx = "mis-x-Q35518"
akkadian_in_latin_script = "Q113819406"
akkadian_in_cuneiform_script = "Q35518"
described_by_source = "P1343"
cda = "Q115610663" #CDA
cad ="Q1071825" #CAD
rla = "Q1246462" #Reallexicon
frayne_stuckey_2021 = "Q117435060" #Handbook of Gods and Goddesses
assyrian_dialect = "Q117430111"
logogram = "Q138659"
syllabogram = "Q2373910"
syllabic_spelling = "Q117439192"
logographic_spelling = "Q117439223"
alphabetic_spelling = "Q117451320"
paradigm = "Q1428334"
G_stem = "Q117618297"
D_stem = "Q117618680"
Š_stem = "Q117618950"
N_stem = "Q117619108"
Gt_stem = "Q117619765"
Dt_stem = "Q117620012"
Nt_stem = "Q117620764"
Št_stem = "Q117829516" #This ignores St-lexical/passive distinction
Gtn_stem = "Q117620946"
Dtn_stem = "Q117621064"
Štn_stem = "Q117621278"
Ntn_stem = "Q117621403"
ŠD_stem = "Q117621515"


#P-values
alternative_spelling = "P8530"
dialect_variant = "P7481" #dialect, graphic or phonetic variety that this lexeme, form or sense is used in
page_number_prop = "P304"
volume_prop = "P478"
derived_from_lexeme_prop = "P5191"
instance_of = "P31"
conjugation_class = "P5186"
subject_named_as = "P1810"
has_root = "P5920"
particle = "Q184943"

line_num = "P7421"
stated_in = "P249"
hassurface = "P10614"
column = "P3903"
ext_url = "P854"
filename_archive_prop = "P7793"

#Links labels to QID's of grammatical features in wikidatabase (also found in gram_dict.txt)
gram_dict = {

"Masculine subject":"Q117795175",
"Feminine subject":"Q117795184",
"Common subject":"Q117795196",
"Singular subject":"Q117795205",
"Plural subject":"Q117795217",
"Dual subject":"Q117795221",
"First person subject":"Q117795114",
"Second person subject":"Q117795140",
"Third person subject":"Q117795156",
"First person direct object":"Q117797681",
"Second person direct object":"Q117797682",
"Third person direct object":"Q117797683",
"Masculine direct object":"Q117797684",
"Feminine direct object":"Q117797685",
"Common direct object":"Q117797686",
"Singular direct object":"Q117797687",
"Plural direct object":"Q117797688",
"Dual direct object":"Q117797689",
"First person indirect object":"Q117797690",
"Second person indirect object":"Q117797691",
"Third person indirect object":"Q117797692",
"Masculine indirect object":"Q117797693",
"Feminine indirect object":"Q117797694",
"Common indirect object":"Q117797695",
"Singular indirect object":"Q117797696",
"Plural indirect object":"Q117797697",
"Dual indirect object":"Q117797698",
"First person direct/indirect object":"Q117797699",
"Second person direct/indirect object":"Q117797700",
"Third person direct/indirect object":"Q117797701",
"Masculine direct/indirect object":"Q117797702",
"Feminine direct/indirect object":"Q117797703",
"Common direct/indirect object":"Q117797704",
"Singular direct/indirect object":"Q117797705",
"Plural direct/indirect object":"Q117797706",
"Dual direct/indirect object":"Q117797707",
"First person predicative":"Q117797708",
"Second person predicative":"Q117797709",
"Third person predicative":"Q117797710",
"Masculine predicative":"Q117797711",
"Feminine predicative":"Q117797712",
"Common predicative":"Q117797713",
"Singular predicative":"Q117797714",
"Plural predicative":"Q117797715",
"Dual predicative":"Q117797716",
"Accusative":"Q146078",
"Bound state/construct state":"Q1641446",
"Common":"Q1305037",
"Dual":"Q110022",
"Feminine":"Q1775415",
"First person":"Q21714344",
"First person plural":"Q51929290",
"First person singular":"Q51929218",
"First person singular feminine":"Q65091963",
"First person singular masculine":"Q65091957",
"First person singular possessive":"Q56703567",
"Genitive":"Q146233",
"Locative":"Q202142",
"Masculine":"Q499327",
"Nominative":"Q131105",
"Plural":"Q146786",
"Question":"Q117824263",
"Second person":"Q51929049",
"Masculine possessive":"Q69761633",
"Feminine possessive":"Q69761768",
"Common possessive":"Q117796237",
"Plural possessive":"Q78191289",
"mā particle":"Q117824243",
"First person possessive":"Q71470598",
"Second person possessive":"Q71470837",
"Third person possessive":"Q71470909",
"Second person plural":"Q51929403",
"Second person plural feminine":"Q55098010",
"Second person plural masculine":"Q55097931",
"Second person singular":"Q51929369",
"Second-person singular masculine":"Q55097773",
"Singular":"Q110786",
"Terminative":"Q747019",
"Third person":"Q51929074",
"Third person plural feminine":"Q52433019",
"Third person plural masculine":"Q52432983",
"Third person singular":"Q51929447",
"Third person singular feminine":"Q52431970",
"Third person singular masculine":"Q52431955",
"Unbound state":"Q117777474",
"Ventive":"Q2513026",
"Present tense":"Q192613",
"Past tense":"Q1994301",
"Perfect tense":"Q625420",
"Finite verb":"Q2166170",
"Indicative mood":"Q682111",
"Vetitive mood":"Q22716",
"Infinitive":"Q179230",
"Subordinative":"Q117824471",
"Subordinate -ni":"Q117824501",
"Precative":"Q117824584",
"Quotative":"Q117824666",
"NEG":"Q1478451",
"REL":"Q1050744",
"XP":"Q956030",
"QP":"Q54310231"
}

#Dictionary to convert between spreadsheet lexcat labels and equivalent in QID's
lexcat_dict = {"NOUN":noun,"ADJ":adjective,"VERB":verb,"PROPN":propn,
               "ADV":adverb,"NUM":numeral,"ADP":preposition,"PRP":preposition,
               "DET":determiner,"SCONJ":subconj,"CCONJ":conj,"CONJ":conj,
               "PART":particle,"PRON":pronoun}

stem_dict = {"G":G_stem,"D":D_stem,"Š":Š_stem,"N":N_stem,"ŠD":ŠD_stem,
             "Gt":Gt_stem,"Dt":Dt_stem,"Št":Št_stem,"Nt":Nt_stem,
             "Gtn":Gtn_stem,"Dtn":Dtn_stem,"Štn":Štn_stem,"Ntn":Ntn_stem,
             }


conllu_data_file_name = "conllu_data.tsv"

header_row = ["FID","LID","problem","pnum","ppos","label","index","form","lemma","UPOS","XPOS","morphology","head_index","syn_dep","8","9"]

conllu_data_file = open(conllu_data_file_name,'r',encoding='utf-8')
reader = csv.DictReader(conllu_data_file,delimiter="\t")

output_file_name = "conllu_data_ouput.tsv"

header_row_output = ["FID","LID","problem","pnum","ppos","label","index","form","lemma","UPOS","XPOS","morphology","head_index","syn_dep","8","9"]

output_file = open(output_file_name,'w',newline='',encoding="utf-8")
writer = csv.DictWriter(output_file, delimiter="\t",fieldnames=header_row_output)

#Write header of output file
writer.writeheader()

log_file_name = "upload_annotated_forms_result.csv"

#logging.basicConfig(level=logging.DEBUG)

wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://www.wikidata.org/wiki/User:Sinleqeunnini)'

login_instance = wbi_login.Clientlogin(user='Sinleqeunnini', password='zJm3@DXFs#QB$se')

wbi = WikibaseIntegrator(login=login_instance)



counter = 1  # Counter used to slow speed of data upload, avoiding cutoff by Wikidata's spam limit

for row in reader:

    # Use this when testing to limit number of rows processed
    if counter > 500:
        break

    print("Reading row: ")
    print(row)

    pnum_dict = convert_pnum(row["pnum"])
    label = convert_label(row["label"]) #A dict of three strings {surface, column, line}, which may be empty strings
    index = row["index"]
    form = row["form"]
    lemma = row["lemma"]
    upos = convert_upos(row["UPOS"]) #convert row label to QID for upos
    xpos = convert_xpos(row["XPOS"]) # "" ""
    #print("upos")
    #print(upos)
    #print("xpos")
    #print(xpos)
    #print("row[morphology]")
    #print(row["morphology"])
    morph = convert_morphology(upos,xpos,row["morphology"]) #convert ud feature string to list of QID's
    #print("morph")
    #print(morph)
    verb_stem = "" #Verb stem as QID
    verb_stem_str = "" #Verb stem as string

    #String variables for the citation info
    colu = label["column"] #Column
    lin_num = label["line_num"]
    sur = label["surface"] #Surface
    ur = pnum_dict["url"] #CDLI url
    fi = pnum_dict["filename_archive"] #Filename

    fid = "" #String for the LID ('FID') of future form to be created

    if row["problem"] == "x":
        print("Row is marked as problem. Skipping.")
        counter = counter + 1
        writer.writerow(row)
        continue


    #Find verbstem if it is present in morph
    if re.search(r'(?<=VerbStem=)([A-Za-zŠ]{1,3})',row["morphology"]):
        print("Getting verb stem:")
        print(re.findall(r'(?<=VerbStem=)([A-Za-zŠ]+)\|',row["morphology"]))
        verb_stem_str = re.findall(r'(?<=VerbStem=)([A-Za-zŠ]{1,3})',row["morphology"])[0]
        if verb_stem_str in stem_dict.keys():
            verb_stem = stem_dict[verb_stem_str]


    #temporarily avoid uploading verb forms
    if upos == verb and verb_stem != G_stem:
        print("Row is verb not of G-stem. Marking as problem and skipping.")
        row["problem"] = "x"
        writer.writerow(row)
        counter = counter + 1
        continue



    #If the upos is not  recognized category (e.g. X), skip entry
    if upos == "":
        print("Row does not have recognizable UPOS. Marking as problem and skipping.")
        row["problem"] = "x"
        writer.writerow(row)
        counter = counter + 1

        continue



    lexeme = wbi.lexeme.new(lexical_category=upos, language=akkadian_language) #Set up lexeme now




    # Pause loop if modulo number

    if counter % 20000000 == 0:
        print("Counter is: " + str(counter) + "Sleeping for 65 seconds")
        time.sleep(65)

    if row["FID"] != "":
        print("FID already exists for this item. Skipping.")
        counter = counter + 1
        writer.writerow(row)
        continue



    # If we have an LID, get the wiki lexeme associated with it
    elif row["LID"] != "":
        print("LID for this row already exists: " + row["LID"])
        lexeme = wbi.lexeme.get(entity_id=row["LID"])

        print("Checking for matching forms")
        # If we don't already have a form under lexeme matching phonology and morphological analysis
        if not find_form(lexeme, form, upos, xpos, row["morphology"],colu,lin_num,sur,fi,ur):
            print("No matching form found. Will add new one")
            f = Form()
            f.representations.set(language=akkadian_in_latin_script_misx, value=form)
            f.claims.add(datatypes.Item(prop_nr=instance_of, value=alphabetic_spelling))
            if pnum_dict["url"] != "":
                f.claims.add(datatypes.ExternalID(prop_nr=ext_url, value=pnum_dict["url"]))
            if pnum_dict["filename_archive"] != "":
                f.claims.add(datatypes.ExternalID(prop_nr=filename_archive_prop, value=pnum_dict["filename_archive"]))
            if label["surface"] != "":
                f.claims.add(datatypes.Item(prop_nr=hassurface, value=label["surface"]))
            if label["column"] != "":
                f.claims.add(datatypes.ExternalID(prop_nr=column, value=label["column"]))
            if label["line_num"] != "":
                f.claims.add(datatypes.ExternalID(prop_nr=line_num, value=label["line_num"]))

            print(morph)
            # If list of QID's for morphology is not empty
            if morph != []:
                print("Adding grammatical features: ")

                f.grammatical_features = list(morph)

            print("Adding new form to preexisting lexeme ")
            #print(f)
            fs = lexeme.forms.add(f)
            forms_dict = fs.forms
            forms_dict_inv = {k: v for v, k in forms_dict.items()}
            fid = forms_dict_inv[f]
            print("In loop fid")
            print(fid)

            #row["FID"] = fid

        else:
            print("A preexisting matching form was found. Skipping form.")


    # Do a check if there already is an akkadian lexeme in wikidata that matches the spelling and lexcat of this form
    #There is an annoying bug in the data whereby normalized forms with a capital letter have their lemmas in lower case,
    #e.g. form: Aššur, lemma: aššur. B/c of this, we need to check two cases
    elif row["LID"] == "" and (lemma in wikidata_lexemes.keys() or lemma.capitalize() in wikidata_lexemes.keys()):


        #Capitalize value of lemma variable if needed
        if lemma.capitalize() in wikidata_lexemes.keys() and not (lemma in wikidata_lexemes.keys()):
            lemma = lemma.capitalize()

        print("List of lexemes with matching lemma:")
        print(wikidata_lexemes[lemma])
        #print(wikidata_lexemes[lemma]["lexcat"])
        # Get list of forms with lexcat labels matching that of our lemma
        common_tuples = [t for t in wikidata_lexemes[lemma] if upos in t[1]]
        print("common_tuples")
        print(common_tuples)


        # If number of matches is > 1, skip this row b/c we need to decide based on sense how to classify the form
        if len(common_tuples) > 1:

            print("Found " + str(len(common_tuples)) + " possible lexemes for " + lemma + ". Marking as problem")
            row["problem"] = "x"
            writer.writerow(row)

            counter = counter + 1 #Still add counter

            continue

        # Otherwise, if there is exactly one match in lexcat, we add the form under the matching lemma
        elif len(common_tuples) == 1:
            print("Exactly one lemma matching lexcat" )

            lid = common_tuples[0][0]

            lexeme = wbi.lexeme.get(entity_id=lid)

            print("LID of candidate: " + lid)
            # Check if upos (a QID) is in the string given by uri of lexeme.lexical_category
            if upos in lexeme.lexical_category:
                print("Match between upos and lexeme.lexical_category")
                # If we don't already have a form under lexeme matching phonology and morphological analysis
                if not find_form(lexeme, form, upos, xpos, row["morphology"],colu,lin_num,sur,fi,ur):
                    f = Form()
                    f.representations.set(language=akkadian_in_latin_script_misx, value=form)
                    f.claims.add(datatypes.Item(prop_nr=instance_of, value=alphabetic_spelling))
                    if pnum_dict["url"] != "":
                        f.claims.add(datatypes.ExternalID(prop_nr=ext_url, value=pnum_dict["url"]))
                    if pnum_dict["filename_archive"] != "":
                        f.claims.add(
                            datatypes.ExternalID(prop_nr=filename_archive_prop, value=pnum_dict["filename_archive"]))
                    if label["surface"] != "":
                        f.claims.add(datatypes.Item(prop_nr=hassurface, value=label["surface"]))
                    if label["column"] != "":
                        f.claims.add(datatypes.ExternalID(prop_nr=column, value=label["column"]))
                    if label["line_num"] != "":
                        f.claims.add(datatypes.ExternalID(prop_nr=line_num, value=label["line_num"]))

                    # If list of QID's for morphology is not empty
                    print(morph)
                    if morph != []:
                        print("Adding grammatical features.")

                        f.grammatical_features = list(morph)

                    print("Adding new form to existing lemma")
                    #lexeme.forms.add(f)

                    fs = lexeme.forms.add(f)
                    forms_dict = fs.forms
                    forms_dict_inv = {k:v for v,k in forms_dict.items()}
                    fid = forms_dict_inv[f]
                    print("In loop fid")
                    print(fid)



                    #fid = f.id
                    #row["FID"] = fid



        #Else there is no lexcat match and we must create a new lexeme to host the form
        else:

            print("Lemma is in wikidata, but no match with lexemes on basis of lexcat. Making new lexeme.")
            lexeme.lemmas.set(language=akkadian_in_latin_script_misx, value=lemma)

            # Add verb stem
            if verb_stem != "":
                lexeme.claims.add(datatypes.Item(prop_nr=conjugation_class, value=verb_stem),
                                  action_if_exists=ActionIfExists.KEEP)

            f = Form()

            f.representations.set(language=akkadian_in_latin_script_misx, value=form)
            f.claims.add(datatypes.Item(prop_nr=instance_of, value=alphabetic_spelling))
            if pnum_dict["url"] != "":
                f.claims.add(datatypes.ExternalID(prop_nr=ext_url, value=pnum_dict["url"]))
            if pnum_dict["filename_archive"] != "":
                f.claims.add(datatypes.ExternalID(prop_nr=filename_archive_prop, value=pnum_dict["filename_archive"]))
            if label["surface"] != "":
                f.claims.add(datatypes.Item(prop_nr=hassurface, value=label["surface"]))
            if label["column"] != "":
                f.claims.add(datatypes.ExternalID(prop_nr=column, value=label["column"]))
            if label["line_num"] != "":
                f.claims.add(datatypes.ExternalID(prop_nr=line_num, value=label["line_num"]))

            # If list of QID's for morphology is not empty
            print(morph)
            if morph != []:
                print("Adding grammatical features.")

                f.grammatical_features = list(morph)

            print("Adding new form to lexeme")
            #lexeme.forms.add(f)

            fs = lexeme.forms.add(f)
            forms_dict = fs.forms
            forms_dict_inv = {k: v for v, k in forms_dict.items()}
            fid = forms_dict_inv[f]
            print("In loop fid")
            print(fid)

            #fid = f.id
            #row["FID"] = fid


    #Otherwise lemma is not already in wikidata and we must also make a new lexeme
    else:

        print("Lemma is not in wikidata. Making new lexeme.")
        lexeme.lemmas.set(language=akkadian_in_latin_script_misx, value=lemma)

        #Add verb stem
        if verb_stem != "":

            lexeme.claims.add(datatypes.Item(prop_nr=conjugation_class, value=verb_stem),
                              action_if_exists=ActionIfExists.KEEP)

        f = Form()
        f.representations.set(language=akkadian_in_latin_script_misx, value=form)
        f.claims.add(datatypes.Item(prop_nr=instance_of, value=alphabetic_spelling))
        if pnum_dict["url"] != "":
            f.claims.add(datatypes.ExternalID(prop_nr=ext_url, value=pnum_dict["url"]))
        if pnum_dict["filename_archive"] != "":
            f.claims.add(datatypes.ExternalID(prop_nr=filename_archive_prop, value=pnum_dict["filename_archive"]))
        if label["surface"] != "":
            f.claims.add(datatypes.Item(prop_nr=hassurface, value=label["surface"]))
        if label["column"] != "":
            f.claims.add(datatypes.ExternalID(prop_nr=column, value=label["column"]))
        if label["line_num"] != "":
            f.claims.add(datatypes.ExternalID(prop_nr=line_num, value=label["line_num"]))

        # If list of QID's for morphology is not empty
        print(morph)
        if morph != []:
            print("Adding grammatical features.")

            f.grammatical_features = list(morph)

        print("Adding new form to lexeme")
        #lexeme.forms.add(f)

        #fid = f.id
        #row["FID"] = fid

        fs = lexeme.forms.add(f)
        forms_dict = fs.forms
        forms_dict_inv = {k: v for v, k in forms_dict.items()}
        fid = forms_dict_inv[f]
        print("In loop fid")
        print(fid)


    #print("lexeme: ")
    #print(lexeme)
    print("Writing lexeme to wikidata")
    # Actually write new lexeme entry to wikidata
    result = lexeme.write()
    new_lid = result.id

    ff = find_form(result,form,upos,xpos,row["morphology"],colu,lin_num,sur,fi,ur)

    if ff:
        fid = ff["id"]

    #If a new form was created, get its FID/LID
    print("fid")
    print(fid)
    row["FID"] = fid

    # Print updated row of csv file to ouput file
    row["LID"] = new_lid
    writer.writerow(row)

    # Increment counter if we created new ID
    counter = counter + 1






