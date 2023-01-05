
from spacy.attrs import LIKE_NUM

_num_words = []

def like_num(text):
    if text.startswith(("+", "-", "±", "~")):
        text = text[1:]
    text = text.replace(",", "").replace(".", "")
    if text.isdigit():
        return True
    if text.count("/") == 1:
        num, denom = text.split("/")
        if num.isdigit() and denom.isdigit():
            return True
    if text.lower() in _num_words:
        return True
    return False

def prefix(string: str) -> str:
    return string[0:2]


def suffix(string: str) -> str:
    return string[-4:]

LEX_ATTRS = {LIKE_NUM: like_num}
