import regex,re
import subprocess, sys
import json

#Make sure to get rid of header info in eval files of all the dialects!!

#Specify all the dialect dictionaries to convert via the KEYWORD appearing in each file of the form: 2020-akk-x-KEYWORD.eval
dialects = ["oldbab","stdbab","neobab","ltebab","mbperi","neoass"]



#dictionary for converting oracc fine-pos to ud coarse-pos

posLabelDic = {"AN":"PROPN","CN":"PROPN","DN":"PROPN","EN":"PROPN","FN":"PROPN","GN":"PROPN",
               "LN":"PROPN","MN":"PROPN","ON":"PROPN","PN":"PROPN","QN":"PROPN","RN":"PROPN",
               "SN":"PROPN","TN":"PROPN","YN":"PROPN","WN":"PROPN","AJ":"ADJ","AV":"ADV","NU":"NUM",
               "CNJ":"CONJ","DET":"DET","J":"INTJ","N":"NOUN","PP":"PRON","V":"VERB","IP":"PRON","DP":"DET",
               "MOD":"PART","PRP":"ADP","QP":"PRON","RP":"PRON","REL":"PRON","SBJ":"SCONJ","XP":"PRON",
               "u":"X","n":"NUM","X":"X","NN":"NN"}

#Dictionary that basically assigns Oracc proper noun types to noun category, for use in determining how to parse morph string below
coarseSyntaxDict = {"AN":"NOUN","CN":"NOUN","DN":"NOUN","EN":"NOUN","FN":"NOUN","GN":"NOUN",
               "LN":"NOUN","MN":"NOUN","ON":"NOUN","PN":"NOUN","QN":"NOUN","RN":"NOUN",
               "SN":"NOUN","TN":"NOUN","YN":"NOUN","WN":"NOUN","AJ":"ADJ","AV":"ADV","NU":"NUM",
               "CNJ":"CONJ","DET":"DET","J":"INTJ","N":"NOUN","PP":"PRON","V":"VERB","IP":"PRON","DP":"DET",
               "MOD":"PART","PRP":"ADP","QP":"PRON","RP":"PRON","REL":"PRON","SBJ":"SCONJ","XP":"PRON",
               "u":"X","n":"NUM","X":"X","NN":"NN","NOUN":"NOUN","ADV":"ADV","PROPN":"NOUN","CONJ":"CONJ"}


verbStemList = ['G','Gt','Gtn','D','Dt','Dtn','Dt(n)''N','Nt','Ntn','Nt(n)','Š','Št','Štn','Št(n)','ŠD','R'] #Note presence of labels with options like Dt(n) which will have to be handled latter
verbTenseFormList = ['Prt','Prs','Prf','Stat','Inf','Vadj','Prec','Imp'] #Gather together labels for both tense and VerbForm in spacy. Calling this list 'tense' is only partially accurate. Note that Vadj requires us to put the form under Adj
verbTenseFormDict = {"Prt":"Past","Prs":"Pres","Prf":"Perf","":"XXX","Imp":"Imp","Stat":"Stat","Inf":"Inf","Prec":"Prec"} #We only need handle these three
caseList = ['Nom','Acc','Gen','AnyCase', 'Dat','Obl'] #Note AnyCase, Dative - some of these can refer to morpheme features to infinitives, nouns, verbal suffixes

#For now, Dative case is ignored (i.e. assigned empty string) even though in OB dative suffixes are different from accusative ones
#Note also that sometimes in BabyFST a nominal form may not have case assigned to it, hence the XXX label
caseDict = {'Nom':'Nom','Gen':'Gen','Acc':'Acc','Dat':'','AnyCase':'','Obl':'','':'XXX'}
perList = ['1Sg','2Sg','3Sg','1Pl','2Pl','3Pl']
numList = ['Sg','Pl']
numDict = {'Sg':'Sing','Pl':'Plur','':'XXX'} #Conversion dict between BabyFST terms and spacy model's
genList = ['Masc','Fem']
consList = ['Cons']
consDict = {'Cons':'Yes','':'No'} #Here, an empty string in BabyFST shall be taken as negative feature value in spacy model, even though right now this system is not implemented (instead, it is mostly existence-based)
boundList = ['Construct']
boundDict = {'Construct':'Bound','':'Free'}
subjList = ['Subjunct']
subjDict = {'Subjunct':'Yes','':'No'}
ventList = ['Vent']
ventDict = {'Vent':'Yes','':'No'}
PossList = ['Poss']

