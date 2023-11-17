# Akkadian-language-models

Akkadian language models based on Spacy, trained on various subcorpora of Oracc with either on normalized texts or transliterated ones. The bulk of the sentences come from selected projects hosted on Oracc that came with lemmatization, POS tags, and in some instances paragraph divisions. An additional set of augmentation data consisting of about 250 normalized sentences made by the contributor were also added. 

The initial model AkkParser (Ong and Gordin 2023 - to appear) is found in `/ak_basic_model` was trained on two volumes of Neo-Assyrian letters in normalization, specifically SAA 1 and 5, as well as slightly
modified training data from Luukko et. al. 2020, which consisted of Neo-Assyrian royal inscriptions.

The more developed normalized model (i.e. model trained on normalized sentences) is based on a substantially larger data set from Oracc and is under continual development. It is located in `/ak_norm_model`. In addition to the modified data from Luukko et. al. 2020 and the augmentation data, a list of the SAA volumes comprising the data set is given below (along with percentage of each volume that has been annotated and included in the data set): 

* SAA 1 - Letters from the royal archives of Sargon II (r. 721-705): Assyria and the West. 100% complete.
* SAA 2 - Neo-Assyrian treaties and oaths. 100% complete.
* SAA 3 - Court Poetry and Literary Miscellanea. 0% complete.
* SAA 4 - Queries to the Sungod: Divination and Politics in Sargonid Assyria. 0% complete.
* SAA 5 - Letters from the royal archives of Sargon II (r. 721-705): North and Northeast. 100% complete. 
* SAA 6 - Legal Transactions of the Royal Court of Nineveh, Part I: Tiglath-Pileser III through Esarhaddon. 0% complete.
* SAA 7 - Imperial Administrative Records, Part I: Palace and Temple Administration. 0% complete.
* SAA 8 - Astrological reports. 1% complete.
* SAA 9 - Assyrian prophecies. %100 complete.
* SAA 10 - Letters from Assyrian and Babylonian scholars. 8% complete.
* SAA 11 - Imperial Administrative Records, Part II: Provincial and Military Administration. 0% complete.
* SAA 12 - Grants, Decres and Gifts of the Neo-Assyrian Period. 0% complete.
* SAA 13 - Letters from Assyrian and Babylonian Priests to Kings Esarhaddon and Assurbanipal. 10% complete.
* SAA 14 - Legal Transactions of the Royal Court of Nineveh, Part II: Assurbanipal Through Sin-šarru-iškun. 0% complete.
* SAA 15 - Further letters of Sargon II: Babylonia and the eastern provinces. 100% complete.
* SAA 16 - Political correspondence of Esarhaddon. 13% complete.
* SAA 17 - The Neo-Babylonian Correspondence of Sargon and Sennacherib. 100% complete.
* SAA 18 - The Babylonian Correspondence of Esarhaddon and letters to Assurbanipal and Sin-šarru-iškun from Northern and Central Babylonia. 100% complete.
* SAA 19 - Letters of Tiglath-Pileser III and Sargon II from Calah/Nimrud. 63% complete.
* SAA 20 - Assyrian Royal Rituals and Cultic Texts. 0% complete.
* SAA 21 - Letters of Assurbanipal: Assyria, Babylonia, and vassal states. %100 complete.

A few additional Oracc projects also provide the following data:

* Anzu - Standard Babylonian Anzu Epic. %100 complete.
* Barutu - A small number of extispicy texts. %100 complete.
* RINAP4 - Royal inscriptions of Esarhaddon (r. 681-669). Annotations mainly cover Nineveh A prism and certain fragmentary copies. 10% complete.
* tcma/assur - Middle Assyrian letters and administrative texts from Assur and northern Mesopotamia. ~.005% complete (4 letters done).

Another model AkkParser-Trans was trained on transliterated texts mirroring the normalized texts used to train AkkParser-Norm. The relation between the normalized and transliterated data sets is described in Ong and Gordin 2023 (to appear). However, currently only a subset of the texts used to train the normalized model are currently formatted for the transliterated model. It is located under `/akt_trans_model`.  

