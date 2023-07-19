import spacy
import pandas as pd
import os, glob, sys
import re
import spacy_conll
import json
from fnmatch import fnmatch

oraccVolume = "saa02"

#File and dictionary for transliteration-norm json
transNormDictFileName = "akt_trans_lemma_lookup_"+oraccVolume+".json"
transNormDictFile = open(transNormDictFileName, 'r')
transNormDict = json.load(transNormDictFile)

#File and dictionary for norm-lemma json
normLemmaDictFileName = "ak_norm_lemma_lookup_"+oraccVolume+".json"
normLemmaDictFile = open(normLemmaDictFileName, 'r')
normLemmaDict = json.load(normLemmaDictFile)

#File and dictionary for tokenizer exceptions (i.e. compound forms,,often expressed as compound logograms)
tokExceptFileName = 'tokenizer_exceptions_dict.json'
tokExceptFile = open('tokenizer_exceptions_dict.json', 'r')
tokExceptDict = json.load(tokExceptFile)

#Input, output paths. These must exist before running the script
normInputPath = "./norm_input_"+oraccVolume+"/"
transInputPath = "./trans_input_"+oraccVolume+"/"
outputPathIntermediate = "./output_intermediate_"+oraccVolume+"/"
outputPathFinal = "./output_final_"+oraccVolume+"/"


#Dictionary of lemma pairs from Assyrian to Babylonian, and
#other oddities like appearance of ša₂ as broken form (whose lemma should be ša but is in fact ša₂ in norm file), used as last resort in checking forms
dialectConversionDict = {"išti":"ištu","ištu":"išti","qabli":"qabsi","bītu":"bētu","bīt":"bēt","ša₂":"ša",
                         "la":"lā","a-ki":"akī","lu":"lū","kur":"Mat","mūraku":"arku",
                         "kī":"kî","ū":"u","issar":"Ištar","limmu":"līmu","pīhātu":"pāhātu","amātu":"awātu"}

#In above, note how we have lowercase issar (not Issar)

#Dictionary of preposition contraction forms
prepContractionDict = {"i-pa-an":"ina pān","id-da-a-te":"ina dāte","i-da-tu₂-u-a":"ina datūwa","i-da-tu-šu₂-nu":"ina dātuššunu","i-da-tu₂-u-šu":"ina dātūšu","i-da-tu-šu":"ina dātuššu",
                       "i-da-a-te-šu₂-nu":"ina dātešunu","i-da-at":"ina dāt","id-da-a-te":"ina dāt","i-da-tuk-ka":"ina dātukka",
                       "i-ti-ma-li":"ina timāli","i-ša₂-šu-me":"ina šalsūmi","a-UGU":"ana muhhi","a-ki-ma":"ana kīma","iš-šad-dag-diš":"ina šaddaqdiš","a-ṭe₃-mu":"ana ṭēmu",
                       "i-pa-na-tu₂-šu₂-nu":"ina pānātuššunu","i-ma-ti":"ina mati","i-qa-an-ni":"ina qanni","i-ši-a-ri":"ina šiāri","i-ši-ia-ri":"ina šiāri","i-ṭe₃-en":"ina ṭēn",
                       "ib-E₂":"ina bēt","id-da-at":"ina dāt","ih-ha-ra-me-ma":"ina harammēma","im-ma-at":"ina mat","im-ma-te":"ina mate","ip-pi-it-ti":"ina pitti",
                       "a-HA.LA-šu₂":"ana zittīšu","a-bal-duk-ka":"ana baldukka","a-bal-la-tuk-ka":"ana ballātukka","im-ma-ti":"ina mati","am-ma-la":"ana mala","am-mi₃-ni":"ana mīni","na-am-mal":"ana mal"
}

#Helper function to check and repair form that has open bracket on left
# as a result of bad tokenization by spacy, which peels of '{' from determiners in transliterations or broken forms

def correct_bracket(token : str):

    #First count number of { and } in token. If equal, we'll assume we don't need to add anything
    if token.count("{") == token.count("}"):
        return token

    #If form has '}' in it and it doesn't already start with {, then we assume the original initial character was '{', and add it
    elif "}" in token and token[0] != "{":
        token = "{" + token

    #Assuming brackets are still not balanced, check for determiners at end of word with missing bracket
    if token.count("{") != token.count("}"):
        if "{" in token and token[-1] != "}":
            token = token + "}"

    #Now check for lopped off ) (e.g. {d}1(ŠAR'U ), assuming brackets {,} are finally balanced
    if token.count("{") == token.count("}"):
        if "(" in token and token[-1] != ")":
            token = token + ")"
            print("Added )")

    return token

