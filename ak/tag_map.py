# coding: utf8
from __future__ import unicode_literals

from ...symbols import POS, AUX, ADJ, CCONJ, NUM, ADV, ADP, X, VERB
from ...symbols import NOUN, PART, INTJ, PRON

#Map Oracc pos tags to UD POS

TAG_MAP = {
    "EN": {POS: ADJ},
    "CN": {POS: PROPN},
    "DN": {POS: PROPN},
    "FN": {POS: PROPN},
    "GN": {POS: PROPN},
    "LN": {POS: PROPN},
    "MN": {POS: PROPN},
    "ON": {POS: PROPN},
    "PN": {POS: PROPN},
    "QN": {POS: PROPN},
    "RN": {POS: PROPN},
    "SN": {POS: PROPN},
    "TN": {POS: PROPN},
    "WN": {POS: PROPN},
    "YN": {POS: PROPN},
    "NU": {POS: NUM},
}

#Original line:  "AAfp2x": {POS: ADJ, "morph": "Case=Gen|Degree=Pos|Gender=Fem|MorphPos=Adj|Number=Plur"},
