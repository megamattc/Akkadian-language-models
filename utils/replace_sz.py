from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator import wbi_login, datatypes, WikibaseIntegrator
from wikibaseintegrator.wbi_enums import ActionIfExists
from wikibaseintegrator.models import Reference, References, Form, Sense
from wikibaseintegrator.models.qualifiers import Qualifiers
import logging
import csv
import json
import requests
import sys
from SPARQLWrapper import SPARQLWrapper, JSON

akkadian_in_latin_script = "Q113819406"
akkadian_in_latin_script_misx = "mis-x-Q113819406"

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

query = """
# tool: ordia
# title: List of lexemes for a language
SELECT
  ?lexeme ?lexemeLabel
  ?lexical_category ?lexical_categoryLabel
WITH {
  SELECT ?lexeme ?lexemeLabel ?lexical_category WHERE {
    ?lexeme a ontolex:LexicalEntry ;
            dct:language wd:Q35518 ; 
            wikibase:lemma ?lexemeLabel .
    FILTER (LANG(?lexemeLabel) = "mis-x-q113819406")
    FILTER contains(?lexemeLabel, 'sz')
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



login_instance = wbi_login.Clientlogin(user='Sinleqeunnini', password='zJm3@DXFs#QB$se')

wbi = WikibaseIntegrator(login=login_instance)

#No go through the list of lexemes from wikidata and make a dictionary based on LID, lexcat, and transcription lemma
#to check against the spreadsheet of forms to be input

for result in results["results"]["bindings"]:
    value = result["lexeme"]["value"]
    lid = value.split("/")[-1]
    lexeme = wbi.lexeme.get(lid)
    lemma = result["lexemeLabel"]["value"]
    lemma_replace = lemma.replace("sz","š")
    print("Replaced " + lemma + " with " + lemma_replace)
    lexeme.lemmas.set(language=akkadian_in_latin_script_misx, value=lemma_replace,action_if_exists=ActionIfExists.REPLACE_ALL)
    #print(lexeme.lemmas)

    output = lexeme.write()
    print(output)
    #wikidata_lexemes.update({lemma:{"lid":lid,"lexcat":lexcat}})