#Helper function to see if two elements belong to preposition contraction like i-pa-an = ina pān
def in_prep_contraction(normForm : str,transForm : str):
    keys = prepContractionDict.keys()
    if transForm in keys:
        if normForm in prepContractionDict[transForm]:
            print("Common prep contraction: " + prepContractionDict[transForm])
            return True
    else:
        return False

#Helper function that strips off determiner, if any
def strip_determiner(token : str):
    token = re.sub("\{LU₂\}", "", token) #Hack for now to handle case with subscripts
    
    token = re.sub("\{[A-Z-a-z0-9]+\}","", token)

    return token

#A helper function which checks if element is represented within compound in the sense that the element's lemma is the same as a lemma of one of the components of the compound, as determined by lemmaDict
#The function returns a string specifying if the containment is as strict element (e.g. ša i ša-rēši)
#or if element equals compound (which we need to consider for those transliteration forms with multiple components but which appear only once in the transliteration conllu file, like {LU₂}ša₂-E₂-02-e -> ša-bēti-šanie
def in_compound_form(element : str, compound : str, lemmaDict : dict):

    #First check if element is in lemmaDict, and if it is, get its lemma.
    if element in lemmaDict.keys():

        elementLemma = lemmaDict[element]

        itemList = re.split(r"[\s-]", compound)

        for item in itemList:
            # Many of the arguments that get passed in as compound are proper names (which were initially put in the tokenizer_exception file
            # because I had not yet told spacy not to tokenize on - (and hence simply put the PN's in the list of tokenizer exceptions as a block))
            # Hence need to check first if an item of the compound is actually in lemmaDict (since the components of many names, like Ṭab in Ṭab-Aššur, are not in lemmaDict)
            if (item in lemmaDict.keys()) and (elementLemma.casefold() == lemmaDict[item].casefold()):
                return "element"
            # It may also be the case that elementLemma actually == compound, if
            elif elementLemma.casefold() == compound.casefold():
                return "entire"

    #This case is meant for instancs like element = ṣāb šarri, compound = ṣāb šarri
    elif element.casefold() == compound.casefold():
        return "entire"

    #Otherwise
    else:
        return ""


#Checks if normalized form1 belongs to the compound represented by the transliteration form2 (which is usually compound logographic).
#The transliteration-lemma dictionaries I created are not 1-1 for these compound forms, since (as I realized only later), the conllu output that Niek's oracc scripts yield
#reserves an entire line for each logographic element of the compound, with the form field containing the entire logographic compound.
#For example, {LU₂}A.SIG = mār damqi takes up two conllu lines, one for mār and one for damqi. But '{LU₂}A.SIG' is used for the form
#field in both lines. Other information in the original oracc json file for the text must have disambiguated the two entries.
#But that info is not readily at hand now. So I use the dictionary in tokenizer_exception.py as shortcut, since it contains
#most of the compound forms expressed by compound logograms/transliterations (but perhaps not all).