split_regex_str = re.compile(r'(?<=\w)\+(?=[A-Za-z]+=)') #Right now we use expanded regex module instead of regex to allow variable positive lookbehind, even though we currently don't use it

#Helper function that returns first element of intersection of two lists if the set is not empty, otherwise empty string
def get_first(feature_list: list, parse_list: list) -> str:
    intersect_list = list(set(feature_list).intersection(parse_list))
    if len(intersect_list) > 0:
        return intersect_list[0]
    else:
        return ""

#Helper function that merges a parse string into a list of parse strings. If the set of features in two strings match, the strings are considered equivalent
def merge_feature_into_list(parse_str: str, feature_list: list[str]):
    parse_str_set = set(parse_str.split("|"))
    match = False
    for feature_str in feature_list:
        feature_str_set = set(feature_str.split("|"))
        if parse_str_set == feature_str_set:
            match = True

    #If no match, add parse string
    if match == False:
        feature_list.append(parse_str)



#Function to merge dicitonary {token:parse string} into dictionary whose keys are tokens and the values a list of possible parse strings for the tokens
def merge_feature_into_dict(entry: dict, parse_dict: dict):
    key = list(entry.keys())[0]
    value = entry[key]

    if key not in parse_dict.keys():
        parse_dict.update({key:[value]})
    else:
        feature_list = parse_dict[key]
        merge_feature_into_list(value,feature_list)

#Converts feature dictionary from one whose values are strings to one whose values are dictionaries. It's assumed the strings are defined in a way this will not lead to contradictions
def convert_dictionary(feature_dict:dict)->dict:
    output_dict = {}
    keys = feature_dict.keys()
    for key in keys:
        value_list = feature_dict[key]
        list_for_key = []

        for parse_str in value_list:
            parse_value_dict = {}
            parse_str_array = parse_str.split("|")

            for pair_str in parse_str_array:
                #Occasionally a null gets stored in the dictionary, for some reason. I currently don't know why
                if "=" not in pair_str:
                    continue
                else:
                    feature = pair_str.split("=")[0]
                    value = pair_str.split("=")[1]
                    parse_value_dict.update({feature:value})

            list_for_key.append(parse_value_dict)

        output_dict.update({key:list_for_key})

    return output_dict

#Converts BabyFST person strings (1sg, 3pl, etc.) to spacy model feature strings, depending on whether the represent verb or nominal form
def convert_person(person: str, form_type: str)-> str:

    output = "XXX"

    if form_type == "noun":

        if person == "1Sg":
            output = "PossSuffGen=Com|PossSuffPer=1|PossSuffNum=Sing"
        if person == "2Sg":
            output = "PossSuffPer=2|PossSuffNum=Sing"
        if person == "3Sg":
            output = "PossSuffPer=3|PossSuffNum=Sing"
        if person == "1Pl":
            output = "PossSuffGen=Com|PossSuffPer=1|PossSuffNum=Plur"
        if person == "2Pl":
            output = "PossSuffPer=2|PossSuffNum=Plur"
        if person == "3Pl":
            output = "PossSuffPer=3|PossSuffNum=Plur"

    #For now, we don't distinguish acc and dat suffixes
    elif form_type == "suff":

        if person == "1Sg":
            output = "VerbSuffGen=Com|VerbSuffPer=1|VerbSuffNum=Sing"
        if person == "2Sg":
            output = "VerbSuffPer=2|VerbSuffNum=Sing"
        if person == "3Sg":
            output = "VerbSuffPer=3|VerbSuffNum=Sing"
        if person == "1Pl":
            output = "VerbSuffGen=Com|VerbSuffPer=1|VerbSuffNum=Plur"
        if person == "2Pl":
            output = "VerbSuffPer=2|VerbSuffNum=Plur"
        if person == "3Pl":
            output = "VerbSuffPer=3|VerbSuffNum=Plur"

        # For now, we don't distinguish acc and dat suffixes
    elif form_type == "pred":

        if person == "1Sg":
            output = "PredSuffGen=Com|PredSuffPer=1|PredSuffNum=Sing"
        if person == "2Sg":
            output = "PredSuffPer=2|PredSuffNum=Sing"
        if person == "3Sg":
            output = "PredSuffPer=3|PredSuffNum=Sing"
        if person == "1Pl":
            output = "PredSuffGen=Com|PredSuffPer=1|PredSuffNum=Plur"
        if person == "2Pl":
            output = "PredSuffPer=2|PredSuffNum=Plur"
        if person == "3Pl":
            output = "PredSuffPer=3|PredSuffNum=Plur"

    elif form_type == "verb":

        if person == "1Sg":
            output = "Gender=Com|Person=1|Number=Sing"
        if person == "2Sg":
            output = "Person=2|Number=Sing"
        if person == "3Sg":
            output = "Person=3|Number=Sing"
        if person == "1Pl":
            output = "Gender=Com|Person=1|Number=Plur"
        if person == "2Pl":
            output = "Person=2|Number=Plur"
        if person == "3Pl":
            output = "Person=3|Number=Plur"

    return output

