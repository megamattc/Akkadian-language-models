# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

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


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


results = get_results(endpoint_url, query)

wikidata_lexemes = {}

for result in results["results"]["bindings"]:
    value = result["lexeme"]["value"]
    lexcat = result["lexical_categoryLabel"]["value"]
    lemma = result["lexemeLabel"]["value"]
    lid = value.split("/")[-1]

    wikidata_lexemes.update({lemma: {"lid": lid, "lexcat": lexcat}})