# Note on morphological annotation

The morphological annotation scheme used for AkkParser generally follows that of Luukko, Sahala et. al. 2020. In addition to this, the following should be noted.

## General notes on format

Unlike Luukko, Sahala et. al., I do not manually separate verbal and nominal suffixes from their base in the normalization so as to treat them as separate tokens. Rather, I encode them as features in the morphological description. An example is *mārūšu* 'his sons', which receives the encoding

* *mārūšu* : Gender=Masc|Number=Plur|Case=Nom|PossSuffNum=Sing|PossSuffPer=3|PossSuffGen=Masc

The labels for the suffixes are generally self-explanatory, with the following exceptions:

* There are different labels for verbal suffixes, nominal suffixes, and suffixes on prepositions. The verbal suffix labels begin with VerbSuff-, the nominal suffix labels with PossSuff-, and the preposition suffix labels with PrepSuff-.

* Because the morphological annotation scheme was initially designed for Neo-Assyrian, no distinction is made between dative and accusative verbal suffixes. If and when it comes time to do annotations for OB and before, this scheme will have to be augmented.

* The presence of the *-mā* suffix is labelled with Focus=Yes, even as the uses of the particle are various and not necessarily related to linguistic focus. The label is for convenience only.

* There is a soft inconsistency in how certain unary features are treated. Generally unary features like *-mā*, the subordinative marker *-ū*, and the subordinative *-ni* are given the value 'Yes' if explicitly present, while the label is entirely absent if the morpheme is not present. At a few points, however, I experimented with a binary representation, where the absence of the morpheme was indicated by using the value 'No'. Hence a form like *nēpuš* 'we did' would include features Subordinative=No|Focus=No. This has meant a minority of the model's analyses will include 'No' values for these features alongside leaving the label out entirely. In the future I will likely systematize this issue.

* Because AkkParser's morphologizer is statistical and largely independent of the syntactic parser, there need not be consistency either within the set of features for a given form (e.g. a verb being labelled as both precative and having present tense) or between the features and the syntactic labels (e.g. nominal features appearing on a verbal form). At the current size of the treebank (approximately 100,000 words) the amount of intra-feature inconsistency has become fairly small (say less than 5%) while the morph-syntactic feature inconsistency is somewhat more common. These problems may become more prominently temporarily when training the model on a new corpus with novel features. 

* Also due to the fact that the morphologizer is statistical, on rare occasion the values for one feature may get mixed up with those of another (e.g. Case=Plur, Person=Acc).

## Notes on grammatical analysis

In terms of the actually grammatical analysis I use, it again largely follows Luukko, Sahala, et. al. 2020, save on a number of important points:

* I label predicative forms based on verbal adjectives as verbs and assign them person and number features just like more typical verbal forms.

* Although I initially identified verbal forms in the prohibitive with the feature-value pair Mood=Proh (as Luukko, Sahala, et. al. 2020 do), I eventually stopped using it because I think it is too difficult for the parser to identify the presence of prohibitive versus simple negative present verbs (as it is primarily a pragmatic phenomenon). 

* Similarly for the category of the vetitive. Initially I used it even though **in the Oracc normalized editions ** on the verbal form itself there is nothing to distinguish a vetitive from a preterite. Hence I have stopped recognizing this feature.

* As a side note, I think the overall set of categories used by Luukko, Sahala, et. al. 2020 for verbs (based on the schema of Reiner 1966) is inefficient for  purposes of automatic morphological analysis (in addition to being somewhat linguistically inaccurate). A maximally descriptive yet simpler set of labels for verbs can be obtained by combining the tense/aspect, mood, and finiteness categories.

