# Guidelines for running the pipelines associated with models AkkParser, AkkParser-Norm, and AkkParser-Trans, including:

* Setting up the necessary software packages and applications needed for making annotations, text processing, model training, etc.
* General description of the pipeline components for all models
* Walkthrough of the workflow from start to finish, with notes about things to pay attention to, likely problems, and issues I haven't solved or still find troublesome
* Overview of helper scripts and directory structure

How much guidance you need in using the tools and data in this repository depends greatly on your background in Natural Language Processing (NLP), programming skills, intended purpose, and what you already have installed on your machine. You will need to be able to use the terminal and understand basic command line functions, and knowing the basics of Python is also very helpful. With that said, you may very well find shortcuts or better ways to do things than I have, depending on how much effort you want to put into automating certain tasks as opposed to just getting them done by hand quickly. You may also only wish to 'get your feet wet' in terms of seeing how certain tasks are done without needing to do all the work necessary for completing that task (say annotating a whole batch of texts). You can simply skip to the next checkpoint in the pipeline that has a full data set processed for you.

The guidelines are a mix of things in the sense that they reflect both how the original model AkkParser and its data set were created and how methods have evolved since then. A high-level discussion of AkkParser and its data can be found in the forthcoming publication of this model. Here we are more interested in the nuts and bolts of how to reproduce the pipeline and to document things for posterity. 