def share_compound_form(textLemma : str, transDictLemma : str, tokenDict : dict, lemmaDict : dict):
    tokenDictKeys = tokenDict.keys() #All compounds recorded by me are already preserved in normalization in the keys

    #Currently we are imaging one case to handle. Maybe think of more later.
    #Case 1: textLemma is 1st member of recorded compound, transDictLemma is last (this is, I assume, how my trans-lemma dictionaries work, since trans entries always seem to go with final members of compounds)
    sharedCompounds = [form for form in tokenDictKeys if ((in_compound_form(transDictLemma, form, lemmaDict) in ["element","entire"]) and (in_compound_form(textLemma, form, lemmaDict) in ["element","entire"]))]
    #If the list sharedCompounds s non-empty, textLemma and transDictLemma probably belong to same compound. Ideally, the list should have only one element

    #print("sharedCompounds: ")
    #print(sharedCompounds)

    if len(sharedCompounds) > 0:
        #We should get position of textLemma within the normalized compound to see how many futher lines in conllu file we must include in compound
         #Just take first element of list of shared compounds, then split it on whitespace, - to check for position of textLemma in the compound
        compound = sharedCompounds[0]
        print("In share_compound,")
        print("textLemma: " + textLemma + ", transDictLemma: " + transDictLemma + ", compound: " + compound)

        transContainmentType = in_compound_form(transDictLemma,compound,lemmaDict)
        normContainmentType = in_compound_form(textLemma, compound, lemmaDict)

        elementList = re.split(r"[\s-]", compound)



        #We need to know if transDictLemma is a proper element of the compound or equals the entire compound (in which case there are still probably
        #hypens in it, so that we can determine the value of the 2nd and 4th coordinates in the returned 4-tuple. The 2nd coordinate is an integer that essentially indicates
        #how much to jump ahead in the normalization file, while the 4th says how much to jump in the transliteration file

        #Case of textLemma = ša, transDictLemma = rēšu, compound = ša-rēši; third condition current just to make the program run
        if transContainmentType == "element" and normContainmentType == "element" and textLemma in elementList:

            # Return list of three integers and string. First the position of textLemma in compound, second the jump amount for normalization file
            # The 4th integer is the jump distance for transliteration. In the case the transliterated token occupies multiple lines,
            # the 2nd and 4th integer should be the same, but if it is like {LU₂}ša₂-E₂-02-e, then in normalization file we must jump multiple steps, in transliteration just 1.

            return (elementList.index(textLemma), len(elementList), compound, len(elementList))

        #Case of textLemma = ṣāb šarri, transDictLemma = šarru, compound = ṣāb šarri
        elif transContainmentType == "element" and normContainmentType == "entire":

            #In this case, textLemma is necessarily the first element of compound (as it is the entire compound)
            #We only need to jump 1 step in norm file (since the entire compound is in one entry there)
            #But in transfile we need to jump the number of elements in the compound

            return (0,1,compound,len(elementList))

        #Case of textLemma = ša, transDictLemma = {LU₂}ša₂-E₂-02-e/ša-bēti-šanie, compound = ša-bēti-šanie
        elif transContainmentType == "entire" and normContainmentType == "element":

        # In this case, we do NOT use len(elementList) for 4th coordinate, because we are in a situation like where transDictLemma = compound = ša-bēti-šanie,
        # i.e. we only want the trans file index to increment by 1, but the norm file index by number of elements in compound
            return (0, len(elementList), compound, 1)

        #I don't see how the following case could arise, but include it for completion
        elif transContainmentType == "entire" and normContainmentType == "entire":

            return (0,1,compound,1)


        #If for some reason we cannot determine containment, return (0,0,"",0)
        elif transContainmentType == "" or normContainmentType == "":
            return (0,0,"",0)

        else:
            return (0,0,"",0)

    #If there are no shared compounds between textLemma and transDictLemma
    #They might still belong to compound not yet in that list.

    #One possibility is that textLemma is contained within transDictLemma or vice versa. This can happen with
    #broken forms in both transliteration/normalization files. E.g. Trans file has x+x-u2, norm file has x+x, u2
    #So we check for this as well

    elif textLemma in transDictLemma:
        #We assume here that both textLemma, transDictLemma are broken forms, containing elements joined by "-"

        print("textLemma: " + textLemma + " in transDictLemma: " + transDictLemma)

        textLemmaElements = textLemma.split("-")
        transDictLemmaElements = transDictLemma.split("-")

        #We want to subtract out textLemmaElements from transDictLemmaElements
        remainingElements = []

        for i in range(0,len(textLemmaElements)):
            if textLemmaElements[i] in transDictLemmaElements:
                #By assumption, len(textLemmaElements) <= len(transDictLemmaElements), so we pop off the shared elements
                transDictLemmaElements.pop(i)

        print("remainingElements in transDictLemma:")
        print(transDictLemmaElements)

        #index of element 'textLemma' in transDictLemma given by find() function, number of jump steps
        #for norm file given by len(remainingElements)+1 (holds even if textLemma = transDictLemma)
        return (transDictLemma.find(textLemma),len(transDictLemmaElements)+1,transDictLemma,1)

    elif transDictLemma in textLemma:
        print("transDictLemma in textLemma")
        # We assume here that both textLemma, transDictLemma are broken forms, containing elements joined by "-"
        #Do the same as above, save with roles of transDictLemma and textLemma reversed
        textLemmaElements = textLemma.split("-")
        transDictLemmaElements = transDictLemma.split("-")

        print("transDictLemmaElements: ")
        print(transDictLemmaElements)
        print("textLemmaElements: ")
        print(textLemmaElements)

        for i in range(0,len(transDictLemmaElements)):
            print(transDictLemmaElements[i])
            print(transDictLemmaElements[i] in textLemmaElements)
            if transDictLemmaElements[i] in textLemmaElements:
                print("Popping element of textLemmaElements equal to: " + transDictLemmaElements[i])
                #By assumption, len(textLemmaElements) <= len(transDictLemmaElements), so we pop off the shared elements
                textLemmaElements.pop(i)

        print("remainingElements in textLemma:" )
        print(textLemmaElements)

        # index of element 'transDictLemma' in textLemma given by find() function; number of jump steps
        # for norm file given by len(remainingElements)+1 (holds even if textLemma = transDictLemma)
        return (textLemma.find(transDictLemma), len(textLemmaElements) + 1, textLemma, 1)

    else:
        return (0,0,"",0)