#Combine feature string (e.g. "Gender=") and value string (e.g. "Fem"). Sometimes value is empty string or is marked for deletion ("XXX").
# In those cases, empty string is returned. Note also that the feature input is assumed to end in '='
def form_pair(feature: str, value: str)-> str:
    output = ""

    if value == "" or value == "XXX" or value == None:
        return output
    else:
        output = feature+value
        return output


#Function to convert BabyFST parse string to ud/ak parse string
def convert_parse(parse_str: str) -> str:
    # The BabyFST parse notion is awkward to convert to spacy model's, and don't even know if it is completely consistent. First split up according to '=' groups

    parseArray = re.split(split_regex_str, parse_str) #Split on '+' according to above regex pattern
    #print("parseArray")
    #print(parseArray)
    parse_str_array = regex.split(r'[+=]', parse_str) #This splits up the parse_str on +/=

    lemma_data = parseArray[0]  # Get leftmost element, which contains lemma, finepos, plus other features

    ud_parse = "" #String to be returned


    #Get finepos for categorization of how to handle parse string
    #lemma_data_array = lemma_data.split("+")
    finepos = parse_str_array[1] #Get string to right of initial item, which is the lemma

    coarsepos = ""
    synCat = "" #NOUN, VERB, PRON, etc.

    #Try to assign finepos, coarsepos, otherwise leave as empty strings
    if finepos in posLabelDic.keys():
        coarsepos = posLabelDic[finepos]
        synCat = coarseSyntaxDict[finepos]


    #If coarsepos is a PROPN there should be no split in parse string
    if coarsepos == "PROPN":
        propn_array = lemma_data.split("+") #We already have lemma, finepos
        #Sometimes a PN doesn't have case assigned to it, so we have to check
        if len(propn_array) > 2:
            nounCaseLabel = propn_array[2] #Only have case left (BabyFST does not note gender or number of PN's)
        else:
            nounCaseLabel = "XXX" #Assign XXX so later we can delete the pair

        ud_parse = "POS=PROPN|"+form_pair("Case=",nounCaseLabel) #We add POS tage at beginning for identification purposes later



    #For verbs, there are many groups in parse string
    if synCat == 'VERB':

        #If we have an infinitive, there is only one = group, which is lemma_data. So split on +.
        if "Inf" in parse_str:
            #Parse just lemma_data
            lemma_data_array = lemma_data.split("+")

            # Get common element between verbStemList and parseArray if it exists, and if not, assign empty string
            verbStemLabel = get_first(verbStemList, lemma_data_array)
            verbInfBoundLabel = get_first(boundList,lemma_data_array)  # 'Construct' if infinitive in bound form, nothing otherwise
            verbConsLabel = get_first(consList,lemma_data_array)  # I believe this is for -ma suffix? for both finite, infinitive
            verbCaseLabel = get_first(caseList,lemma_data_array)  # Case for infinitive, or, for finitive verbs the presence of an accusative suffix (whereby person, gender labels refer to suffix, not verb stem)

            verbGenLabel = "Masc" #By assumption

            verbPerLabel = "" # Person+num for finite verb (1Sg, 2Sg, 1Pl. etc.), meaning person+num of verb OR person+num of dative/accusative
            verbGenLabel = "" # Gender, either for verb or verbal suffix, of infinitive or finitive verb

            #Also need to check for possessive suffixes
            if "Poss" in parse_str:
                poss_str = parse_str.split("Poss")[1] #We assume Poss substr is at end of string, and only one Poss label appears
                poss_str_array = regex.split(r'[+=]', poss_str)
                verbPerLabel = get_first(perList,poss_str_array)
                verbGenLabel = get_first(genList,poss_str_array)




            #Now assemble into output string

            verbStemPair = form_pair('VerbStem=',verbStemLabel)
            verbFormPair = 'VerbForm=Inf'  # By assumption
            nounBoundPair = form_pair('NounBase=',boundDict[verbInfBoundLabel])
            verbFocusPair = form_pair('Focus=',consDict[verbConsLabel])
            verbNumPair = 'Number=Sing'  # Inf is singular
            nounGenPair = 'Gender=Masc'  # Infinitives are masculine


            # No matter if inf case label is nom or gen or acc, it can't refer to any verbal suffix (b/c possessive suff on inf would be described by Poss)

            nounCasePair = form_pair('Case=',caseDict[verbCaseLabel])

            verbPerPair = convert_person(verbPerLabel,"noun")
            verbGenPair = form_pair('PossSuffGen=',verbGenLabel)

            #print([verbStemPair,verbFormPair,nounBoundPair,verbFocusPair,verbNumPair,nounGenPair,nounCasePair,verbPerPair,verbGenPair])

            ud_parse = "|".join(["POS=VERB",verbStemPair,verbFormPair,nounBoundPair,verbFocusPair,verbNumPair,nounGenPair,nounCasePair,verbPerPair,verbGenPair])
            #print("ud_parse")
            #print(ud_parse)
            #Get rid of double || and initial, final |

            ud_parse = ud_parse.replace("||","|")
            ud_parse = ud_parse.rstrip("|")
            ud_parse = ud_parse.lstrip("|")

        #If V and Vadj are in parse_str, I think this is one of BabyFST's way of encoding statives? But then what about the Stat label?

        elif "Vadj" in parse_str:

            lemma_data_array = lemma_data.split("+")

            # If there are case and gender features on it, then it is an adjective

            feature_set = {"Sg", "Pl", "Nom", "Acc", "Gen"}
            if feature_set.intersection(lemma_data_array):

                adjGenLabel = get_first(genList,lemma_data_array) #For some reason these forms are not specified for gender in BabyFST
                adjNumLabel = get_first(numList,lemma_data_array)
                adjCaseLabel = get_first(caseList,lemma_data_array)

                adjGenPair = form_pair("Gender=",adjGenLabel)
                adjNumPair = form_pair("Number=",numDict[adjNumLabel])
                adjCasePair = form_pair("Case=",caseDict[adjCaseLabel])

                #Still check for -ma
                verbConsLabel = get_first(consList, parse_str.split("+"))

                verbConsPair = form_pair("Focus=", consDict[verbConsLabel])

                ud_parse = "|".join(["POS=ADJ",adjGenPair,adjNumPair,adjCasePair,verbConsPair])

                ud_parse = ud_parse.replace("XXX", "")
                ud_parse = re.sub(r'\|{2,}', "|", ud_parse)
                ud_parse = ud_parse.rstrip("|")
                ud_parse = ud_parse.lstrip("|")

                #print("Line")
                #print(line)
                #print("ud_parse")
                #print(ud_parse)

            #Otherwise the form. which is still Vadj, is a stative, I guess
            else:

                verbStemLabel = get_first(verbStemList, lemma_data_array)
                verbStemPair = form_pair("VerbStem=", verbStemLabel)
                verbConsLabel = get_first(consList, parse_str.split("+"))
                verbConsPair = form_pair("Focus=", consDict[verbConsLabel])

                verbTenseFormPair = "VerbForm=Stat" #We're just going to call these statives, even though if they were, they're all 3.m.s.
                verbPerPair = "Person=3"
                verbNumPair = "Number=Sing"
                verbGenPair = "Gender=Masc"

                ud_parse = "|".join(["POS=VERB",verbStemPair, verbTenseFormPair, verbPerPair, verbNumPair,verbGenPair,verbConsPair])

                ud_parse = ud_parse.replace("XXX", "")
                ud_parse = re.sub(r'\|{2,}', "|", ud_parse)
                ud_parse = ud_parse.rstrip("|")
                ud_parse = ud_parse.lstrip("|")

                #print("Line")
                #print(line)
                #print("ud_parse")
                #print(ud_parse)


        #Else we have some other finite form
        else:
            lemma_data_array = lemma_data.split("+")
            verbStemLabel = get_first(verbStemList, lemma_data_array)
            verbStemPair = form_pair("VerbStem=",verbStemLabel)
            #print("In Verb Fin")
            #print(line)
            #print("VerbStemPair")
            #print(verbStemPair)
            verbConsLabel = get_first(consList,parse_str.split("+"))  # I believe this is for -ma suffix? We can just break up parse_str by +
            verbConsPair = form_pair("Focus=",consDict[verbConsLabel])

            finiteFormList = ['Prs','Prt','Prf','Prec','Imp'] #Only the verb forms that aren't infinitive, stative (or verbal adjective), since we took care of those above

            verbTenseFormLabel = get_first(finiteFormList,parse_str_array)
            verbTenseFormPair = form_pair("Tense=",verbTenseFormDict[verbTenseFormLabel])
            verbStemPerLabel = ""
            verbStemPerPair = ""
            verbStemGenLabel = ""
            verbStemGenPair = ""


            match = re.search('(?<=(Prt|Prs|Prf|rec|Imp|tat)=)([1-3](Sg|Pl))(=){0,1}(Masc|Fem){0,1}',parse_str)  # Right now just assume there is one suffix. Later we will have to change this

            if match:
                verbStemPerLabel = match.group(2)
                verbStemGenLabel = match.group(5)

                verbStemPerPair = convert_person(verbStemPerLabel,"verb")
                verbStemGenPair = form_pair("Gender=",verbStemGenLabel)


            verbSuffPerLabel = ""

            match = re.search('(?<=(Acc|Dat)=)([1-3](Sg|Pl))' ,parse_str) #Right now just assume there is one suffix. Later we will have to change this

            if match:
                verbSuffPerLabel = match.group(2)

            #print("parse_str")
            #print(parse_str)
            #print("verbSuffPerLabel")
            #print(verbSuffPerLabel)
            verbSuffPerPair = convert_person(verbSuffPerLabel, "suff")

            verbSuffGenLabel = ""

            match = re.search('(?<=(Acc|Dat)=[1-3](Sg|Pl)=)(Masc|Fem)' ,parse_str)
            if match:
                verbSuffGenLabel = match.group(3)

            verbSuffGenPair = form_pair('VerbSuffGen=', verbSuffGenLabel)

            verbVentPair = ""
            if "Vent" in parse_str:
                verbVentPair = "Ventive=Yes"
            else:
                verbVentPair = "Ventive=No"

            verbSubjPair = ""

            if "Subjunct" in parse_str:
                verbSubjPair = "Subordinative=Yes" #Note change in terminology
            else:
                verbSubjPair = "Subordinative=No"

            ud_parse = "|".join(["POS=VERB",verbStemPair,verbTenseFormPair,verbStemPerPair,verbStemGenPair,verbVentPair,verbSubjPair,verbSuffPerPair,verbSuffGenPair,verbConsPair])

            ud_parse = ud_parse.replace("XXX","")
            ud_parse = re.sub(r'\|{2,}',"|",ud_parse)
            ud_parse = ud_parse.rstrip("|")
            ud_parse = ud_parse.lstrip("|")

            print("Line")
            print(parse_str)
            print("ud_parse")
            print(ud_parse)

    #Now for nouns
    if synCat == "NOUN":

        nounBoundLabel = ""
        nounGenLabel = ""
        nounConsLabel = ""
        nounNumLabel = ""
        nounCaseLabel = ""

        match = re.search(r"(?<=\+N=)(Masc|Fem)(\+(Sg|Pl))(\+(Nom|Acc|Gen|Obl|AnyCase)){0,1}", parse_str)
        if match:
            #print(match.groups())
            nounGenLabel = match.group(1)
            #print("nounGenLabel")
            #print(nounGenLabel)
            nounNumLabel = match.group(3)
            nounCaseLabel = match.group(5)

        nounGenPair = form_pair("Gender=",nounGenLabel)
        nounNumPair = form_pair("Number=", numDict[nounNumLabel])
        nounCasePair = form_pair("Case=",nounCaseLabel)

        nounBoundPair = ""

        if "Constr" in parse_str:
            nounBoundPair = "NounBase=Bound"
        else:
            nounBoundPair = "NounBase=Free"

        nounConsPair = ""
        if re.search(r'Cons$',parse_str):
            nounConsPair = "Focus=Yes"
        else:
            nounConsPair = "Focus=No"

        nounSuffPerLabel = ""
        nounSuffGenLabel = ""

        if "Poss" in parse_str:
            poss_str = parse_str.split("Poss")[1]  # We assume Poss substr is at end of string, and only one Poss label appears
            poss_str_array = regex.split(r'[+=]', poss_str)
            nounSuffPerLabel = get_first(perList, poss_str_array)
            nounSuffGenLabel = get_first(genList, poss_str_array)

        nounSuffPerPair = convert_person(nounSuffPerLabel,"noun")
        nounSuffGenPair = form_pair("PossSuffGen=", nounSuffGenLabel)

        #Now we need to check for predicative suffixes like -āku, -āti, etc. We assume they are marked in BabyFST by things like ^Poss=2Sg=Fem

        nounPredPerLabel = ""
        nounPredGenLabel = ""

        match = re.search(r"\+(Sg|Pl)=([1-3](Sg|Pl))(=){0,1}(Masc|Fem){0,1}[+]{0,1}", parse_str)
        if match:
            nounPredPerLabel = match.group(2)
            nounPredGenLabel = match.group(5)

        nounPredPerPair = convert_person(nounPredPerLabel, "pred")
        nounPredGenPair = form_pair("PredSuffGen=", nounPredGenLabel)

        ud_parse = "|".join(["POS=NOUN",nounGenPair, nounNumPair, nounCasePair, nounBoundPair, nounSuffPerPair, nounSuffGenPair,nounPredPerPair,nounPredGenPair,nounConsPair])


        #Clean up errors in string

        ud_parse = ud_parse.replace("XXX", "")
        ud_parse = ud_parse.replace("Case=AnyCase", "")
        ud_parse = ud_parse.replace("Case=Obl", "")
        ud_parse = re.sub(r'\|{2,}', "|", ud_parse)
        ud_parse = ud_parse.rstrip("|")
        ud_parse = ud_parse.lstrip("|")

        #print("Line")
        #print(line)
        #print("array")
        #print([nounGenPair, nounNumPair, nounCasePair, nounBoundPair, nounSuffPerPair, nounSuffGenPair,nounPredPerPair,nounPredGenPair,nounConsPair])
        #print("ud_parse")
        #print(ud_parse)
        #print("---------------")

    if synCat == "ADJ":

        adjGenLabel = ""
        adjConsLabel = ""
        adjNumLabel = ""
        adjCaseLabel = ""

        match = re.search(r"(?<=\+AJ=)(Masc|Fem)(\+(Sg|Pl))(\+(Nom|Acc|Gen|Obl|AnyCase)){0,1}", parse_str)
        if match:
            #print(match.groups())
            adjGenLabel = match.group(1)
            #print("adjGenLabel")
            #print(adjGenLabel)
            adjNumLabel = match.group(3)
            adjCaseLabel = match.group(5)

        adjGenPair = form_pair("Gender=", adjGenLabel)
        adjNumPair = form_pair("Number=", numDict[adjNumLabel])
        adjCasePair = form_pair("Case=", adjCaseLabel)

        adjBoundPair = ""

        if "Constr" in parse_str:
            adjBoundPair = "NounBase=Bound"
        else:
            adjBoundPair = "NounBase=Free"

        adjConsPair = ""
        if re.search(r'Cons$', parse_str):
            adjConsPair = "Focus=Yes"
        else:
            adjConsPair = "Focus=No"

        adjPredPerLabel= ""
        adjPredGenLabel = ""

        match = re.search(r"\+(Sg|Pl)=([1-3](Sg|Pl))(=){0,1}(Masc|Fem){0,1}\w", parse_str)
        if match:
            adjPredPerLabel = match.group(2)
            adjPredGenLabel = match.group(5)

        adjPredPerPair = convert_person(adjPredPerLabel, "pred")
        adjPredGenPair = form_pair("PredSuffGen=", adjPredGenLabel)

        ud_parse = "|".join(["POS=ADJ",adjGenPair, adjNumPair, adjCasePair, adjBoundPair,adjPredPerPair,adjPredGenPair,adjConsPair])


        # Clean up errors in string, including getting rid of Case=AnyCase

        ud_parse = ud_parse.replace("XXX", "")
        ud_parse = ud_parse.replace("Case=AnyCase", "")
        ud_parse = ud_parse.replace("Case=Obl", "")
        ud_parse = re.sub(r'\|{2,}', "|", ud_parse)
        ud_parse = ud_parse.rstrip("|")
        ud_parse = ud_parse.lstrip("|")

        #print("Line")
        #print(line)
        #print("array")
        #print([adjGenPair, adjNumPair, adjCasePair, adjBoundPair,adjPredPerPair,adjPredGenPair,adjConsPair])

        #print("ud_parse")
        #print(ud_parse)
        #print("---------------")




    return ud_parse

