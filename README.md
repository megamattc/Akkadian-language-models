# Akkadian-language-models

Akkadian language models based on Spacy, trained on various subcorpora of Oracc with either on normalized texts or transliterated ones.
The initial model XXX (the description of which is to appear in publication) was trained on two volumes of Neo-Assyrian letters in normalization, specifically SAA 1 and 5, as well as slightly
modified training data from Luukko et. al. 2020, which consisted of Neo-Assyrian royal inscriptions.

Since then, the normalized training set has been expanded and currently consists of SAA 1, 5, parts of 2 and 15, all of SB Anzu and Barutu. The digital sources
for these volumes can be viewed on the list of Oracc projects (http://oracc.museum.upenn.edu/projectlist.html). The model trained on this data
is called YYY.

Another model ZZZ was trained on transliterated texts mirroring the normalized texts used to train YYY. The relation between the normalized and transliterated data sets
is described in the publication concerning XXX. 

The Oracc texts and metadata were scraped using modified versions of scripts made by Niek Veldhuis (https://github.com/niekveldhuis/compass/2_1_Data_Acquisition_ORACC/). 
Each text was placed in its own ```.txt``` file, save for the data from Luukko et. al. 2020, which came as one large file. 
These files were then annotated in Inception for part of speech, syntactic structure, and morphology according to the Universal Dependencies framework (universaldependencies.org), largely following the conventions used in Luukko et. al. 2020. The output format of these annotations
was in ```conllu```. Details concerning the annotation schema can be found in ```XYZ```. 

The process of hand-annotation was assisted by bootstrapping, and is an illustration of the 'human in the loop' approach to machine learning. In brief, linguistic metadata was initially culled from Oracc to provide lemmas and generic
part of speech tags (denoted UPOS) for most of the tokens in the training set. These tags were, however, occasionally changed on linguistic grounds  or overwritten by the language model in the course of training (see ```XYZ```). We chose an initial subset of texts from this data set and filled out by hand a complete scheme of annotations for that subset consisting of, beyond the initial lemmatization and UPOS tags, Oracc-specific part of speech tags, token-wise morphological analysis, and syntactic dependencies. We then trained the model on this gold-standard training data and applied its predictions to the rest of the original training data for all the above fields of annotation. We chose another subset from the resulting annotated data set and corrected or completed its annotations by hand. Because these new, model-generated annotations were partially correct, completing or correcting them by hand was faster than making all annotations based only on the raw text. The resulting expanded gold-standard training data was used to train the model again, leading to a cyclic process of model training and annotation correction which significantly accelerated the speed of annotating the entire corpus.

An individual wishing to recreate the process we used to annotate an Akkadian corpus (in normalization or transliteration) and train a language model on it should consult ```XYZ``` for a detailed walkthrough of the various scripts and other procedures necessary to make the pipeline work.
The trained models are themselves packaged as Python modules and can be downloaded for use just like any other Spacy module with one
important caveat. Both the normalized and transliterated versions of the language models run on custom Language classes modeled on Spacy's
default Language classes located in ```/spacy/lang```. The folder for normalized class (as well as the label of the language in the files) is called ```ak``` and the corresponding label for the transliterated class is ```akt```. Both the ```ak``` and ```akt``` folders should be placed in the ```/spacy/lang``` directory alongside spacy's other language modules (e.g. ```de```, ```am```,```ar```). Alternatively, you may modify the appropriate scripts to locate these folders in another place of your choosing. 

We should also acknowledge that one component of the YYY model is a custom morphological parser modeled on Aleksi Sahala's parser for
Babylonian dialects of Akkadian (see https://github.com/asahala/BabyFST and Sahala 2020). Our modifications mainly consist of adapting the parser
for Neo-Assyrian dialects and integrating its functionality into a Spacy pipeline. More details can be found in ```XYZ```.

Works cited:

M. Luukko, A. Sahala, S. Hardwick, and K. Lindén. 2020. "Akkadian Treebank for early Neo-Assyrian Royal Inscriptions". In: Proceedings of the 19th International Workshop on Treebanks and Linguistic Theories, pages 124–134, Düsseldorf, Germany. Association for Computational Linguistics.

A. Sahala, M. Silfverberg, A. Arppe, and K. Lindén. 2020. “BabyFST : Towards a Finite-State Based Computa-
tional Model of Ancient Babylonian”. In: Proceedings of the 12th Conference on Language Resources and
Evaluation (LREC 2020). Ed. by N. Calzolari, pp. 3886–3894. Marseille, France. European Language Resources Association.
