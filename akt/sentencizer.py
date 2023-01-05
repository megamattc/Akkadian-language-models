#An experiment in designing a sentencizer which recognizes sentence initial tokens or sequences of tokens for NA letters. Not yet finished

from typing import List, Tuple
from spacy import Language
from spacy.pipeline import Sentencizer
from spacy.tokens import Token
from typing import Optional, List, Dict, Tuple
from thinc.api import Model
import spacy

class AkkadianSentencizer(Sentencizer):
    def __init__(
        self,
        name = "sentencizer",
        *,
        punct_chars = None,
        overwrite = False, #Set overwrite to False
    ) -> None:
        super().__init__(name, punct_chars=punct_chars, overwrite=overwrite)

        quotativeList = ["mā","muk","mūku","nuk","nūku"] #List of quotative particles, 
        tasparList = ["tašpuranni"]
        
    def __call__(self, doc):
        """Apply the sentencizer to a Doc and set Token.is_sent_start = 1 if token meets certain conditions particular to letters genre.

        doc (Doc): The document to process.
        RETURNS (Doc): The processed Doc.

        """
        error_handler = self.get_error_handler()
        try:
            for i, token in enumerate(doc):
                if i < len(doc)-1: #If index is not at the end of the doc
                    if doc[i].text == "ša" and doc[i+1].text in 
                if doc[i].text in quotativeList:
                    doc[i].sent_start = 1
            return doc
        except Exception as e:
            error_handler(self.name, self, [doc], e)
