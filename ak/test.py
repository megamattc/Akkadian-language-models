import spacy
import ak

nlp = spacy.blank("ak")

nlp.add_pipe("lemmatizer").initialize()
#nlp.initialize()
AKLemmatizer = nlp.get_pipe("lemmatizer")

print(AKLemmatizer.mode)

doc = nlp("ana šarri bēlīya urdaka Bel-duri Ilu-mušezib")
print([token.lemma_ for token in doc])