For more details on these projects, consult the [Oracc project list](http://oracc.museum.upenn.edu/projectlist.html).

The Oracc texts and metadata were scraped using modified versions of scripts made by Niek Veldhuis (https://github.com/niekveldhuis/compass/2_1_Data_Acquisition_ORACC/). 
Each text was placed in its own ```.txt``` file, save for the data from Luukko et. al. 2020, which came as one large file. 
These files were then annotated in Inception for part of speech, syntactic structure, and morphology according to the Universal Dependencies framework (universaldependencies.org), largely following the conventions used in Luukko et. al. 2020. The output format of these annotations
was in ```conllu```. Details concerning the annotation schema can be found in ```guidelines.txt```. 

The process of hand-annotation was assisted by bootstrapping, and is an illustration of the 'human in the loop' approach to machine learning. In brief, linguistic metadata was initially culled from Oracc to provide lemmas and generic
part of speech tags (denoted UPOS) for most of the tokens in the training set. These tags were, however, occasionally changed on linguistic grounds  or overwritten by the language model in the course of training (see ```guidelines.txt```). We chose an initial subset of texts from this data set and filled out by hand a complete scheme of annotations for that subset consisting of, beyond the initial lemmatization and UPOS tags, Oracc-specific part of speech tags, token-wise morphological analysis, and syntactic dependencies. We then trained the model on this gold-standard training data and applied its predictions to the rest of the original training data for all the above fields of annotation. We chose another subset from the resulting annotated data set and corrected or completed its annotations by hand. Because these new, model-generated annotations were partially correct, completing or correcting them by hand was faster than making all annotations based only on the raw text. The resulting expanded gold-standard training data was used to train the model again, leading to a cyclic process of model training and annotation correction which significantly accelerated the speed of annotating the entire corpus.

An individual wishing to recreate the process we used to annotate an Akkadian corpus (in normalization or transliteration) and train a language model on it should consult ```guidelines.txt``` for a detailed walkthrough of the various scripts and other procedures necessary to make the pipeline work.
The trained models are themselves packaged as Python modules and can be downloaded for use just like any other Spacy module with one
important caveat. Both the normalized and transliterated versions of the language models run on custom Language classes modeled on Spacy's
default Language classes located in ```/spacy/lang```. The folder for normalized class (as well as the label of the language in the files) is called ```ak``` and the corresponding label for the transliterated class is ```akt```. Both the ```ak``` and ```akt``` folders should be placed in the ```/spacy/lang``` directory alongside spacy's other language modules (e.g. ```de```, ```am```,```ar```). Alternatively, you may modify the appropriate scripts to locate these folders in another place of your choosing. 

We should also acknowledge that one component of the AkkParser-Norm model is a custom morphological parser modeled on Aleksi Sahala's parser for
Babylonian dialects of Akkadian (see https://github.com/asahala/BabyFST and Sahala 2020). Our modifications mainly consist of adapting the parser
for Neo-Assyrian dialects and integrating its functionality into a Spacy pipeline. More details can be found in ```guidelines.md```.

Works cited:

M. Luukko, A. Sahala, S. Hardwick, and K. Lindén. 2020. "Akkadian Treebank for early Neo-Assyrian Royal Inscriptions". In: Proceedings of the 19th International Workshop on Treebanks and Linguistic Theories, pages 124–134, Düsseldorf, Germany. Association for Computational Linguistics.

A. Sahala, M. Silfverberg, A. Arppe, and K. Lindén. 2020. “BabyFST : Towards a Finite-State Based Computa-
tional Model of Ancient Babylonian”. In: Proceedings of the 12th Conference on Language Resources and
Evaluation (LREC 2020). Ed. by N. Calzolari, pp. 3886–3894. Marseille, France. European Language Resources Association.