#Function that transfers lines of trans file to norm file, printing to output file

def transfer_lines(normLines : list, transLines : list, outputFile):
    # Now go through lines of transliteration file
    normIndex = 0
    transIndex = 0
    while normIndex < len(normLines):

        print("---------------")  # Just for debugging
        print("normIndex: " + str(normIndex))
        print("transIndex: " + str(transIndex))
        if transIndex >= len(transLines):
            print("transIndex = len(transLines) = " + str(transIndex))
            break

        transLineArray = transLines[transIndex].rstrip('\n').split('\t')
        normLineArray = normLines[normIndex].rstrip('\n').split('\t')

        transForm = correct_bracket(transLineArray[2])  # Get transliteration token
        #print("correctedBracket: " + transForm)

        # Get lemma itself, because (unfortunately), I didn't remember that a single logogram and transliterations can yield different forms, even if those forms all have the same lemma
        #Correct left bracket in case of broken forms
        normLemmaFromText = correct_bracket(normLineArray[3])

        # But we will also need the form itself when checking for shared compounds, because the lemma itself will not usually be represented in the tokenizer_exception file (e.g. mukīl appāti, where the form for the first element is mukīl (which is found in tokenizer_exception), while the lemma is mukillu, which is not
        normFormFromText = correct_bracket(normLineArray[2])
        print("transForm: " + transForm)
        print("normLemmaFromText: " + normLemmaFromText)
        print("normFormFromText: " + normFormFromText)

        if transForm not in transNormDict.keys():
            print("transForm " + transForm + " not found in transNormDict keys at trans index " + str(transIndex))
            normIndex = normIndex + 1
            transIndex = transIndex + 1

        else:


            # We need to first check if the normalized token is a number, b/c pure numbers are not in the lemma table for normalizations (=normLemmaDict, although they are in the lemma table for transliterations)
            if normLemmaFromText.isdigit():
                print("normLemmaFromText is digit")
                # If the transliteration form is also an int and equals the normalized form, just skip
                if transForm.isdigit() and int(transForm) == int(normLemmaFromText):
                    normIndex = normIndex + 1
                    transIndex = transIndex + 1

                else:
                    print("Number mismatch at normIndex " + str(normIndex))
                    print("normLemmaFromText: " + normLemmaFromText)
                    print("transForm: " + transForm)


                    normIndex = normIndex + 1
                    transIndex = transIndex + 1

            # Hard code a few specific cases here b/c I am at a loss as to how to handle them in the more general loops below

            # Case of transForm = {LU₂}ša-pān(IGI)-ēkalli(KUR), normForm = ša/ša₂, next two norm lines are pān, ēkalli
            elif transForm == "{LU₂}ša₂-IGI-KUR" and normIndex + 2 < len(normLines) and normFormFromText in ["ša","ša₂"]:

                print("Matched transForm == {LU₂}ša₂-IGI-KUR")
                transIndex = transIndex + 1
                normIndex = normIndex + 3
            # Otherwise, normalized token is not a number, and has entry in normLemmaDict

            # Case of transForm = "KUR-ǎs-šur{KI}", normForm = māt, next two norm lines are pān, ēkalli

            elif transNormDict[transForm] == "Māt-Aššur" == normFormFromText:
                print("Matched transForm == KUR-ǎs-šur{KI} normFormFromText = māt")

                transIndex = transIndex + 3
                normIndex = normIndex + 1

            # Otherwise, normalized token is not a number, and has entry in normLemmaDict

            else:



                # In all string comparisons we should compare cae-insensitive b/c of problems standardizing cases in some PN's

                # In addition, we need to use both the normalized form of the transliteration and the lemma of that normalized form in comparisons, because of complications arising
                # from compound terms

                transNormFromDict = transNormDict[transForm]  # Note that this form reflects Assyrian phonology (e.g. imāri, not imēri, unlike transLemmaFromDct below)

                # if transForm is a logographic or transliterate compound, this is the last element of the compound.
                # But it can be the whole compound itself in normalized form still with dashes, such as {LU₂}ša₂-E₂-02-e -> ša-bēti-šanie.
                # Below in checking compound membership, we thus have to include the case where transLemmaFromDict is essentially just
                # transForm itself in normalized form with dashes

                # Because some transliteration and/or normalization forms are not actually in normLemmaDict (e.g. broken forms represented in transliteration
                # Wto check for membership in normLemmaDict

                if transNormFromDict in normLemmaDict.keys():

                    transLemmaFromDict = normLemmaDict[
                        transNormFromDict]  # This form reflects Babylonian phonology (imēri vs. imāri). Cf. above.

                # Otherwise, we just use transNormFromDict
                else:
                    transLemmaFromDict = transNormFromDict

                print("transNormFromDict: " + transNormFromDict)
                print("transLemmaFromDict: " + transLemmaFromDict)

                # Check normLemmaFromText against both transFormFromDict and transLemmaFromDict b/c of Babylonian/Assyrian phonology issue described above. This first case is unlikely to happen, but we also need to do this check for the compound cases
                #Also check normFormFromText against transFormFromDict because of other incompatibilities arising from differences in trans form dict, trans lemma dict, and norm form, and norm lemma dict
                if normLemmaFromText.casefold() == transLemmaFromDict.casefold() \
                        or normLemmaFromText.casefold() == transNormFromDict.casefold()\
                        or normFormFromText.casefold() == transNormFromDict.casefold() \
                        or (normFormFromText in transNormDict.keys() and transNormDict[normFormFromText].casefold() == transNormFromDict.casefold()):

                    print("Direct match ")
                    normLineArray[10] = correct_bracket(normLineArray[2])  # Store inflected norm form in 10th position
                    normLineArray[2] = transForm

                    normIndex = normIndex + 1
                    transIndex = transIndex + 1

                #If direct comparison fails, next check if their lemmas or norms are dialect equivalents
                elif normLemmaFromText.casefold() in dialectConversionDict.keys() and (dialectConversionDict[normLemmaFromText.casefold()] == transLemmaFromDict or dialectConversionDict[normLemmaFromText.casefold()] == transNormFromDict):
                    print("Dialect match ")
                    normLineArray[10] = correct_bracket(normLineArray[2])  # Store inflected norm form in 10th position
                    normLineArray[2] = transForm

                    normIndex = normIndex + 1
                    transIndex = transIndex + 1

                #or if normLemmaFromText is beginning element of transForm (and not the whole form), as in KUR and KUR-aš-šur{KI}
                elif normLemmaFromText.casefold() in transForm.casefold() and transForm.casefold().replace(normLemmaFromText.casefold(),"") != "":

                    print("normLemmaFromText properly in transForm")

                    #Hack to handle cases where presence of determiner in transForm (e.g. {LU₂}) is messing up comparison

                    transForm_sub = strip_determiner(transForm)

                    print("transForm_sub: " + transForm_sub)

                    #Find out how many elements remain in transForm and jump that many extra
                    #There are two cases where problems may arise. One is norm = ša, transForm = {LU₂}ša-IGI-KUR. The other is norm = {1}ha, transForm = {1}ha-al-qi.
                    #The former case is handled by the '_sub' terms, which strip off determiner. The latter is handed by non _sub terms.
                    #Whichever method yields the smaller jump interval, we use that.

                    remainder_sub = transForm_sub.casefold().replace(normLemmaFromText.casefold(), "").lstrip("-")
                    remainder_sub = remainder_sub.replace("₂","") #Add this to handle cases of transForm having a sign with subscript 2, norm only 1 (right now only for ša₂/ša)

                    remainder = transForm.casefold().replace(normLemmaFromText.casefold(), "").lstrip("-")

                    remainderArray_sub = [x for x in remainder_sub.split("-") if x != ""]
                    remainderArray = [x for x in remainder.split("-") if x != ""]

                    print("remainderArray_sub: ")
                    print(remainderArray_sub)

                    print("remainderArray: ")
                    print(remainderArray)


                    normLineArray[10] = correct_bracket(normLineArray[2])  # Store inflected norm form in 10th position
                    normLineArray[2] = transForm

                    jumpAddition = min(len(remainderArray),len(remainderArray_sub))

                    print("jumpAddition = " + str(jumpAddition))

                    #We need to make a check that the subsequent lines after the norm line actually have # of lines = jumpAddition,,or subtract a certain number
                    #based on how the remaining elements of transForm clump together. Fur instance, if the norm file has x, u₂-ni (instead of x, u₂, ni) while trans file has x-u₂-ni
                    # we want in norm file to jump only 2 lines, not 3. So we need to look ahead in norm file

                    remainderArrayJoined = "-".join(remainderArray)
                    remainderArray_subJoined = "-".join(remainderArray_sub)

                    #But we also need to check elements in norm file against the normalized versions of the transForm, since they can be present (e.g. norm form = ša, pan, ekalli, while transForm = ša-IGI-KUR)
                    remainderArrayNormalized = [transNormDict[x] for x in remainderArray if x in transNormDict.keys()]
                    remainderArray_subNormalized = [transNormDict[x] for x in remainderArray_sub if x in transNormDict.keys()]

                    jumpAdditionModified = 0

                    i = 1

                    while jumpAdditionModified < jumpAddition and normIndex+jumpAdditionModified+1 <len(normLines):
                        print("Now checking the new few lines of norm file")
                        nextElement = correct_bracket(normLines[normIndex+jumpAdditionModified+1].rstrip("\n").split("\t")[2]) #Get next line form
                        print("nextElement is: " + nextElement)

                        #If that next line's form is in the remainder of transForm - normForm, get its length and add it to jumpAdditionModified, go on to next line
                        if nextElement.casefold() in remainderArrayJoined or nextElement.casefold() in remainderArray_subJoined or \
                                nextElement.casefold() in remainderArrayNormalized or nextElement.casefold() in remainderArray_subJoined:
                            print("Match in remainderArrayJoined/_sub: " )
                            print(remainderArrayJoined)
                            print(remainderArray_subJoined)

                            jumpAdditionModified = jumpAdditionModified + 1 #We've found an additional element, so increment jump counter only by one

                        elif nextElement.casefold() in remainderArrayNormalized or nextElement.casefold() in remainderArray_subNormalized:

                            print("Match in remainderArrayNormalized/_sub: ")
                            print(remainderArrayNormalized)
                            print(remainderArray_subNormalized)

                            jumpAdditionModified = jumpAdditionModified + 1


                        #If the next line's form is not in the remainder, stop
                        else:
                            print("Breaking with jumpAdditionModified at: " + str(jumpAdditionModified))
                            break

                    print("jumpAdditionModified is: " + str(jumpAdditionModified))

                    normIndex = normIndex + 1+ jumpAdditionModified
                    transIndex = transIndex + 1

                # Otherwise, if normLemmaFromText, transLemmaFromDict are not identical, they should come from the same compound found in tokenizer_exception dictionary
                # The main problem is that transLemmaFromDict itself may not appear as a substring of that compound (e.g. appatu in mukīl appāti)

                else:

                    # We have to pass normFormFromText to search function b/c sometimes the lemma of an element in a normalized compound is not within the compound itself (e.g. mukīl/mukillu in mukīl appāti)
                    # Note that we also have to check both transNormFromDict and transLemmaFromDict b/c te trans norm dict follows Assyrian phonology while the (trans) lemma dict is Babylonian
                    transFormTuple = share_compound_form(normFormFromText, transNormFromDict, tokExceptDict,
                                                         normLemmaDict)
                    transLemmaTuple = share_compound_form(normFormFromText, transLemmaFromDict, tokExceptDict,
                                                          normLemmaDict)


                    # Define this 4-tuple
                    (indexOfnormLemmaFromText, normJump, compound, transJump) = (0, 0, "", 0)

                    # We first opt for transNormTuple case. If its comparison works out, use it for jump info
                    if transFormTuple != (0, 0, "", 0):
                        print("transFormTuple != (0,0,'',0)")
                        (indexOfnormLemmaFromText, normJump, compound, transJump) = transFormTuple
                    # Otherwise, use transLemmaTuple
                    elif transLemmaTuple != (0, 0, "", 0):
                        print("transLemmaTuple != (0,0,'',0)")
                        (indexOfnormLemmaFromText, normJump, compound, transJump) = transLemmaTuple

                    # Check if normFormFromText, transForm belong to preposition compound like i-pa-an = ina pān
                    elif in_prep_contraction(normFormFromText, transForm):
                        print("In preposition contraction")
                        (indexOfnormLemmaFromText, normJump, compound, transJump) = (0, 2, normFormFromText, 2)

                    # If all the above fails, use 'null' tuple

                    else:

                        (indexOfnormLemmaFromText, normJump, compound, transJump) = (0, 0, "", 0)

                    print("(indexOfnormLemmaFromText, normJump, compound, transJump) = (" + str(
                        indexOfnormLemmaFromText) + "," + str(normJump) + "," + compound + "," + str(transJump) + ")")

                    # If there is shared compound
                    if normJump > 0:

                        # First store old normalization form in field 10, transfer transliteration form to the normalization file
                        # And store 'the' compound that the normalized and transliteration forms belong to at the level of lemmas. This compound
                        # may not be unique, and we may later want to change features of share_compound_form to handle that.

                        # Right now, assigning normLineArray[2] to normLinArray[10] should just put the first element of a compound there
                        normLineArray[10] = correct_bracket(normLineArray[2])

                        normLineArray[2] = transForm
                        normLineArray[3] = compound

                        # We want to transfer (what should be) the single DEP rel that connects an element in the compound from outside the compound (this may be on the first element already) to the head of the compound
                        # So we need to go through the other lines in the normalization containing those other elements of the compound and see if they have DEP rel from outside
                        # As far as I know there are at most only 3 elements in any of the compounds registered in oracc,,making normJump <= 3.

                        innerIncrement = indexOfnormLemmaFromText + 1  # Start with element right after normLemmaFromText



                        # By design, indexOfnormLemmaFromText is < normJump
                        while innerIncrement < normJump:

                            print("Checking inner elements, with innerIncrement: " + str(innerIncrement))

                            innerHeadIndex = normLines[normIndex + innerIncrement].split('\t')[7]


                            # Note that this index is a relative one, representing the token in sentence before we took out all the spaces or meaningless tokens like '{'
                            #We want to look at the index one  we have to jump to get beyond the compound
                            finalElementIndex = normLines[normIndex + normJump-1].split('\t')[1]
                            if innerHeadIndex > finalElementIndex:
                                # We need to reassign the head index of the later element of compound to the one indexed by normLemmaFromText
                                normLineArray[7] = innerHeadIndex

                            # It might also be the case that the UPOS,XPOS of the head element of normalized compound does not equal those of the transliterated compound (e.g. ša-rēši). Similarly for the UFeats
                            # Maybe here is where we should handle it. But for now we leave this issue out.
                            innerIncrement = innerIncrement + 1

                        # We also want in the end to jump ahead a number of lines in each file, determined by the nature of the compound

                        #A safe way to calculate the size of the trans jump is to see how many more form entries in the trans file are identical to the current line's
                        i = 1
                        while transIndex+i < len(transLines):
                            nextTransForm = transLines[transIndex+i].rstrip("\n").split("\t")[2]
                            #If next line's transForm is identical, increase counter
                            if transForm == correct_bracket(nextTransForm):
                                i = i + 1
                            #If the next line doesn't have identical form, then stop immediately
                            else:
                                break



                        normIndex = normIndex + normJump
                        transIndex = transIndex + i

                        #Original method of calculating jump distance. Currently putting aside in favor of above method
                        #We need to add a check to see if transForm actually has more elements than transFormFromDict/transLemmaFromDict.
                        # This can happen in cases like {LU₂}A.KIN-ia (3 elements) = mār šiprīya (2 elements). Here, we have to set
                        # transJump = number of elements in transform rather than transFormFromDict etc. b/c that is the number of lines taken up in the norm file
                        # whereas transJump is given by number of elements in transFormFromDict, which here would be 2.

                        #l = len(transForm.split("-"))

                        #if  l > transJump:
                        #    transJump = l

                        #normIndex = normIndex + normJump - indexOfnormLemmaFromText  # Theoretically we make the jump over the rest of a compound when we encounter its head element (making indexOfnormLemmaFromText superfluous),,but we use this formula for debugging, further control
                        #transIndex = transIndex + transJump

                    # If there is no common compound known between transliteration and normalization, mark it with '@@@'
                    if normJump == 0:
                        normLineArray[2] = normLineArray[2] + "@@@"
                        normIndex = normIndex + 1
                        transIndex = transIndex + 1

        # Leave out first row for now, which is the absolute row index from the pandas frame structure

        normLineArray = normLineArray[1:]

        normLine = "\t".join(normLineArray)

        print("Printing normLine")
        print(normLine, file=outputFile)
        # We need to determine whether we are starting a new sentence in the norm file.
        # This should theoretically happen only when second col. of normLines[normIndex] >= normLines[normIndex+1]

        if 0 < normIndex - 1 and normIndex < len(normLines):
            previousNormLineArray = normLines[normIndex - 1].rstrip("\n").split("\t")
            currentNormLineArray = normLines[normIndex].rstrip("\n").split("\t")

            print("previousNormLineArray[1]: " + str(previousNormLineArray[1]))
            print("currentNormLineArray[1]: " + str(currentNormLineArray[1]))

            if int(previousNormLineArray[1]) >= int(currentNormLineArray[1]):
                print("Making new sentence")
                print("\n", file=outputFile)




