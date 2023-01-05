
from spacy.lang.char_classes import LIST_ELLIPSES, LIST_ICONS, LIST_PUNCT, LIST_QUOTES
from spacy.lang.char_classes import CURRENCY, UNITS, PUNCT
from spacy.lang.char_classes import CONCAT_QUOTES, ALPHA, ALPHA_LOWER, ALPHA_UPPER
from spacy.lang.punctuation import TOKENIZER_PREFIXES as BASE_TOKENIZER_PREFIXES
from spacy.lang.punctuation import TOKENIZER_SUFFIXES as BASE_TOKENIZER_SUFFIXES
from spacy.lang.punctuation import TOKENIZER_INFIXES as BASE_TOKENIZER_INFIXES


_prefixes = ["{"] + BASE_TOKENIZER_PREFIXES

_suffixes = BASE_TOKENIZER_SUFFIXES

_infixes = BASE_TOKENIZER_INFIXES


TOKENIZER_PREFIXES = _prefixes
TOKENIZER_SUFFIXES = _suffixes
#TOKENIZER_INFIXES = _infixes
TOKENIZER_INFIXES = (
    LIST_ELLIPSES
    + LIST_ICONS
    + [
        r"(?<=[0-9])[+\-\*^](?=[0-9-])",
        r"(?<=[{al}{q}])\.(?=[{au}{q}])".format(
            al=ALPHA_LOWER, au=ALPHA_UPPER, q=CONCAT_QUOTES
        ),
        r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
        # ✅ Commented out regex that splits on hyphens between letters:
        # r"(?<=[{a}])(?:{h})(?=[{a}])".format(a=ALPHA, h=HYPHENS),
        r"(?<=[{a}0-9])[:<>=/](?=[{a}])".format(a=ALPHA),
    ]
)
