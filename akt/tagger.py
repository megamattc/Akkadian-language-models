#Maybe we don't need this custom tagger
from spacy import Language
from spacy.lookups import Lookups
from spacy.pipeline import Lemmatizer
from spacy.tokens import Token
from spacy.vocab import Vocab
from typing import Optional, List, Dict, Tuple
from thinc.api import Model
import spacy 


class AkkadianTagger(Tagger):
    def __init__(
        self,
        vocab: Vocab,
        model: Optional[Model],
        name: str = "tagger",
        *,
        overwrite: bool = False, # The term 'BACKWARD_OVERWRITE' is the value for overwrite in the original Tagger class
    ) -> None:
        super().__init__(vocab, model, name, overwrite=overwrite)
