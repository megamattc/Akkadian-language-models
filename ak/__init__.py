
import spacy
from spacy.language import Language, BaseDefaults
from spacy.lang.tokenizer_exceptions import URL_MATCH
#from thinc.api import Config
from .stop_words import STOP_WORDS
from .tokenizer_exceptions import TOKENIZER_EXCEPTIONS
from .punctuation import TOKENIZER_PREFIXES, TOKENIZER_SUFFIXES, TOKENIZER_INFIXES
from .lex_attrs import LEX_ATTRS
#from .tag_map import TAG_MAP
from .syntax_iterators import SYNTAX_ITERATORS
from spacy.tokens import Doc
from typing import Optional
from thinc.api import Model
import srsly
from .lemmatizer import AkkadianLemmatizer
from .fst_checker import FSTChecker

# https://nightly.spacy.io/api/language#defaults
class AkkadianDefaults(BaseDefaults):
    stop_words = STOP_WORDS
    tokenizer_exceptions = TOKENIZER_EXCEPTIONS
    prefixes = TOKENIZER_PREFIXES
    suffixes = TOKENIZER_SUFFIXES
    infixes = TOKENIZER_INFIXES
    lex_attr_getters = LEX_ATTRS
    token_match = None
    url_match = URL_MATCH
    #tag_map = TAG_MAP
    writing_system = {"direction": "ltr", "has_case": True, "has_letters": True}

@spacy.registry.languages("ak") #https://nightly.spacy.io/api/top-level#registry
class Akkadian(Language):
    lang = "ak"
    Defaults = AkkadianDefaults

    #custom on init

@Akkadian.factory(
    "lemmatizer",
    assigns=["token.lemma"],
    default_config={"model": None, "mode": "lookup", "overwrite": False},
    default_score_weights={"lemma_acc": 1.0},
)
def make_lemmatizer(
    nlp: Language, model: Optional[Model], name: str, mode: str, overwrite: bool
):
    return AkkadianLemmatizer(nlp.vocab, model, name, mode=mode, overwrite=overwrite)

@Akkadian.factory(
    "fst_checker",
    requires=["token.text","token.pos"]
)
def make_fst_checker(nlp: Language, name: str):
    return FSTChecker(nlp, name)

#Experimental sentencizer. Not finished.

#def make_sentencizer(
#    nlp: Language, name: str, punct_chars: Optional[List[str]], overwrite: bool
#):
#    return AkkadianSentencizer(name, punct_chars=punct_chars, overwrite=overwrite)
 


#Maybe we don't need custom tagger
#def make_tagger(
#    nlp: Language, name: str, model: Model, overwrite: bool, scorer: Optional[Callable], neg_prefix: str,
#):
#    return AkkadianTagger()

#Add locations of lookups data to the registry
@spacy.registry.lookups("ak")
def do_registration():
    from pathlib import Path
    current_path = Path.cwd()
    lookups_path = current_path / "lookups"
    result = {}
    for lookup in lookups_path.iterdir():
        key = lookup.stem[lookup.stem.find('_') + 1:]
        result[key] = str(lookup)
    return result

__all__ = ["Akkadian"]
