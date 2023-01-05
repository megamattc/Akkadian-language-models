# Akkadian-language-models

Akkadian language models based on Spacy, trained on various subcorpora of Oracc with either on normalized texts or transliterated ones.
The initial model XXX (the description of which is to appear in publication) was trained on two volumes of Neo-Assyrian letters in normalization, specifically SAA 1 and 5, as well as slightly
modified training data from Luukko et. al. 2020, which consisted of Neo-Assyrian royal inscriptions.

Since then, the normalized training set has been expanded and currently consists of SAA 1, 5, parts of 2 and 15, all of SB Anzu and Barutu. The digital sources
for these volumes can be viewed on the list of Oracc projects (http://oracc.museum.upenn.edu/projectlist.html). The model trained on this data
is called YYY.

Another model ZZZ was trained on transliterated texts mirroring the normalized texts used to train YYY. The relation between the normalized and transliterated data sets
is described in the publication concerning XXX. 

The Oracc texts and metadata were scraped using modified versions of scripts made by Niek Veldhuis (niekveldhuis/compass/2_1_Data_Acquisition_ORACC/). 
Each text was placed in its own text file, save for the data from Luukko et. al. 2020, which came as one large file. 
These files were then annotated in Inception for part of speech, syntactic structure, and morphology according to the Universal Dependencies framework (universaldependencies.org), largely following the conventions used in Luukko et. al. 2020.
Details concerning the annotation schema can be found in ```XYZ```. The annotated files are in conllu format. The process of hand-annotation was assisted by bootstrapping. First, linguistic metadata culled from Oracc provided lemmas and coarse pos tags for most tokens, although these were occasionally changed by hand on linguistic grounds (see subfolder explanations) or overwritten by the language models in the course of training. Indeed, in the course of hand-annotation a spacy language model was periodically trained on the texts annotated up till that point and then used to suggest annotations for the remaining raw texts. These suggestions were verified or corrected by hand in a portion of the remaining raw texts until the enlarged training set justified retraining the model. This process accelerated the speed of hand-annotation (human in the loop). Additional details on the bootstrapping process can be found in the respective subfolders.

This repository also contains a prototype Akkadian Language class designed for spacy 3.0. It is currently meant for normalized texts and contains a substantial list of tokenizer exceptions for proper nouns and noun phrases in construct.

Works cited:

Mikko Luukko, Aleksi Sahala, Sam Hardwick, and Krister Lindén. 2020. Akkadian Treebank for early Neo-Assyrian Royal Inscriptions. In Proceedings of the 19th International Workshop on Treebanks and Linguistic Theories, pages 124–134, Düsseldorf, Germany. Association for Computational Linguistics.