Another things to note is that the guidelines assume you are working with lemmatized texts from [Oracc](http://oracc.museum.upenn.edu/). If you intend to work with non-Oracc texts or non-lemmatized texts from Oracc you will have to make certain adjustments to the pipeline. 

## Getting the basic tools

In these guidelines, when we speak of a 'natural language model' we mean a machine learning algorithm trained on annotated texts of a given human language, capable of various analytical tasks such as syntactic parsing of sentences, morphological decomposition of words, or semantic role labeling. Spacy is a Python suite which allows individuals to train efficient natural language models in a 'fairly' straightforward way, and it is what we will be using for all our models. 

### Spacy

You can go to the [spacy page regarding installation](https://spacy.io/usage) and follow their instructions (including use of the graphical widget) for obtaining the configuration appropriate for your hardware. If you are overwhelmed by the set of possible ways to proceed with installation, you can instructions associated with ```pip```.  

If you use the widget to help in establishing the correct installation command(s), you do not need to worry about the various language options or efficient vs. accuracy option. We will be using our own custom language classes. You may find it convenient, however, to click on the option for 'trained models', as it includes certain packages you may wish to use at a later date.

Whether you choose to install spacy within a virtual environment or not, you need to note the location of where it is installed on your machine. You can find it by searching for a folder named ```spacy``` using a method of your choice. You should find there is a subfolder ```spacy/lang``` which contains dozens of folders named things like ```en```, ```de```, ```af```, and ```ar```. This is where spacy stores its default language modules (or classes) for English, German, Arabic, etc. You need to place the folders ```ak``` and ```act``` from the repository into this directory.

#### Excursus: More about the language modules

The files they contain specify basic information such as how the writing system and punctuation of the language work, how to split a string of characters into words (i.e. tokenize), direction of the script, etc. Note that it is not necessary for a pipeline to have a specific language class specified, as spacy can use a default language class ```xx``` consisting of basic settings. 

Our pipelines use two custom language modules, ```ak``` and ```akt```, placed within folders with the same name. The module ```ak``` is used for normalized Akkadian texts while ```akt``` is for transliterated texts. In the future they may be combined. What is important about these modules is that they tell spacy how to tokenize transliterated or normalized Akkadian texts the right way. In particular, they tell spacy not to tokenize on dashes (```-```) or brackets (```{}```) and parentheses when used to denote determiners or numerical signs. Originally I did not include this feature in the language modules themselves and had imperfect workarounds for tokenization problems, and as a result early annotations in SAA 1 and 5 sometimes feature improper splits on dashes or brackets. 

A second feature of the language classes is that they contain a *lookup table* for all the lemmas in the texts used as training data. These lookup tables (one for normalization, one for transliteration) consist of Python dictionaries which associate linguistic forms appearing the training set (such as ```šar-ri```) with their underlying lemma (```šarru```). They are located in the ```lookup``` folder within the respective language class. 

> If you intend to start annotating your own corpus of texts from Oracc, you can integrate the lemma lookup table from your corpus into that belonging to AkkParser-Norm or AkkParser-Trans using the ```merge_norm_lemma_lookup.py``` and ```merge_norm_lemma_lookup.py``` scripts (they differ only in a few small details). If you do this (or if you wish to use your own custom lemma lookup table), you may need to update the name of the resulting lookup table specified in the custom ```lemmatizer.py``` file within the ```ak``` or ```act``` folder. Look for the section of the file consisting of

``` 
def create_lookups(self): 
        lookups = Lookups()
        lookups.add_table("lemma_lookup", self.json_to_dict('lookups/ak_norm_lemma_lookup_1_2_5_15_anzu_barutu.json'))
```  

And change the name of the file to what you need. From the code snippet above, you can see that I chose to label files consisting of data drawn from multiple Oracc projects with names reflecting all the projects in them. This makes for lengthy, awkward file names, but since I am constantly expanding the set of corpora I annotate as well as switching between normalized and transliterated data, this convention allows me to see at a glance what the input dictionaries to a model consist of and hence avoid confusion between model versions. You might prefer a different method to keep track of model content, but note that JSON files do not allow for comments in them. 

The remaining folders of the repository should **not** be placed in the spacy installation directory, but instead whatever workspace you use.

### Getting Inception

Inception is an annotator tool created at the Technical University of Darmstadt. We will be using it to do all our annotation work. It is available a Java application at the team's [project homepage](https://inception-project.github.io/). The program uses your default web browser as a user interface and can be launched by clicking on it from the file finder window. The program should probably be placed in your workspace for the annotation project. You can click on the launch icon it creates multiple times to have multiple windows for the program open on your browser. In what follows, it may be convenient to have two windows of Inception open, one for doing the annotations themselves, the other for uploading and deleting files. *Note that you should use only one version of Inception for your annotation work.* The developers make updates to their software, and while you can transfer your work between versions, this requires extra steps and is likely unnecessary for an annotation project such as ours. 

### Other tools

You will need a text editor to process the ```conllu``` files (explained below) that Inception and spacy work with, as well as to edit the various helper scripts for names of files and such in case you wish to do your own annotations. I have found it very helpful to use two kinds of text editors: a very basic one for editing the ```conllu``` files and another for editing programming scripts or doing more sophisticated text manipulation. Whatever you choose, you should make sure the text editor you use for manipulating ```conllu``` files **does not automatically adjust spacing between words or otherwise encodes what look like tab-separated columns with something other than tabs, e.g. single spaces**. I have found it enormously frustrating to edit ```conllu``` files in certain programs like PyCharm or Aquamacs, as they sometimes adjust word alignment in different lines in ways that wreak havoc on the ```conllu```tab-separated format. You may not know just by looking at it that the space encoding between columns is wrong, or, even if you enable the appropriate display of space encoding in these programs, your editing may lead them to introduce spaces in ways you don't want (e.g. pressing Tab doesn't actually introduce a single tab). Both Inception and Spacy are finicky when it comes to the format of the ```conllu``` files they accept, and I can attest to huge amounts of aggravation that come with having to debug a large ```conllu``` file just because of an invisible spacing issue. While it is usually safe to use sophisticated text editors for some amount of ```conllu``` manipulation, I think it is better to use something like the Mac OS's default TextEdit when you want to play it safe. This program does not seem to introduce spacing errors, and pressing Tab always seems to mean just tab.

It will also be helpful to have access to a tool that can debug JSON files and otherwise format them in a pleasing way. I found [this online site](https://jsonformatter.curiousconcept.com/) to be very useful for converting the JSON output from my scripts into the format needed by other parts of my pipeline. While it is almost certainly possible to find ways to make the scripts themselves format their JSON output in the necessary ways, I did not take the time to figure out how to do that in many places within my pipeline (although such might be done eventually). *Note above all that at various points you will need to convert the single quotes in the JSON files produced by the scripts to double quotes so that the file can be input to another script or program*. Using a JSON formatter such as the one linked above will do this as well as make it more readable to the human eye.

## Step 1: Scraping Oracc data, producing basic dictionaries

The python scraper scripts in the ```/utils``` folder are based on Jupyter notebooks written by Niek Veldhuis (https://github.com/niekveldhuis/compass/tree/master/2_1_Data_Acquisition_ORACC). If you want to understand the core aspects of these scripts (e.g. how they process the JSON files, generate and manipulate the pandas data frame) you should consult the comments in those notebooks. 

You run the python scraper scripts in the beginning, when you want to get a corpus from Oracc in normalization and/or transliteration plus the associated helper files. There are different scraper scripts because, depending on the corpus you want to download, certain helpful formatting features can be introduced. For instance, many literary works are divided into single or double line verses, meaning that if you tell the scraper to produce output where each line or double line is separated by a newline, that will tell spaCy to regard each line/double line as its own sentence. This can help enormously with parsing. 

Note that you must have the ```pandas``` and ```tqdm``` packages installed to run these scripts. In general, if you get errors saying that python cannot recognize a certain package, check that you have it installed.

### ProcessOraccVolume.py

This is the basic scraper that is blind to internal divisions of the text. The explanatory comments in this file are more verbose than in the other versions. You specify an Oracc volume/project you want to download in the variables ```oraccVolume``` and ```oraccProject``` (see Niek's [Jupyter notebook](https://github.com/niekveldhuis/compass/blob/master/2_1_Data_Acquisition_ORACC/2_1_0_download_ORACC-JSON.ipynb) for how volume labeling works) and the script outputs both transliterated and normalized versions of the corpus in the subfolders ```output_translit```, ```output_norm```. If you consult the Niek's notebooks on [basic Oracc corpus manipulation](https://github.com/niekveldhuis/compass/blob/master/2_1_Data_Acquisition_ORACC/2_1_3_basic_ORACC-JSON_parser.ipynb) and [extended corpus manipulation](https://github.com/niekveldhuis/compass/blob/master/2_1_Data_Acquisition_ORACC/2_1_4_extended_ORACC-JSON_parser.ipynb), you will see that the scraper outputs text by stringing together tokens according to their token identifier number, which tells you in what text, what line, what position in the line that token appears. 

In addition, the script produces three helper files, ```ak_norm_lemma_lookup_X.json'```, ```akt_trans_lemma_lookup_X.json```, ```ak_attribute_ruler_patterns_X.json```, where 'X' is the label of the Oracc volume you are downloading. The first and second JSON files are the lemma lookup dictionaries for the normalized (resp. transliteratted) texts and will ultimately need to be integrated into the language class ```ak``` (used for normalized texts) or ```akt``` (used for transliterated texts) that undergird the models. The third JSON file is an initial version of the attribute ruler file used to manually specify morphological features and POS labels of specific tokens. What to do with these helper files will be explained below.

### ProcessOraccVerseVolume.py

This scraper is meant for 'verse' texts or corpora, where it is assumed that one line in the text constitutes one sentence. The script cuts up the lines using the line identifier associated with each token. While theoretically the lines should be output in the order they appear in the text, occasionally I have found lines printed out of order. This may be either because of typos in the JSON file, or because the ordering of line ids mostly, but not completely, follows what we would expect. This remains a bug to be solved.

Note also that many verse texts occasionally have a sentence run across two lines. I currently do not know of a way to elegantly handle these exceptions, save to stitch the line components back up again during annotation.

### ProcessOraccChunkVolume.py

Similar to the verse scraper save that it divides up blocks of text according to the 'sentence' delimiter appearing in the JSON files of some Oracc corpora (such as some of the NA royal inscriptions). This scraper is useful for prose texts where the editor has broken up the text into blocks (marked by horizontal lines or paragraph breaks in the online edition), whereas a single line is not a meaningful delimiter for sentences. To see if your corpus is divided in such a way, look into the JSON files for that corpus and see if it contains a key-value pair of the form ```"type":"sentence"``` alongside the pair ```"node":"c"```, as in

```
{
          "node": "c",
          "type": "discourse",
          "subtype": "body",
          "id": "Q003230.U1",
          "cdl": [
            {
              "node": "c",
              "type": "sentence",
              "implicit": "yes",
              "tag": ".",
              "id": "Q003230.U2",
              "label": "i 1 - i 7",
              "cdl": [
              ...
  ```
As with ProcessOraccVerseVolume.py, this scraper seems to sometimes output chunks in different order than how they appear in the online edition. Furthermore, note that what the JSON file regards as a 'sentence' sometimes appears to be a subordinate clause of a complex sentence. This, at least, is what I have noticed so far while using the scraper on RINAP4.

### Note on dictionary formatting

The dictionaries output by the scraper scripts are not initially in a convenient human-readable format, nor are they in fact properly formatted to be reread as JSON files by other scripts later in the pipeline. The former problem is largely because the dictionaries are printed as a single line, without newlines to break up entries in a natural way. The latter problem is because strings are printed with single quotes while double quotes are often needed by the python function that reads in JSON objects. Although there are various python functions designed to 'pretty print' JSON dictionaries with double quotes, at the moment I have found they produce other formatting problems. My current work around, as irritating as it is, is to use an [online JSON formatter](https://jsonformatter.curiousconcept.com/) to reformat the helper files. A side-benefit of using such a formatter is that it can sometimes identify and fix other formatting errors in your file automatically. Until I have found a better solution in the original output mechanism for these dictionaries, you will have to reformat the helper files in the course of the pipeline, sometimes multiple times as they are taken in and spit out by other processing scripts. In what follows, I will usually assume such manual reformatting has been done by you when necessary, but may mention it occasionally as a helpful reminder.  

## Updating the language class 

The way I have implemented the processing pipeline, the lemma lookup table for a given corpus (whether in normalized or transliterated form) is integrated into the custom Akkadian language class itself (```ak```/```akt``` respectively). In particular, every corpus used in training the most current parsing models AkkParser-Norm/AkkParser-Trans has their lookup table integrated in the base language class and does not need to be incorporated in the supersisting model. However, if you are working on a new corpus (or want to recreate the steps used to general AkkParser in the first place), you will need know how to incorporate your lemma lookup table into the language class. We will assume we are working with a normalized corpus (relevant to ```ak```) but the transliterated case is completely parallel.

First you need to merge your lookup table with the one already present in ```ak```. Assuming you have placed the ```ak``` folder in ```/spacy/lang```, the current lookup table used for normalized texts is in ```spacy/lang/ak/lookups```. In my conventions, I label the current file of the lookup table according to all the corpora currently constituting it (i.e. all of the corpora for which I have or am currently producing treebanks). For instance, the file ```ak_norm_lemma_lookup_1_2_5_9_15_anzu_barutu_riao_rinap4.json``` contains the lemmata for SAA 1,2,5,9, 15, SB Anzu, Barutu, RIAO, and RINAP4. If you used the above scraper scripts to download and process another Oracc volume X, the lookup table will be called ```ak_norm_lemma_lookup_X.json```. 

Copy the current lemma lookup file into the ```utils``` directory alongside your own lemma lookup. In the ```utils``` directory should also be the scripts ```merge_norm_lemma_lookup.py``` and ```merge_trans_lemma_lookup.py```. Pick whichever is relevant to your case, and within it redefine the variables ```fileName1```, ```fileName2``` to match the current lemma lookup file and your own lookup file, respectively. Redefine the ```outputFile``` variable to be the name of the merged lookup file (which, in my conventions, results from just adding the label of the new corpus alongside the current string of labels). Run the script and reformat the resulting dictionary as mentioned in **Notes on dictionary formatting**. Note that the merge operation is such that key-value pairs in ```fileName2``` will overwrite those in ```fileName1``` if the keys overlap. You can reverse the values of ```fileName1```,```fileName2``` to have the opposite happen.

Place the new lookup table back in the ```/spacy/lang/ak/lookups``` folder. You may want to keep the old lookup table around just to be able to see at a glance (if you follow my naming conventions) what is the newest corpus added to the table.

Now open up ```/spacy/lang/ak/lemmatizer.py```, the file which defines the custom lemmatizer for models based on ```ak```. You need to change the name of the file the language class looks for as its lookup table. This is given within the function ```create_lookups()```, i.e.:

```
def create_lookups(self): 
        lookups = Lookups()
        lookups.add_table("lemma_lookup", self.json_to_dict('lookups/ak_norm_lemma_lookup_1_2_5_9_15_anzu_barutu_riao_rinap4.json')) #Calls up json file associated with lemmas of SAA 1+2+9+5+15_anzu_barutu etc, in /lookups directory
    
        return lookups


```
Change the name of the lookup file to match what you have under the ```/lookups``` directory. You have now updated the language class for the lookup table.

## Updating the attribute file

A similar merging process needs to be done with respect to the attribute ruler file already associated with the language model and the one newly produced by the scraper script. The difference is that the attribute ruler file is not built into the language class, but instead is loaded into the model during training time. There is no hard, theoretical reason why the attribute ruler is treated differently from the lookup table. We could, if we wanted, define a custom attribute ruler component at the level of the language class which loads no matter what model is built on top of it. For historical reasons, however, I have left it as a component of the model and not the language class. A minor justification for this is that it may occasionally be preferable to switch off the attribute ruler during training if it starts to be worse than the statistical tagger and morphologizer.

In any event, assuming you are working with a normalized corpus (the transliterated case is completely parallel), locate the current attribute file under ```Akkadian-language-models/ak_norm_model```. It should be named much like the lemma lookup file, e.g. ```attribute_ruler_patterns_1_2_5_9_15_anzu_barutu_rinap4.json```. Copy this file to ```/utils``` alongside your new attribute file (reformatted of course), and edit the ```merge_attribute_ruler_patterns.py``` so that the variables ```fileName1```,```fileName2```, and ```outputFileName``` reflect the two attribute files to be merged and the output file name, respectively. 

Note that in addition to this, one must 'clean up' the resulting attribute ruler file (besides reformatting it using the JSON web application) using ```clean_attribute_ruler_patterns.py```. The main issue is the need to eliminate duplicate entries in the file, because the top level data structure is a list. Change the values of the variables ```inputFile1``` and ```outputFile``` in the file accordingly, and return the resulting attribute file to ```Akkadian-language-models/ak_norm_model```. 

Finally, the configuration file of the model must be edited to reflect the new name of the attribute file. For AkkParser-Norm, the current config file is named ```combined_lemmatizers_suff.cfg```. In ```ak_norm_model/configs/combined_lemmatizers_suff.cfg```, adjust the name of the file in the section

```
[initialize.components.attribute_ruler.patterns]
@readers = "srsly.read_json.v1"
path = "attribute_ruler_patterns_1_2_5_9_15_anzu_barutu_rinap4.json"
```

to reflect the new file name.

## Training the 'empty' model to get the initial set of conllu files

We now want to create a set of conllu files corresponding to the set of texts in the chosen corpus, with all tokens lemmatized and assigned pos tags. This is the furthest that the pre-given Oracc metadata will take us. The difficulty, however, is that all we have are the base normalized (or transliterated) texts of the chosen corpus, and we do not want to create the conllu files by hand. 

We can create the conllu files with correct lemmas and POS tags automatically by bootstrapping. Assuming the model has already been trained on a pre-existing corpus (which is the case for AkkParser-Norm and AkkParser-Trans), we can train it again on this same pre-given training corpus save that the lemma lookup file and attribute ruler file have been updated in the way described above. All we are doing is having spaCy retrain the same model save that its lemma lookup and attribute file have been expanded to include the new corpus data. When the updated model is produced, we apply it to the base texts of the new corpus to get conllu files whose lemmas and pos tags are accurate, but whose morpho-syntactic annotations are wildly inaccurate.

To train the model, the project file that governs model training, evaluation, and packaging should be edited to reflect the new corpus. Edit ```ak_norm_model/project.yml``` so that in the following section

```
config: "combined_lemmatizers_suff"
lang: "ak"
treebank: "UD_Akkadian"
train_name: "akk_combined_nonrenumbered-ud-train"
dev_name: "akk_combined_nonrenumbered-ud-dev"
test_name: "akk_combined_nonrenumbered-ud-test"
package_name: "AkkParser_Norm_1_2_5_9_15_anzu_barutu_rinap4"
package_version: "0.0.0"
gpu: -1
```
the package name reflects the addition of the new corpus. The value of ```package_name``` is used to create a python package constituting the new model.

Once all this is done, enter the terminal and navigate to ```/ak_norm_model```. Run the command ```spacy project run train``` to train the model on the pre-given training data contained in ```/ak_norm_model/corpus```. After this, go to the subdirectory of ```/ak_norm_model/packages``` corresponding to the value of ```package_name```, where you will find the subfolders ```remainder``` and ```conllu_output_final```. The first folder is for whatever base texts you want the model to apply its predictions on (i.e. lemmas, pos tags, morpho-syntax). The folder ```conllu_output_final``` holds the conllu files containing these predictions. To apply the model to the files in ```remainder```, run either ```prose_model_annotator_pipe.py``` or ```verse_model_annotator_pipe.py``` depending on whether your base texts have no sentence/chunk separators or they do. Both process whatever is in ```remainder```. The resulting files in ```conllu_output_final``` are the starting point for manual correction and the subsequent bootstrapping cycle.

## Making annotations in Inception

Making annotations in Inception is fairly straightforward and will not be discussed in detail here, save to note a few things. First, making manual corrections/completions is the time to augment the attribute ruler file with complicated morphological forms you notice appearing over and over in your corpus without the parser getting them correct. Second, Inception does not check for formatting errors in the morphological feature specification of a token (so you should be careful when entering them at this time, as well as be prepared to use the debugger script ```check_conllu_num.py```). An example error might be forgetting an equal sign separating key from value (```Case=Gen|NumberSing|Gender=Masc```) or forgetting a ```|``` separating two feature pairs. Nor does Inception detect more complicated dependency errors like cyclic graphs (where the dependecy arrows ultimately form an illogical circle). Finding the latter can be an especially painful task, and remains annoying even after you become proficient at reading conllu graphs. A rule of thumb for (basic) UD dependencies is that a token can never have two arrows heading into it (signalling the token is dependent on two different parent nodes), but can have multiple arrows heading out (it is the parent of multiple children). Thus if your proposed syntactic analysis requires two arrows pointing to a single token, it is wrong. 

When you have finished correcting/completing a single text in Inception, you should download it individually in CONLL-U format into an appropriate processing folder. It is possible to download files as a batch in Inception, but I have not found a convenient way to do it for CONLL-U files.

Note that Inception will automatically preface a sentence it exports in conllu form with a commented line displaying the whole sentence. This is a useful feature. Inception will also index the tokens in each sentence the same way, starting from 1. You can use this as a cheap way to 'reindex' a conllu file whose sentences are sequentially indexed but not necessarily starting from 1 (for instance, first sentence is indexed 3,4,5,6,7, second is 8,9,10,11,12,13, third sentence is 55, 56, 57, 58). This will work as long as the sentences are each internally indexed in a consistent way. While Inception will accept such loosely formatted conllu files, spaCy requires that each sentence be sequentially indexed starting from 1.  

## Sentence divisions, reindexing, further corrections

In a suitable text editor (see above), you can break up the conllu file into separate sentences simply by introducing newlines at the appropriate junctures. For instance, if the conllu file starts as

```
# ana šarri bēlīya urdaka Mahde lū šulmu ana šarri ...
1       ana     ana     ADP    PRP      _       2       case    _       _
2       šarri   šarru   NOUN   N        Case=Gen|Number=Sing|Gender=Masc       0     ROOT      _       _
3       bēlīya  bēlu    NOUN   N        ...                                    2     appos     _       _
4       urdaka  urdu    ...    ...      ...                                    2     nsubj     _       _
5       Mahde   mahde   ...    ...
6       lū      lū      ...    ...
7       šulmu   šulmu   ...    ...
8       ana     ana     ...    ...
9       šarri   šarri   ...    ...
...
```

you can introduce an empty line between rows 5 and 6 to signal a sentence break:

```
# ana šarri bēlīya urdaka Mahde lū šulmu ana šarri ...
1       ana     ana     ADP    PRP       _       2       case    _       _
2       šarri   šarru   NOUN   N         Case=Gen|Number=Sing|Gender=Masc       ...     ...
3       bēlīya  bēlu    ...    ...
4       urdaka  urdu    ...    ...
5       Mahde   mahde   ...    ...

6       lū      lū      ...    ...
7       šulmu   šulmu   ...    ...
8       ana     ana     ...    ...
9       šarri   šarri   ...    ...
...
```

However, this format is unacceptable to spaCy (see above), which must convert the conllu file to its own binary format before it can be used for training. When breaking up a single sentence into several new ones, all the new parts save the first must be reindexed. This can be done by using the ```renumber_conllu.py``` script under ```/utils```, whose single command line argument is the conllu file to be processed. Reindexing is a somewhat non-trivial operation since not only do the head indices need to be renumbered, but also the corresponding dependency indices in the seventh column. Because of the way the script works, the input conllu file must have a single empty line and two comment lines (i.e. beginning with #) separating each sentence (save for the first, which only needs two comment lines). Thus in the above example, the conllu file must look something like

```
#
# ana šarri bēlīya urdaka Mahde lū šulmu ana šarri ...
1       ana     ana     ADP    PRP       _       2       case    _       _
2       šarri   šarru   NOUN   N         Case=Gen|Number=Sing|Gender=Masc       ...     ...
3       bēlīya  bēlu    ...    ...
4       urdaka  urdu    ...    ...
5       Mahde   mahde   ...    ...

#
#
6       lū      lū      ...    ...
7       šulmu   šulmu   ...    ...
8       ana     ana     ...    ...
9       šarri   šarri   ...    ...
...
13      ...     ...     ...

#
#
14      ...     ...     ...
...
```

The resulting reindexed conllu file has the same name as the input save with the string 'renumbered' added to the prefix component. 

Besides introducing sentence divisions and reindexing, going over a conllu file coming from Inception also allows you to catch certain errors or rethink certain decisions you made earlier (as I sometimes do). In addition, this is a time you can manually adjust/correct the tokens themselves, which you could not do in Inception. For instance, if you are working with a normalized file from Oracc that contains logograms, sometimes the Oracc editor does not specify the correct case ending for the underlying form (or you may disagree with their choice). There might be an EN normalized as *bēlu* when it should be in the accusative. You can directly change the orthographic form of the token in the conllu file with minimal trouble.

## Converting the conllu file to .spacy format, further bug hunting

Once you have a one or more corrected/completed conllu files you are ready to turn into training data, you need to convert them in spaCy's binary format. The instructions for how to do this using the direct ```convert``` command can be found in [spaCy's documentation](https://spacy.io/api/cli#convert). Here we wish to point out the hierarchy of error tolerance within the pipeline as we have gone through it up till this point:

```
1. Inception
2. spaCy convert
3. spaCy train
```

In terms of how tolerant the process is of errors or abnormalities in the conllu file it accepts, Inception has the highest threshold. We indicated above it does not require sentences be indexed from 1 (only sequentially), nor does it check for syntax errors in the morphological feature specifications of a token or cyclic graphs. It does check for some errors such a dependency index referring to a non-existent token, or fields containing text strings when they should contain integers. If for some reason two columns in the conllu file are not separated by a single tab (which might happen if you use an inappropriate text editor), Inception will also indicate a problem.

After Inception, spaCy's conversion process is less tolerant. It addition to the things Inception rejects, the converter accepts only conllu files where sentences are indexed from 1, and it detects parsing errors in morphological feature strings. However, it does not detech cyclic graphs.

Finally, spaCy will also detect dependency errors in the binary training files during training time. The chief culprit is cyclic graphs. Sometimes the error message will explicitly state there is a cyclic graph. Other times it prints a more cryptic error message relating to the failure of the backpropagation error to converge. To be sure of the nature of the problem, you can use the ```debug data``` command on the binary training files (see [spaCy documentation](https://spacy.io/api/cli#debug) for usage) to check that it is due to cyclic graphs. The ```debug data``` command is also useful for getting statistics on your training data (number of words, average length of sentences, facts about the labels, and other useful warning messages).

Unfortunately, neither the converter nor the training algorithm (not even the ```debug data``` command) tells you exactly where in a given conllu file an error occurs. If you are converting an entire folder of conllu files, the converter will stop for basic syntax errors, but it will not indicate if a file has a cyclic graph. This extremely frustrating fact can cause you to spend inordinate amounts of time scrolling through a large conllu file squinting your eyes or doing a hackish binary search on the files of a directory in order to discover which file the converter or trainer/debugger does not like. 

There are three ways we recommend to avoid this frustration. First, do not annotate too many files in Inception in one batch unless you are confident. Instead, do a small number and then try to convert them individually. Early on, you might want to also train/debug only in small batches, too, until you get better at avoiding the creating of cyclic graphs in your annotations. This conservative approach will save you the trouble of having to fish within a whole folder of files for the problematic individual. Secondly, if you have a conllu file on hand that you know has some syntactic error but not where it is, you can use the ```check_conllu_num.py``` script. This script checks a single conllu file for the following basic errors:


* Whether there are ten fields in each non-commented line
* Whether each field is separated by a tab (and not just spaces)
* Whether the fields for dependency index and dependency type are correctly formatted (instead of e.g. being reversed, which can happen when manually editing the conllu file)

Currently the script does not check that the morphological feature string (field six) is correctly formatted. This might be added later, however.

Let me also note in passing helpful interpretations of a few syntax errors that might come up during conversion and which might not be initially clear:

* ```'Not enough values to unpack'``` = Morphological feature string has isolated feature or value (usually b/c of lack of equal sign), OR the entire string is ```null``` because you forgot to confirm the appropriate string in Inception.
* ```Too many values to unpack``` = Morphological feature string has two feature-value pairs combined (usually b/c of lack of ```|``` separating them)
* ```'Token index does not begin with 0...' ``` = Sentenced not indexed from 1.

All of the above, however, will not catch a cyclic graph. The first defense, as before, is getting better at not creating them in the first place. Beyond this, the best way I have found to identify them is to regularly check via the ```debug data``` command a small batch of training files (say a dozen or less) placed in the location that the model config file expects the training data. This is normally the folders under ```corpus``` specifying which files are for training, development, and testing. If you already know everything else besides the newly added batch of files is 'clean', when you run the debug command and it finds a problem, you can still successively remove files from the suspect batch to find the problematic one fairly quickly. Here, having sequentially numbered data files (such as CDLI's P-numbers), **where you actually annotate the files in sequential order**, can be a massive help. Otherwise, you may have to do a binary search of the whole large directory of files, taking out one half, checking if the error is in the remaining half, etc. to find the error. 

## Engaging the bootstrapping cycle

Once you've successfully converted the corrected/completed this first batch of conllu files to binary format and trained the model on them, you can ```evaluate``` the model's performance on the test files you've held back from the training set and then ```package``` the model as a python package under the name you specified in the ```project.yml``` file (i.e. under ```package_name```). You can run the ```prose_model_annotator_pipe.py```/```verse_model_annotator_pipe.py``` script on the remaining base text files, select another batch of conllu files from the output, perform the corrections on then in Inception, convert the conllu files Inception spits out to spaCy binaries and add them to the existing training set, and finally train the model on the expanded training set.

This is basically all you do until the entire corpus is annotated. Remember a few things, however:

* Augment the attribute ruler file as you go along, adding frequently occuring, complex morphological forms which the parser seems to frequently get wrong (or which you think the parser would never have a chance of getting right).
* In order to avoid typing in a long sequence of feature-value pairs for a morphological feature string, Inception will display a number of possible completions of whatever string you begin typing in the input window, allowing you to autocomplete the entry. Sometimes this is very useful. However, for long strings which go far beyond the display window or which feature so many permutations that a list display is impractical, it can be easier to maintain a hand-generated list in a text file of frequently occuring combinations, which you copy and paste into Inception. Although not the same as autofill, grouping this list according to natural subcategories (masc/fem nouns, preterite/future tense), and organizing and labeling it logically can allow you to navigate it fairly quickly with the search feature. The longer you stay in the business of annotating Akkadian forms, the more likely this latter strategy will prove superior much of the time. For an example of the list I have used, look at ```Inception_annotations.pdf``` under ```/utils```.

## Getting transliterated annotations from normalized ones

The benefit of working with an Oracc corpus is that you can 'fairly' easily get annotations for the transliterated versions of the texts from the normalized transliterations. This is effectively done by taking the normalized tokens in the normalized conllu files (i.e. the forms in column 2) and replacing them with the corresponding transliterated counterparts. Since there are many possible transliterated tokens corresponding to a single normalized token, one cannot simply go through a normalized conllu file and replace each normalized token by its unique transliterated counterpart. Instead, one needs to first generate a set of 'empty' transliterated conllu files like we did for the initial set of normalized conllu files in the section titled **Training the 'empty' model to get the initial set of conllu files**. 

If you are not working with an Oracc corpus with both normalized and transliterated versions of texts, what you need to ensure is that you have completely 'parallel' versions of the normalized and transliterated texts. This means the arrangement of the texts within and among files for one version (say the normalized texts) is parallel to the other (the transliterated texts). For instance, for the SAA volumes, the general scraper script ```ProcessOraccVolume.py``` places each text in its own file labelled with that text's P-number. E.g. SAA 5, 191 = P224650 is in a file called ```P224650.txt``` and has content

```
saao/saa05/P224650
x x x x x x x x x x illaka x x x x x x x ina libbi {KUR}x x x x x x šadê i-x x x x x x kaqqad eššu x x x x x x ina Muṣaṣiri x x x x e-x x x x x x x x
```

The transliterated version of the text is also called ```P224650.txt``` and has content

```
saao/saa05/P224650
x x x x x x x x x x i-la-ka x x x x x x x ina ŠA₃ {KUR}x x x x x x KUR-e i-x x x x x x SAG.DU GIBIL x x x x x x ina {KUR}mu-ṣa-ṣi-ri x x x x e-x x x x x x x x
```

If you have introduced sentence breaks via newlines into the base normalized texts (as happens, for example, when using ```ProcessOraccVerseVolume.py``` and ```ProcessOraccChunksVolume.py```) you need to make sure the base transliterated texts have these same divisions. Furthermore if, during manual annotation, you represented the annotation of a large normalized text by several conllu files each representing a section of the text (as can happen when working on, say, a long royal inscription), you will need to make sure you have initial transliterated conllu files reflecting this same division. The complication of this parallelism requirement between normalized and transliterated texts is one of the reasons producing transliterated annotations from normalized ones is non-trivial.

### Getting the initial transliterated conllu files

To quickly review how the initial set of transliterated conllu files are created, first integrate the helper file ```akt_trans_lemma_lookup_X.json``` (where 'X' is the label of your corpus) into the pre-given transliterated lemma lookup table in the ```/spacy/lang/akt/lookup``` folder using the ```merge_trans_lemma_lookup.py``` script under ```/utils```, remembering the change the name of the lookup table in ```lemmatizer.py``` to reflect the integrated version. We do not need to worry about an attribute file for the transliterated texts at this time because that is useful primarily for annotating the normalized version of the corpus.

After the language class ```akt``` is updated, modify the ```project.yml``` file so that the final packaged model name reflects the addition of the new transliterated corpus. Then 'train' the transliterated model on the pre-given corpus and ```package``` the result. Just as discussed for the bootstrapping cycle of the normalized model, make sure the resulting model folder under ```packages``` has subfolders titled ```remainder```, ```conllu_output_intermediate``` and ```conllu_output_final``` as well as the helper scripts ```verse_model_annotator_pipe.py``` and ```prose_model_annotator_pipe.py```. Place the base transliterated texts in ```remainder``` and run the appropriate annotator script to assign lemmas and pos tags to the texts and output the initial conllu files. 

### Setting up the appropriate directory structure

The subfolder ```merge``` of ```/utils``` has a series of folders corresponding to the normalized Oracc volumes whose annotations have already been converted to transliterated versions. For your new volume or corpus X you need to create a similar set of folders, i.e. ```norm_input_X```, ```trans_input_X```, ```output_intermediate_X```, and ```output_final_X```. Place the fully annotated normalized conllu files for your corpus in ```norm_input_X``` and the newly created 'empty' transliterated conllu files in ```trans_input_X```. If you compare the contents of your folders to the ones for the pre-existing volumes, you will see that for the latter, the normalized and transliterated conllu files are parallel. You also need to put copies of your volume's lemma lookup tables ```ak_norm_lemma_lookup_X.json``` and ```akt_trans_lemma_lookup_X.json``` in the ```merge``` directory, as these will be used by the merge script.

### Running the merge script

The script ```merge_norm_translit_file.py``` takes the parallel series of transliterated and normalized conllu files in ```trans_input_X``` and ```norm_input_X``` and transfers the orthographic tokens of the former into the latter. The volume to be processed is defined by the ```oraccVolume``` variable in the script. The script transfers tokens by going through each pair of files, scanning parallel line by parallel line. If the transliterated and normalized conllu files are not parallel, the transfer process is hopeless. Even when the conllu files are aligned, it occasionally happens that misalignments occur and they need to be handled properly. 

The misalignments are chiefly due to an artifact of how the original Oracc JSON scripts encoding the base texts and their metadata are handled by the scraper scripts. In Oracc, lexical compounds like {LU₂}A-KIN = *mār šipri* have a more complex encoding in the JSON file than single term forms such as *šarru*. Without going into details here, the upshot is that the scraper scripts represent such compounds in the conllu file by repeating the first element of the compound ver multiple rows, with as many rows as their are atomic elements in the compound. For *mār šipri* this would look like, say

```
...
13      ana     ana     ADP     PRP     _       14      case    ...     ...
14      mār     māru    NOUN    N       ...     16      iobj    ...     ...
15      mār     māru    NOUN    N       ...     ...     ...     ...     ...
16      qibīma  qabû    VERB    V       ...     ...     ...     ...     ...
...
```
where at the least, we would like to have row 15 be 

```
15      šipri     šipru    NOUN    N       ...     ...     ...     ...     ...
```

or actually, since we are dealing with a lexical compound

```
...
13      ana     ana     ADP     PRP     _       14      case    ...     ...
14      mār šipri    mār šipri    NOUN    N       ...     15      iobj    ...     ...
15      qibīma  qabû    VERB    V       ...     ...     ...     ...     ...
...
```

This quirk of representation is due to the simplifying assumptions made by the scraper files (inherited from Niek's scripts) about the kind of tokens they are processing, and it holds for the transliterated conllu files as well:

```
# a-na {LU₂}A-KIN qi-bi-ma....
...
13      a-na     ana     ADP     PRP     _       14      case    ...     ...
14      DUMU     māru    NOUN    N       ...     16      iobj    ...     ...
15      DUMU     māru    NOUN    N       ...     ...     ...     ...     ...
16      qi-bi-ma  qabû    VERB    V       ...     ...     ...     ...     ...
...
```

In Oracc, these lexical compounds are represented in transliterated by a 'long dash'. This dash is different from the regular dash and I don't know how to accurately represent here. Instead, I will simply use the regular dash as a substitute. The long dash separates elements in the compound (whether they are represented as a logograph or syllabogram). For instance, *mār šipri* is represented in transliterated as {LU₂}A-KIN. 
In the normalized corpora already processed, many of these lexical compounds have already been encoded in the ```tokenizer_exceptions.json``` file accompanying AkkParser-Norm, and as a result they appear on a single row in the conllu files. Hence the reason for misalignment between the normalized and transliterated conllu file.

Much of the content of ```merge_norm_translit_file.py``` is meant to handle these misalignments, whose subtle variations and complications (including typos in and mismatches between the lemma lookup tables for transliterated and normalized forms) lead to countless headaches in an effort to square everything up. Perhaps much hardship could have been avoided if I had recognized this issue early on in annotating SAA 1, but as it stands currently the scraper scripts are not designed to correctly handle these lexical compounds. Instead, the merge script must adjust for them. Perhaps in the future the scraper scripts can be modified. In the meantime, the merge script does a fairly good job of realigning and reformatting the lexical compounds provided that the file ```tokenizer_exceptions.dict.json``` is updated to reflect all lexical compounds encountered in the corpus and stored in ```tokenizer_exceptions.json```, and that the corpus is tokenized according to the rules of the current language class. When ```merge_norm_translit_file.py``` is run, it produces a log file ```log.txt```, which is just a running record of all the substitutions made from the transliterated conllu files into the normalized ones. The script is designed so that if an attempted transfer of a transliterated token to its normalized counterpart fails (e.g. because they don't have the same lemma), the normalized token remains in place with a special marker '@@@' added to it. If you grep all the resulting conllu files for this symbol and store the results in another log file (as ```log_prob.txt``` illustrates), you can see all the lines where the script failed. If this list is fairly small and looks to be the result of idiosyncratic issues, you can go into the base transliterated/normalized texts or appropriate conllu files to fix things. Otherwise, if it looks like the merge script is getting things consistently wrong, you may want to just count those lines as lost. Or, if you are daring, you can wade into the details of the script to modify the code to account for the error.

Whatever you do, once you are satisfied with these 'hybrid' conllu files you can proceed to train the transliterated model on them (since the transliterated lemmas are already incorporated into the underlying language class). 

## Experimental components

This section briefly discusses a few experimental components in the pipeline for normalized texts.

### Deterministic parser

Aleksi Sahala has developed a deterministic parser for certain dialects of Akkadian called [BabyFST](https://github.com/asahala/BabyFST). Its principle function is to take a normalized form and return a list of possible parses for it.

### Transformer