#Convert entire eval file to json file that gets printed out to a file
def convert_eval_to_json(evalFile,outputFile):
    lines = evalFile.readlines()

    lemma_str = fine_pos_str = coarse_pos_str = ""

    # List whose elements are dictionaries whose keys are forms and whose values the various +parses from eval list
    parse_list = []

    for index in range(0, len(lines)):
        line = lines[index]
        lineArray = line.split()

        coarsepos = ""

        # If we have a header line or empty line, skip
        if '##' in line or line.isspace():
            continue

        # If our line is not a header or empty line, it is a form line, whose fourth item has +/-. We want all the lines
        elif lineArray[3] in ["+","-"]:

            # print("Line")
            # print(line)

            form = lineArray[0]
            parse_str = lineArray[1]

            ud_morph = convert_parse(parse_str)

            # print("ud_morph")
            # print(ud_morph)

            # Add form and parse to list
            parse_list.append({form: ud_morph})

    # Now collapse entries in a dictionary whose values represent the possible parses of forms in string form

    parse_str_dict = {}

    for entry in parse_list:
        merge_feature_into_dict(entry, parse_str_dict)

    # Convert this dictionary into one whose values are in dictionary form

    parse_dict = convert_dictionary(parse_str_dict)

    # Print output

    print(parse_dict, file=outputFile)

