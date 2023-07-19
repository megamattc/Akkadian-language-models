# pip install sparqlwrapper
# https://rdflib.github.io/sparqlwrapper/

import sys
from SPARQLWrapper import SPARQLWrapper, JSON

endpoint_url = "https://query.wikidata.org/sparql"

query = """SELECT
  ?lexeme ?lemma
  ?lexical_category ?lexical_categoryLabel ?form ?word
WITH {
  SELECT ?lexeme ?lemma ?lexical_category ?form ?word WHERE {
    ?lexeme a ontolex:LexicalEntry ;
            dct:language wd:Q35518 ; 
            wikibase:lemma ?lemma ;
            wikibase:lexicalCategory ?lexical_category .
    OPTIONAL {
      ?lexeme ontolex:lexicalForm ?form .
      ?form a ontolex:Form ;
         ontolex:representation ?word ;
         wdt:P31 wd:Q117451320 .
         
         
    }
            
    FILTER(lang(?word)="mis-x-q113819406")
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


def get_results(endpoint_url, query):
    user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
    # TODO adjust user agent; see https://w.wiki/CX6
    sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    return sparql.query().convert()


results = get_results(endpoint_url, query)

for result in results["results"]["bindings"]:
    print(result)
