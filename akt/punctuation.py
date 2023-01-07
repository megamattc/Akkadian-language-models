
from spacy.lang.char_classes import LIST_ELLIPSES, LIST_ICONS, LIST_PUNCT, LIST_QUOTES, LIST_CURRENCY
from spacy.lang.char_classes import CURRENCY, UNITS, PUNCT,COMBINING_DIACRITICS, HYPHENS
from spacy.lang.char_classes import CONCAT_QUOTES, ALPHA, ALPHA_LOWER, ALPHA_UPPER
from spacy.lang.punctuation import TOKENIZER_PREFIXES as BASE_TOKENIZER_PREFIXES
from spacy.lang.punctuation import TOKENIZER_SUFFIXES as BASE_TOKENIZER_SUFFIXES
from spacy.lang.punctuation import TOKENIZER_INFIXES as BASE_TOKENIZER_INFIXES

split_chars = lambda char: list(char.strip().split(" "))
merge_chars = lambda char: char.strip().replace(" ", "|")
group_chars = lambda char: char.strip().replace(" ", "")


_prefixes = BASE_TOKENIZER_PREFIXES

_suffixes = BASE_TOKENIZER_SUFFIXES

_infixes = BASE_TOKENIZER_INFIXES

#Remove "{", "}", and ")" from spacy's default punctuation list:

_punct = (
    r"… …… , : ; \! \? ¿ ؟ ¡ \( \[ \] < > _ # \* & 。 ？ ！ ， 、 ； ： ～ · । ، ۔ ؛ ٪"
)

LIST_PUNCT = split_chars(_punct)

#Also included regex to check for word initial "{" (for determiners). Not sure if it duplicates above adjustment

TOKENIZER_PREFIXES = (
    [r"(?<=\s)\{(?=\S)","§", "%", "=", "—", "–", r"\+(?![0-9])"]
    + LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_CURRENCY
    + LIST_ICONS
)


#TOKENIZER_SUFFIXES = _suffixes

TOKENIZER_SUFFIXES = (
    LIST_PUNCT
    + LIST_ELLIPSES
    + LIST_QUOTES
    + LIST_ICONS
    + ["'s", "'S", "’s", "’S", "—", "–"]
    + [
        r"(?<=\S)\)(?=\s)",
        r"(?<=\S)\}(?=\s)",
        r"(?<=[0-9])\+",
        r"(?<=°[FfCcKk])\.",
        r"(?<=[0-9])(?:{c})".format(c=CURRENCY),
        r"(?<=[0-9])(?:{u})".format(u=UNITS),
        r"(?<=[0-9{al}{e}{p}(?:{q})])\.".format(
            al=ALPHA_LOWER, e=r"%²\-\+", q=CONCAT_QUOTES, p=PUNCT
        ),
        r"(?<=[{au}][{au}])\.".format(au=ALPHA_UPPER),
    ]
)

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