#Create all the dialect filenames in a dictionary
dialect_filenames_dict = {dialect:"2020-akk-x-"+dialect+".eval" for dialect in dialects}
output_filenames_dict = {dialect:"eval_dict_"+dialect+".json" for dialect in dialects}
output2_filenames_dict = {dialect:"eval_dict_"+dialect+"_2.json" for dialect in dialects}
#Now call the convert_to_json function for all the dialects

for dialect in dialects:


    #Get the eval file
    evalFile = open(dialect_filenames_dict[dialect],'r')

    #Output file in json format whose values are dictionaries
    outputFile = open(output_filenames_dict[dialect],'w')

    convert_eval_to_json(evalFile,outputFile)

    #Workaround for converting the single quotes in the resulting json file to double quotes. There is probably a better way to do this

    #subprocess.run(f'sed -i s"/\'/"/g" {output_filenames_dict[dialect]} > {output2_filenames_dict[dialect]}',shell=True)
    subprocess.run(f'source change_quotes.sh {output_filenames_dict[dialect]} {output2_filenames_dict[dialect]}',shell=True)
    #Rename files

    subprocess.run(f'mv {output2_filenames_dict[dialect]} {output_filenames_dict[dialect]}',shell=True)



#Now merge all dictionary files together as well

dictionaries = {dialect:json.load(open(output_filenames_dict[dialect])) for dialect in dialects}

general_dict = {dialect:dictionaries[dialect] for dialect in dialects}


#general_dict = {"ltebab": lte_dict, "stdbab": std_dict, "oldbab": old_dict, "mbperi": mbperi_dict, "neobab": neo_dict}

general_dict_name = "eval_dict_general.json"
temp_dict_name = "temp_"+general_dict_name

output_file = open(general_dict_name, 'w')
print(general_dict, file=output_file)

#Change quotes on the general dictionary

subprocess.run(f'source change_quotes.sh {general_dict_name} {temp_dict_name}',shell=True)

subprocess.run(f'mv {temp_dict_name} {general_dict_name}',shell=True)



















