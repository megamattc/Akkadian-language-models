import os
import json
from typing import List, Tuple, Callable, Iterable
from spacy import Language
from spacy.training import Example
from spacy.lookups import Lookups
from spacy.pipeline import Lemmatizer
from spacy.tokens import Token
from spacy.vocab import Vocab
from typing import Optional, List, Dict, Tuple
from thinc.api import Model
import spacy 

class AkkadianLemmatizer(Lemmatizer):
    def __init__(
        self,
        vocab: Vocab,
        model: Optional[Model],
        name: str = "lemmatizer",
        *,
        mode: str = "lookup",
        overwrite: bool = True,
    ) -> None:
        super().__init__(vocab, model, name, mode=mode, overwrite=overwrite)
        
        #lookups_tables = spacy.registry.lookups.get(ak)() #Not certain if this is necessary, but commenting out because it causes problems on initializing lemmatizer object.
        #if not nlp.vocab.lookups.has_table('lemma_lookup'):
        #    language_data = srsly.read_json(lookups_tables["lemma_lookup"])
        #    nlp.vocab.lookups.add_table("lemma_lookup", language_data)
           
    
    def rule_lemmatize(self, token: Token) -> List[str]:
        pass

    def lookup_lemmatize(self, token: Token) -> List[str]:

        lookup_table = self.lookups.get_table("lemma_lookup")
        string = token.text.lower()
        return [lookup_table.get(string, string)]

    

    def initialize(
        self,
        get_examples: Optional[Callable[[], Iterable[Example]]] = None,
        nlp: Optional[Language] = None,
        lookups: Optional[Lookups] = None,
    ):
        if lookups is None:
            self.lookups = self.create_lookups()
        else:
            self.lookups = lookups

    def create_lookups(self): #Got the next two functions from stackoverflow. Feels like a hack. 
        lookups = Lookups()
        lookups.add_table("lemma_lookup", self.json_to_dict('lookups/ak_lemma_lookup_1_2_5_15_anzu_barutu.json')) #Calls up json file associated with lemmas of SAA 1+2+5+15_anzu_barutu etc, in /lookups directory
    
        return lookups

    def json_to_dict(self, filename):
        location = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        with open(os.path.join(location, filename)) as f_in:
            return json.load(f_in)