#List of names of input norm and trans files. They should form  two parallel lists of files starting with P-numbers

normFilesList = [file for file in os.listdir(normInputPath) if fnmatch(file, '*.conllu')]
transFilesList = [file for file in os.listdir(transInputPath) if fnmatch(file, '*.conllu')]

normFilesList.sort()
transFilesList.sort()
#normFilesList = glob.glob(os.path.join(normInputPath, '*.conllu')).sort()
#transFilesList = glob.glob(os.path.join(transInputPath, '*.conllu')).sort()

pairFilesList = []

#Check if the two lists of files is same length, and if so, zip them together
if len(normFilesList) == len(transFilesList):
    pairFilesList = zip(normFilesList,transFilesList)
    #print(pairFilesList)
else:
    print("Different number of files in norm, trans directories")
    sys.exit()


for (normFilename,transFilename) in pairFilesList:
    normInputFile = open(os.path.join(os.getcwd(), normInputPath, normFilename), 'r')
    transInputFile = open(os.path.join(os.getcwd(), transInputPath, transFilename), 'r')

    normInputFileName = os.path.basename(normInputFile.name)

    normInputFileBase = os.path.splitext(normInputFileName)[0]

    transInputFileName = os.path.basename(transInputFile.name)

    transInputFileBase = os.path.splitext(transInputFileName)[0]

    normOutputFileNameIntermediate = outputPathIntermediate + normInputFileBase + "_norm.tsv"
    transOutputFileNameIntermediate = outputPathIntermediate + transInputFileBase + "_trans.tsv"

    transOutputFileNameFinal = outputPathFinal + transInputFileBase + "_trans_final.conllu"

    #Get lines from norm input file, clean them up
    originalNormLines = normInputFile.readlines()  # Get lines from input norm conllu file.
    intermediateNormLines = []
    # First, cut out comment lines and empty lines
    for i in range(0,len(originalNormLines)):
        # Skip over comment lines with '#', empty space
        line = originalNormLines[i]
        if ("#" in line) or (line.isspace()) or "saa" in line or "/" in line or re.search(r'P[0-9]{6}',line):
            continue
        else:
            intermediateNormLines.append(line.rstrip("\n"))

    # Get lines from trans input file and clean them up
    originalTransLines = transInputFile.readlines()  # Get lines from input norm conllu file.
    intermediateTransLines = []
    # First, cut out comment lines and empty lines
    for i in range(0, len(originalTransLines)):
        # Skip over comment lines with '#', empty space
        line = originalTransLines[i]
        if ("#" in line) or line.isspace() or "saa" in line or "/" in line or re.search(r'P[0-9]{6}',line):
            continue
        else:
            intermediateTransLines.append(line.rstrip("\n"))

    #Transfer the edited norm file to a new one as a .tsv file for pandas

    normOutputFileIntermediate = open(normOutputFileNameIntermediate, 'w')

    for i in range(0,len(intermediateNormLines)):

        print(intermediateNormLines[i],file=normOutputFileIntermediate)
        #print(intermediateNormLines[i])

    normOutputFileIntermediate.close()

    #Ditto for trans files

    transOutputFileIntermediate = open(transOutputFileNameIntermediate, 'w')

    for i in range(0,len(intermediateTransLines)):

        print(intermediateTransLines[i],file=transOutputFileIntermediate)
        #print(intermediateNormLines[i])

    transOutputFileIntermediate.close()

    header = ["id","form","lemma","upos","xpos","feats","head","deprel","deps","misc"]

    normdf = pd.read_table(normOutputFileNameIntermediate,names = header)
    #print(normdf)
    transdf = pd.read_table(transOutputFileNameIntermediate, names = header)

    #eliminate rows with '{', or '}'
    transdf = transdf[transdf.form != "{"]
    transdf = transdf[transdf.form != '}']
    transdf = transdf.reset_index(drop=True)

    # eliminate rows with (', or ')'
    transdf = transdf[transdf.form != "("]
    transdf = transdf[transdf.form != ')']
    transdf = transdf.reset_index(drop=True)

    normdf = normdf[normdf.form != "-"]
    normdf = normdf[normdf.form != "{"]
    normdf = normdf[normdf.form != "}"]
    normdf = normdf[normdf.form != "("]
    normdf = normdf[normdf.form != ")"]
    normdf = normdf.reset_index(drop=True)

    transdf.to_csv(transOutputFileNameIntermediate, sep="\t", header=False)
    normdf.to_csv(normOutputFileNameIntermediate, sep="\t", header=False)

    normOutputFileIntermediate.close()

    normOutputFileIntermediate = open(normOutputFileNameIntermediate, 'r')

    normLines = normOutputFileIntermediate.readlines()

    transOutputFileIntermediate = open(transOutputFileNameIntermediate, 'r')

    transLines = transOutputFileIntermediate.readlines()

    transOutputFileFinal = open(transOutputFileNameFinal, 'w')

    print("Processing " + transInputFileBase)

    transfer_lines(normLines,transLines,transOutputFileFinal)
