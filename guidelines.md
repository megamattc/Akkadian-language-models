# Guidelines for running the pipelines associated with models XXX, YYY, and ZZZ, including:

* Setting up the necessary software packages and applications needed for making annotations, text processing, model training, etc.
* General description of the pipeline components for all models
* Walkthrough of the workflow from start to finish, with notes about things to pay attention to, likely problems, and issues I haven't solved or still find troublesome
* Overview of helper scripts and directory structure

How much guidance you need in using the tools and data in this repository depends greatly on your background in Natural Language Processing (NLP), programming skills, intended purpose, and what you already have installed on your machine. You will need to be able to use the terminal and understand basic command line functions, and knowing the basics of Python is also very helpful. With that said, you may very well find shortcuts or better ways to do things than I have, depending on how much effort you want to put into automating certain tasks as opposed to just getting them done by hand quickly. You may also only wish to 'get your feet wet' in terms of seeing how certain tasks are done without needing to do all the work necessary for completing that task (say annotating a whole batch of texts). You can simply skip to the next checkpoint in the pipeline that has a full data set processed for you.

The guidelines are a mix of things in the sense that they reflect both how the original model XXX and its data set were created and how methods have evolved since then. A high-level discussion of XXX and its data can be found in PUBLICATION ABC. Here we are more interested in the nuts and bolts of how to reproduce the pipeline and to document things for posterity. 

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

> If you intend to start annotating your own corpus of texts from Oracc, you can integrate the lemma lookup table from your corpus into that belonging to YYY or ZZZ using the ```merge_norm_lemma_lookup.py``` and ```merge_norm_lemma_lookup.py``` scripts (they differ only in a few small details). If you do this (or if you wish to use your own custom lemma lookup table), you may need to update the name of the resulting lookup table specified in the custom ```lemmatizer.py``` file within the ```ak``` or ```act``` folder. Look for the section of the file consisting of

``` 
def create_lookups(self): 
        lookups = Lookups()
        lookups.add_table("lemma_lookup", self.json_to_dict('lookups/ak_lemma_lookup_1_2_5_15_anzu_barutu.json'))
```  

And change the name of the file to what you need. From the code snippet above, you can see that I chose to label files consisting of data drawn from multiple Oracc projects with names reflecting all the projects in them. This makes for lengthy, awkward file names, but since I am constantly expanding the set of corpora I annotate as well as switching between normalized and transliterated data, this convention allows me to see at a glance what the input dictionaries to a model consist of and hence avoid confusion between model versions. You might prefer a different method to keep track of model content, but note that JSON files do not allow for comments in them. 

The remain folders of the repository should **not** be placed in the spacy installation directory, but instead whatever workspace you use.

### Getting Inception

Inception is an annotator tool created at the Technical University of Darmstadt. We will be using it to do all our annotation work. It is available a Java application at the team's [project homepage](https://inception-project.github.io/). The program uses your default web browser as a user interface and can be launched by clicking on it from the file finder window. The program should probably be placed in your workspace for the annotation project. You can click on the launch icon it creates multiple times to have multiple windows for the program open on your browser. In what follows, it may be convenient to have two windows of Inception open, one for doing the annotations themselves, the other for uploading and deleting files. *Note that you should use only one version of Inception for your annotation work.* The developers make updates to their software, and while you can transfer your work between versions, this requires extra steps and is likely unnecessary an annotation project such as ours. 

### Other tools

You will need a text editor to process the ```conllu``` files (explained below) that Inception and spacy work with, as well as to edit the various helper scripts for names of files and such in case you wish to do your own annotations. I have found it very helpful to use two kinds of text editors: a very basic one for editing the ```consul``` files and another for editing programming scripts or doing more sophisticated text manipulation. Whatever you choose, you should make sure the text editor you use for manipulating ```conllu``` files *does not automatically adjust spacing between words or otherwise encodes what look like tab-separated columns with something other than tabs, e.g. single spaces*. I have found it enormously frustrating to edit ```conllu``` files in certain programs like PyCharm or Aquamacs, as they sometimes adjust word alignment in different lines in ways that wreaks havoc on the ```conllu```tab-separated format. You may not know just by looking at it that the space encoding is wrong, or, even if you enable the appropriate display of space encoding in these programs, your editing may lead them to introduce spaces in ways you don't want (e.g. pressing Tab doesn't actually introduce a single tab). Both Inception and Spacy are finicky when it comes to the format of the ```conllu``` files they accept, and I can attest to amount of aggravation that comes with having to debug a large ```conllu``` file just because of an invisible spacing issue. While it is usually safe to use sophisticated text editors for some amount of ```conllu``` manipulation, I think it is better to use something like the Mac OS's default TextEdit when you want to play it safe. This program does not seem to introduce spacing errors, and pressing Tab always seems to mean just tab.

It will also be helpful to have access to a tool that can debug JSON files and otherwise format them in a pleasing way. I found [this online site](https://jsonformatter.curiousconcept.com/) to be very useful for converting the JSON output from my scripts into the format needed by other parts of my pipeline. While it is almost certainly possible to find ways to make the scripts themselves format their JSON output in the necessary ways, I did not take the time to figure out how to do that in many places within my pipeline (although such might be done eventually). *Note above all that at various points you will need to convert the single quotes in the JSON files produced by the scripts to double quotes so that the file can be input to another script or program*. Using a JSON formatter such as the one linked above will do this as well as make it more readable to the human eye.

## Step 1: Scraping Oracc data, producing basic dictionaries    

  