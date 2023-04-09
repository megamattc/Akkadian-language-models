from wikibaseintegrator.wbi_config import config as wbi_config
from wikibaseintegrator import wbi_login, datatypes, WikibaseIntegrator
from wikibaseintegrator.models import Reference, References, Form, Sense, Claim, Claims, Snak, Snaks
from wikibaseintegrator.models.qualifiers import Qualifiers
import logging
import csv

#logging.basicConfig(level=logging.DEBUG)

wbi_config['USER_AGENT'] = 'MyWikibaseBot/1.0 (https://www.wikidata.org/wiki/User:Sinleqeunnini)'


input_file = open("FrameLemmas.csv",'r',encoding="utf-8")

reader = csv.DictReader(input_file)

login_instance = wbi_login.Clientlogin(user='Sinleqeunnini', password='zJm3@DXFs#QB$se')

wbi = WikibaseIntegrator(login=login_instance)

verb="Q24905"
noun="Q1084"
adjective="Q34698"
propn="Q147276"

akkadian_language= "Q35518"
akkadian_in_latin_script = "mis-x-Q113819406"
described_by_source = "P1343"
cda = "Q115610663"
page_number_prop = "P304"
page_number = "405"
alternative_spelling = "P8530"
sense = "instruction"

lex_term_dict = {"noun":noun,"adj":adjective,"verb":verb,"pn":propn}

#lexcat = lex_term_dict[row["lexical_category"]]
lexcat = noun
#lexemelabel = row["term"]
lexemelabel = "têrtu"

lexeme = wbi.lexeme.new(lexical_category=lexcat, language=akkadian_language)
lexeme.lemmas.set(language=akkadian_in_latin_script, value=lexemelabel)


cda_claims = lexeme.claims.add(datatypes.Item(prop_nr=described_by_source,value=cda))

for cda_claim in cda_claims:
#cda_claim.mainsnak(datatypes.Item(prop_nr=described_by_source, value=cda))
    cda_claim.qualifiers.set([datatypes.ExternalID(prop_nr=page_number_prop, value=page_number)])
#cda_claim.qualifiers()
    print(cda_claim)

#lexeme.claims.add(cda_claim)

cursense = Sense()
cursense.glosses.set(language="en", value=sense)

lexeme.senses.add(cursense)

result = lexeme.write()
print(result)
