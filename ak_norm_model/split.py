
"""Load inception conllu data and split into train and test files"""
import srsly
import typer
import warnings
from pathlib import Path
import random

import spacy
from spacy.tokens import DocBin
from spacy.util import filter_spans, get_lang_class
from sklearn.model_selection import train_test_split


def split(test_size:float, random_state:int, lang:str):

    lang = get_lang_class(lang)
    nlp = lang()

    corpus_path = Path.cwd() / "corpus" / "converted"
    assert corpus_path.exists()

    doc_bin = DocBin()
    for spacy_file in corpus_path.iterdir():
        doc_bin.merge(DocBin().from_bytes(spacy_file.read_bytes()))
    docs = [doc for doc in doc_bin.get_docs(nlp.vocab)]
    random.shuffle(docs)
    train_set, validation_set = train_test_split(docs, test_size=test_size, random_state=random_state)
    validation_set, test_set = train_test_split(validation_set, test_size=test_size, random_state=random_state)
    
    # the DocBin will store the training documents
    train_db = DocBin()
    for doc in train_set:
        train_db.add(doc)
    train_db.to_disk((corpus_path /"train.spacy"))

    # Save the validation Docs to disk 
    validation_db = DocBin()
    for doc in validation_set:
        validation_db.add(doc)
    validation_db.to_disk((corpus_path / "dev.spacy"))
    
    # Save the test Docs to disk 
    test_db = DocBin()
    for doc in test_set:
        test_db.add(doc)
    test_db.to_disk((corpus_path / "test.spacy"))

    print(f'🚂 Created {len(train_set)} training docs')
    print(f'😊 Created {len(validation_set)} validation docs')
    print(f'🧪  Created {len(test_set)} test docs')

if __name__ == "__main__":
    typer.run(split)