* In some Akkadian grammars (such as Huehnergard's), the use of independent pronominal forms to modify nouns is regarded as an instance of demonstrative pronouns ('this king' etc.). I have taken these to be instances of determiners. Hence in phrases like *šarru šūati* the pronoun labeled as a determiner, even as its morphological features still reflect pronominal forms. 

* Similarly, I take quantifiers like *kala*, *kalīšina* to be determiners rather than nouns, even if they are the head of a construct phrase. 

* Based on what I have seen of the NA royal archive corpus, it is sometimes justifiable to treat independent pronominal forms like *šū, šūtu* as copular forms connecting subject and predicate or serving as existential markers. As a result, many of these pronominal forms have morphological feature-value pairs appropriate to copular verbs, even as their UPOS, XPOS labels still mark them as independent pronouns. Whether this analysis holds more widely in the NA corpus or beyond is not yet clear.

* For quotation particles like *mā*, *mūk*, *umma*, I assign the XPOS label 'Quotative' (this label may be changed in the future). Hence the full UPOS/XPOS label for such forms is PART, Quotative.

* There is a bit of prevarication in how I have treated by-forms(?) of certain compound prepositions, such as *ina* IGI versus IGI. In the former case I treat the Akkadian form underlying IGI as a noun in the genitive case, in construct with what follows it. Only *ina* was taken as a preposition, which assigns genitive case to IGI. In places where IGI alone appears I initially treated the form as a preposition, which assigns case to the following noun. More recently I have abandoned this, taking the IGI just as a noun in the genitive in construct, mainly due to the amount of work needed to relabel such forms as prepositions. What the actual status of these forms is I do not know. They do not seem to me to be simple written abbreviations of a full compound preposition given how they alternate in the NA corpus, but that is just a suggestion.

* Although Luukko, Sahala, et. al. regard participles as nouns, I have in later parts of my treebank often taken them as adjectives modifying their head noun, and either sitting in construct with their (single) nominal argument (as Huehnergard's OB grammar indicates), or, if the participle is seemingly not in construct, assigning explicit verbal roles to them like finite verbs. Part of the reason for this is that I do not think the participles stand in apposition to the head noun like epithets. There is not absolute consistency in whether the participle is labelled as an adjective or noun in the corpus, but the former label predominates in later parts of the treebank.

## Data bugs related to morphological annotation

Note that morphological feature typos in a conllu file are a major source of data bugs when converting the conllu files to spaCy binaries using the ```convert``` command. The most typical problems the compiler issues are:

* ValueError: need more than 1 value to unpack

* ValueError: too many values to unpack (expected 2)

These have to do with whether, for every token in the conllu file, its morphological feature string (if it has one) is of the form X1=Y1|X2=Y2|....|Xn=Yn. 

The first error occurs if the spaCy interpreter cannot parser an item into the form X=Y. This can happen if, in place of a valid string, there is simply the term 'null'. This usually happens when you are typing/pasting a string into the feature window of Inception but forget to confirm it by hitting return. However, despite my efforts to be meticulous about entering strings into Inception, I still do not know exactly when the 'null' appears. The error also happens if you forget to separate the feature and value parts of a pair with an '=' sign (e.g. CaseAcc instead of Case=Acc), or if you have double separator brackets with nothing inside (i.e. '||'), or if you have an initial or terminal separator bracket on the string (e.g. |Case=Acc|Number=Plur).  

The second error happens when the spaCy interpreter parses an item into more than a single pair X=Y. This can happen when you forget a separator bracket between pairs (e.g. Case=AccNumber=Plur instead of Case=Acc|Number=Plur). 

At some point I have improve the conllu format checker script to include checks for the above problems (which can reasonably done using regular expressions). For now, you should be aware of them as you check a conllu file manually.

## Conclusion

Overall, there is much that can and should be debated about an appropriate, morphological annotation scheme in UD shared among annotators of Akkadian. For now I am relying on my own ideas.


Works cited:

M. Luukko, A. Sahala, S. Hardwick, and K. Lindén. 2020. "Akkadian Treebank for early Neo-Assyrian Royal Inscriptions". In: Proceedings of the 19th International Workshop on Treebanks and Linguistic Theories, pages 124–134, Düsseldorf, Germany. Association for Computational Linguistics.

E. Reiner. 1966. *A Linguistic Analysis of Akkadian* (Janua Linguarum, Series Practica, 21). Mouton, The Hague