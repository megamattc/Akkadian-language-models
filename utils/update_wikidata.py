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



def convert_logogram(lemma: str, lemma_dict: dict) -> str:

    lemma_array = lemma.split(".")
    sign_str = "" #String for the signs to be returned

    for sign in lemma_array:
        sign_low = sign.lower()
        try:
            sign_str = sign_str + lemma_dict[sign_low]
        except:
            print("Failed to find sign for: " + sign +" in " + lemma)
            sign_str = sign_str + "_X_"

    return sign_str


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()

endpoint_url = "https://query.wikidata.org/sparql"

now = datetime.now() # current date and time
date_time = now.strftime("%m_%d_%H_%M")

input_file_name = "FrameLemmasNew.csv"
output_file_name = "FrameLemmasOutput.csv"

log_file_name = "wikidata_lexemes_current_list.csv"


query = """
SELECT
  ?lexeme ?lemma
  ?lexical_category ?lexical_categoryLabel
WITH {
  SELECT ?lexeme ?lemma ?lexical_category WHERE {
    ?lexeme a ontolex:LexicalEntry ;
            dct:language wd:Q35518 ; 
            wikibase:lemma ?lemma .
    FILTER(lang(?lemma)="mis-x-q113819406")
    OPTIONAL {
      ?lexeme wikibase:lexicalCategory ?lexical_category .
    }
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

results = get_results(endpoint_url, query)

wikidata_lexemes = {}

#No go through the list of lexemes from wikidata and make a dictionary based on LID, lexcat, and transcription lemma
#to check against the spreadsheet of forms to be input

for result in results["results"]["bindings"]:
    value = result["lexeme"]["value"]
    lexcat = result["lexical_categoryLabel"]["value"]
    lemma = result["lemma"]["value"]
    lid = value.split("/")[-1]

    #print(result)

    wikidata_lexemes.update({lemma:{"lid":lid,"lexcat":lexcat}})

#print("wikidata_lexemes")
#print(wikidata_lexemes)

#Print out wikidata lexemes to log file
log_file = open(log_file_name,'w',encoding="utf-8")
print(date_time,log_file)
for entry in wikidata_lexemes.keys():
    print(entry + "," + wikidata_lexemes[entry]["lexcat"] + "," + wikidata_lexemes[entry]["lid"],file=log_file)

#Get nuolenna sign list
nuolenna_file = open("nuolenna_sign_list.json",mode='r',encoding='utf-8')
nuolenna_dict = json.load(nuolenna_file)

#logging.basicConfig(level=logging.DEBUG)

wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://www.wikidata.org/wiki/User:Sinleqeunnini)'


input_file = open(input_file_name,'r',encoding="utf-8")
output_file = open(output_file_name,'w',newline='',encoding="utf-8")

#Create header in new file
header_line = input_file.readlines()[0].strip("\n")
header_row = header_line.split(",")
print("Header row:")
print(header_row)
input_file.close()


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
G_stem = "Q117618297"
D_stem = "Q117618680"
Š_stem = "Q117618950"
N_stem = "Q117619108"
Gt_stem = "Q117619765"
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

#Dictionary to convert between spreadsheet lexcat labels and equivalent in QID's
lex_term_dict = {"noun":noun,"adj":adjective,"verb":verb,"pn":propn,"adv":adverb,"num":numeral,"prep":preposition,"det":determiner,
                 "verb phrase":verb_phrase,"subconj":subconj}

#Dictionary to convert between wikidate lexcat labels and spreadsheet lexcat labels
lexcat_dict = {"noun":"noun","adjective":"adj","verb":"verb","proper noun":"pn","adverb":"adv","numeral":"num","preposition":"prep","determiner":"det",
               "verb phrase":"verb phrase","subordinating conjunction":"subconj"}

stem_dict = {"G":G_stem,"D":D_stem,"Š":Š_stem,"N":N_stem,"ŠD":ŠD_stem}

#csv file reader/writer
input_file = open(input_file_name,'r',encoding="utf-8")
reader = csv.DictReader(input_file)
writer = csv.DictWriter(output_file,fieldnames=header_row)

#Write header row of output file
writer.writeheader()



login_instance = wbi_login.Clientlogin(user='Sinleqeunnini', password='zJm3@DXFs#QB$se')

wbi = WikibaseIntegrator(login=login_instance)

counter = 1 #Counter used to slow speed of data upload, avoiding cutoff by Wikidata's spam limit

for row in reader:

    print("Reading row: ")
    print(row)

    #lexemelabel = None
    #lexeme = None

    #Pause loop if modulo number

    if counter % 85 == 0:
        print("Counter is: " + str(counter) + "Sleeping for 180 seconds")
        time.sleep(180)

    if row["non-lexeme"] == "x":
        print("Proposed lexeme is non-lexeme: " + row["term"])
        writer.writerow(row)
        continue

    # If we have an LID, get the wiki lexeme associated with it
    #elif row["LID"] != "":
    #    lexeme = wbi.lexeme.get(entity_id=row["LID"])

    #Do a check if there already is an akkadian lexeme in wikidata that matches the spelling and lexcat of this form
    elif row["LID"] == "" and row["term"] in wikidata_lexemes.keys():
        #print("wikidata_lexemes[row]")
        #print(wikidata_lexemes[row["term"]]["lexcat"])
        if lexcat_dict[wikidata_lexemes[row["term"]]["lexcat"]] == row["lexical_category"]:
            print("Possible duplicate: " + row["term"])
            row["term"] = row["term"] + "_XXXXX"
            writer.writerow(row)
            continue

    #If entry has no LID, make new lexeme


    lexemelabel = row["term"]
    lexcat = row["lexical_category"]
    lexeme = wbi.lexeme.new(lexical_category=lexcat, language=akkadian_language)
    lexeme.lemmas.set(language=akkadian_in_latin_script_misx, value=lexemelabel)

    #Now go though the columns

    if row["Stem"] != "":
        stem = row["Stem"]
        lexeme.claims.add(datatypes.Item(prop_nr=conjugation_class,value=stem_dict[stem]),action_if_exists=ActionIfExists.KEEP)

    #Check if print reference is CDA
    if row["CDA_page"] != "":

        cda_claims = lexeme.claims.add(datatypes.Item(prop_nr=described_by_source, value=cda),action_if_exists=ActionIfExists.KEEP)
        # Add page number qualifier to described_by_source
        for cda_claim in cda_claims:
            #print("cda_claim.mainsnak.datavalue.value.id: ")
            #print(cda_claim.mainsnak.datavalue["value"]["id"])
            #print("cda_claim.mainsnak.property_number: ")
            #print(cda_claim.mainsnak.property_number)
            if cda_claim.mainsnak.property_number == described_by_source and cda_claim.mainsnak.datavalue["value"]["id"] == cda:
                cda_claim.qualifiers.set([datatypes.ExternalID(prop_nr=page_number_prop, value=row["CDA_page"])],action_if_exists=ActionIfExists.KEEP)

                #If there is a CDA numeral for homonymous forms, add that too as qualifier
                #if row["CDA_numeral"] != "":
                #    cda_claim.qualifiers.set([datatypes.ExternalID(prop_nr=page_number_prop, value=row["CDA_page"])])
                #print("CDA claim: ")
                #print(cda_claim)

        # If there is a Roman numeral distinction (I/II/etc...)
        if row["CDA_numeral"] != "":
            citation = row["term"] + " " + row["CDA_numeral"]
            lexeme.claims.add(datatypes.ExternalID(prop_nr=subject_named_as, value=citation),action_if_exists=ActionIfExists.KEEP)


    # Check if print reference is CDA
    if row["CAD_page"] != "":

        cda_claims = lexeme.claims.add(datatypes.Item(prop_nr=described_by_source, value=cad),action_if_exists=ActionIfExists.KEEP)
        # Add page number qualifier to described_by_source.
        # The only way I know how to do that now is to go through all the claims assigned to the lexeme and check if the value matches the one I want
        for cda_claim in cda_claims:
            #print("cda_claim.mainsnak.datavalue.value.id: ")
            #print(cda_claim.mainsnak.datavalue["value"]["id"])
            #print("cda_claim.mainsnak.property_number: ")
            #print(cda_claim.mainsnak.property_number)

            if cda_claim.mainsnak.property_number == described_by_source and cda_claim.mainsnak.datavalue["value"]["id"] == cad:
                cad_array = row["CAD_page"].split(" ") #Split up string by space between volume and page
                cad_vol = cad_array[0].strip()
                cad_page = cad_array[1].strip()

                #Add volume and page qualifiers
                cda_claim.qualifiers.set([datatypes.ExternalID(prop_nr=volume_prop, value=cad_vol)])
                cda_claim.qualifiers.set([datatypes.ExternalID(prop_nr=page_number_prop, value=cad_page)])
                #print("CAD claim: ")
                #print(cda_claim)

        # If there is a Roman numeral distinction (I/II/etc...)
        if row["CDA_numeral"] != "":
            citation = row["term"] + " " + row["CAD_letter"]
            lexeme.claims.add(datatypes.ExternalID(prop_nr=subject_named_as, value=citation),action_if_exists=ActionIfExists.KEEP)

    # Check if print reference is CDA
    if row["RlA_page"] != "":

        cda_claims = lexeme.claims.add(datatypes.Item(prop_nr=described_by_source, value=rla),action_if_exists=ActionIfExists.KEEP)
        # Add page number qualifier to described_by_source.
        # The only way I know how to do that now is to go through all the claims assigned to the lexeme and check if the value matches the one I want
        for cda_claim in cda_claims:
            #print("cda_claim.mainsnak.datavalue.value.id: ")
            #print(cda_claim.mainsnak.datavalue["value"]["id"])
            #print("cda_claim.mainsnak.property_number: ")
            #print(cda_claim.mainsnak.property_number)

            if cda_claim.mainsnak.property_number == described_by_source and cda_claim.mainsnak.datavalue["value"]["id"] == rla:
                #Split up string
                rla_array = row["RlA_page"].split(";")
                rla_vol = rla_array[0].strip()
                rla_page = rla_array[1].strip()

                cda_claim.qualifiers.set([datatypes.ExternalID(prop_nr=volume_prop, value=rla_vol)])
                cda_claim.qualifiers.set([datatypes.ExternalID(prop_nr=page_number_prop, value=rla_page)])
                #print("RlA claim: ")
                #print(cda_claim)

    #Check if there is a Frayne and Stuckey 2021 reference
    if row["FrayneStuckey_page"] != "":

        cda_claims = lexeme.claims.add(datatypes.Item(prop_nr=described_by_source, value=frayne_stuckey_2021),action_if_exists=ActionIfExists.KEEP)
        # Add page number qualifier to described_by_source
        for cda_claim in cda_claims:
            # print("cda_claim.mainsnak.datavalue.value.id: ")
            # print(cda_claim.mainsnak.datavalue["value"]["id"])
            # print("cda_claim.mainsnak.property_number: ")
            # print(cda_claim.mainsnak.property_number)
            if cda_claim.mainsnak.property_number == described_by_source and cda_claim.mainsnak.datavalue["value"]["id"] == frayne_stuckey_2021:
                cda_claim.qualifiers.set([datatypes.ExternalID(prop_nr=page_number_prop, value=row["FrayneStuckey_page"])])
                # print("CDA claim: ")
                # print(cda_claim)

    # If there is an entry in the logogram column
    if row["logogram"] != "":
        logogram_array = row["logogram"].split(";")
        logogram_lemma = logogram_array[0]
        #print("logogram_lemma: " + logogram_lemma)

        # Add first logogram to lemma definition
        logogram_lemma_converted = convert_logogram(logogram_lemma, nuolenna_dict)
        #print("logogram_lemma_converted: " + logogram_lemma_converted)

        lexeme.lemmas.set(language=akkadian_in_cuneiform_script_misx, value=logogram_lemma_converted)
        # If there are remaining logograms, add them to the forms list
        for i in range(0, len(logogram_array)):
            logogram_lemma = logogram_array[i]
            #print("additional logogram_lemma: " + logogram_lemma)
            logogram_lemma_converted = convert_logogram(logogram_lemma, nuolenna_dict)
            f = Form()
            f.representations.set(language=akkadian_in_cuneiform_script_misx, value=logogram_lemma_converted)
            #For all logograms, define them as logographic spellings

            f.claims.add(datatypes.Item(prop_nr=instance_of, value=logographic_spelling),action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
            lexeme.forms.add(f)

    # If there is an entry in the alternate spelling column
    if row["alternate_spelling"] != "":
        alternate_array = row["alternate_spelling"].split(";")

        for i in range(0, len(alternate_array)):
            alternate_lemma = alternate_array[i].strip()
            #print("alternate_spelling: " + alternate_lemma)
            f = Form()
            f.representations.set(language=akkadian_in_latin_script_misx, value=alternate_lemma)
            f.claims.add(datatypes.Item(prop_nr=instance_of, value=alphabetic_spelling),action_if_exists=ActionIfExists.APPEND_OR_REPLACE)
            lexeme.forms.add(f)

    # We need to add the lexemeLabel to the list of forms for consistency's sake
    f = Form()
    f.representations.set(language=akkadian_in_latin_script_misx, value=lexemelabel)
    f.claims.add(datatypes.Item(prop_nr=instance_of, value=alphabetic_spelling))
    lexeme.forms.add(f)

    # If there is an entry in the assyrian dialect column
    if row["assyrian_dialect"] != "":
        assyrian_array = row["assyrian_dialect"].split(";")

        for i in range(0, len(assyrian_array)):
            assyrian_lemma = assyrian_array[i].strip()
            #print("assyrian_dialect: " + assyrian_lemma)
            f = Form()
            f.representations.set(language=akkadian_in_latin_script_misx, value=assyrian_lemma)
            f.claims.add(datatypes.Item(prop_nr=dialect_variant,value=assyrian_dialect))
            lexeme.forms.add(f)

    #If LID of Sumerian loan is given in table, add it (sometimes table just has 'yes' indicating the Akkadian form is a Sumerian load,
    #but I haven't found the Sumerian lexeme in wikidata yet.
    if "L" in row["sumerian_loanword"]:
        print("Sumerian loanword ID:")
        print(row["sumerian_loanword"])
        lexeme.claims.add(datatypes.Lexeme(prop_nr=derived_from_lexeme_prop,value=row["sumerian_loanword"]),action_if_exists=ActionIfExists.KEEP)






    #Now handle the senses
    senses = row["sense"]
    sense_array = senses.split(";")

    for sense in sense_array:
        if sense != "":
            cursense = Sense()
            cursense.glosses.set(language="en", value=sense)
            lexeme.senses.add(cursense,action_if_exists=ActionIfExists.APPEND_OR_REPLACE)

    print("lexeme: ")
    print(lexeme)

    #Actually write new lexeme entry to wikidata
    result = lexeme.write()
    new_lid = result.id

    #Print updated row of csv file to ouput file
    row["LID"] = new_lid
    writer.writerow(row)

    #Increment counter if we created new ID
    counter = counter + 1

