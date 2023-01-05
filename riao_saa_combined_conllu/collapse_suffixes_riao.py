import os
import re

inputFile = open("akk_riao-ud-test.conllu", 'r')
outputFile = open("akk_riao-ud-testConverted.conllu", 'w')

lines = inputFile.readlines()

lineIndex = 0

while lineIndex < len(lines):
    line = lines[lineIndex].rstrip('\n')
    matchCompositeToken = re.search(r"^[0-9]+-[0-9]+", line)
    if matchCompositeToken != None: #See if line starts with range of numbers, indicating a composite token.
        #print(line)

        matchString = matchCompositeToken.group()
        matchArray = matchString.split('-')
        
        headID =  matchArray[0] #Get ID's of 
        suffID = matchArray[1]

        if int(suffID)-int(headID) == 2: #For akk_riao, the composite tokens usually consist of exactly two tokens, the base and the suffix. But this condition checks if we have exactly three subtokens. This happens when there is a -ma or -ni suffix after a pronominal suffix.
            compositeLineArray = lines[lineIndex].rstrip('\n').split('\t') #Split up composite line along tab
            headLineArray = lines[lineIndex+1].rstrip('\n').split('\t') #Split up head line along tab
            suff1LineArray = lines[lineIndex+2].rstrip('\n').split('\t') #Split up suffix 1 line along tab
            suff2LineArray = lines[lineIndex+3].rstrip('\n').split('\t') #Split up suffix 2 line along tab

            headLineArray[1] = compositeLineArray[1] #Transfer surface form from the composite line to the head line (whose ID is one more than the ID of the token right before the composite token)

            headTokenPOS = headLineArray[3] #Get POS of head and two suffixes
            suff1TokenPOS = suff1LineArray[3] 
            suff2TokenPOS = suff2LineArray[3] 
        
            if headTokenPOS == 'NOUN' and suff1TokenPOS == 'PRON' and suff2TokenPOS == 'PART': #If head token is a noun, suff1 a pron, and suff2 is -ma particle or -ni particle
        
                oldHeadFeatures = headLineArray[5] #Get morphological features of head

                if oldHeadFeatures == '_': #This may happen for a compound token that is actually a fragment, as in x-ba, where the head is x and its features column is marked '_'
                    oldHeadFeatures = ""
                    
                elif "NounBase=Suffixal|" in oldHeadFeatures:
                    headLineArray[5] = oldHeadFeatures.replace("NounBase=Suffixal|","") #Get ride of NounBase=Suffixal feature

                oldSuff1Features = suff1LineArray[5] #Now we need to relabel and transfer the features of the suffix to the head
                oldSuff1FeaturesArray = oldSuff1Features.split('|') #Split up string according to features

                
                #print(oldSuff1FeaturesArray)
                #print(lineIndex)

                
                for feature in oldSuff1FeaturesArray: #Get name, value of each feature
                    featureArray = feature.split('=')
                    featureName = featureArray[0]
                    featureValue = featureArray[1]

                    if featureName == 'Gender': #Transfer feature value to head features string
                        headLineArray[5] += "|"+"PossSuffGen="+featureValue
                    if featureName == 'Number':
                        headLineArray[5] += "|"+"PossSuffNum="+featureValue
                    if featureName == 'Person':
                        headLineArray[5] += "|"+"PossSuffPer="+featureValue

                
                oldSuff2Features = suff2LineArray[5] 
                oldSuff2FeaturesArray = oldSuff2Features.split('|')

                if oldSuff2Features != "_": #Check if line has features (which in akk_riao-ud-test means it is -ni)
                
                    for feature in oldSuff2FeaturesArray:
                        featureArray = feature.split('=')
                        featureName = featureArray[0]
                        featureValue = featureArray[1]

                        if featureName == 'Subordinative': #The ni particle
                            headLineArray[5] += "|"+"Subordinative="+featureValue
                            
                elif suff2LineArray[1] == 'ma': #Otherwise, it is the -ma particle
                    headLineArray[5] += "|"+"Focus=Yes"
                    
            if headTokenPOS == 'VERB' and suff1TokenPOS == 'PRON' and suff2TokenPOS == 'PART': #If head token is a verb, suff1 a pron, suff2 is a particle (-ma/-ni)
        
            
                #No need to get rid of any features in head
                
                oldSuff1Features = suff1LineArray[5] #Now we need to relabel and transfer the features of the suffix to the head
                oldSuff1FeaturesArray = oldSuff1Features.split('|') #Split up string according to features

                if len(oldSuff1FeaturesArray) >= 1: #copy of akk_riao-ud-test.conllu on universaldependencies.org has some errors in it, including one line where the morphological features of a pronominal suffix aren't specified. We put this if condition here to avoid it.
                    for feature in oldSuff1FeaturesArray: #Get name, value of each feature
                        featureArray = feature.split('=')
                        featureName = featureArray[0]
                        featureValue = featureArray[1]

                        if featureName == 'Gender':
                            headLineArray[5] += "|"+"VerbSuffGen="+featureValue
                        if featureName == 'Number':
                            headLineArray[5] += "|"+"VerbSuffNum="+featureValue
                        if featureName == 'Person':
                            headLineArray[5] += "|"+"VerbSuffPer="+featureValue
                            
                oldSuff2Features = suff2LineArray[5] 
                oldSuff2FeaturesArray = oldSuff2Features.split('|')

                if oldSuff2Features != "_": #Check if line has features (which in akk_riao-ud-test means it is -ni)
                
                    for feature in oldSuff2FeaturesArray:
                        featureArray = feature.split('=')
                        featureName = featureArray[0]
                        featureValue = featureArray[1]

                        if featureName == 'Subordinative': #The ni particle
                            headLineArray[5] += "|"+"Subordinative="+featureValue
                            
                elif suff2LineArray[1] == 'ma': #Otherwise, it is the -ma particle
                    headLineArray[5] += "|"+"Focus=Yes"

            outputLine = '\t'.join(headLineArray)
            #print(outputLine)
            print(outputLine, file=outputFile)
            
            lineIndex = lineIndex+4
            continue

        if int(suffID)-int(headID) == 1: #If we have exactly two subtokens
        
            
        
            headLineIndex = lineIndex+1 #Head token is 1 line after composite
            suffixLineIndex = lineIndex+2 #Suff token is 2 lines after composite

            #lines.pop(lineIndex) #Eliminate line for composite token
            compositeLineArray = lines[lineIndex].split('\t') #Split up composite line along tab
            headLineArray = lines[headLineIndex].rstrip('\n').split('\t') #Split up head line along tab
            suffLineArray = lines[suffixLineIndex].rstrip('\n').split('\t') #Split up suffix line along tab
        
            headLineArray[1] = compositeLineArray[1] #Transfer surface form from the composite line to the head line (whose ID is one more than the ID of the token right before the composite token)

            headTokenPOS = headLineArray[3] #See if head token is noun
            suffTokenPOS = suffLineArray[3] #and that suffix is a pronoun

            if headTokenPOS == 'PROPN' and suffTokenPOS == 'PART': #If head token is a proper noun, suff a part (pretty much the only possible suffix for a proper noun, save perhaps -ni in subordinate clauses'
        
                #No need to get morphological features of head

                if headLineArray[5] == '_': #This should happen if head is a proper noun
                    headLineArray[5] = "" #That way, we don't ajoin strings to '_'
               
    
            if headTokenPOS == 'NOUN' and suffTokenPOS == 'PRON': #If head token is a noun, suff a pron
        
                oldHeadFeatures = headLineArray[5] #Get morphological features of head

                if oldHeadFeatures == '_': #If first token is an x
                    headLineArray[5] = "" #That way, we don't ajoin strings to '_'
                    #print("oldHeadFeatures is _")
                    
                elif "NounBase=Suffixal|" in oldHeadFeatures:
                    headLineArray[5] = oldHeadFeatures.replace("NounBase=Suffixal|","") #Get ride of NounBase=Suffixal feature

                oldSuffFeatures = suffLineArray[5] #Now we need to relabel and transfer the features of the suffix to the head
                oldSuffFeaturesArray = oldSuffFeatures.split('|') #Split up string according to features
                #print(oldSuffFeaturesArray)
                #print(lineIndex)
                for feature in oldSuffFeaturesArray: #Get name, value of each feature
                    featureArray = feature.split('=')
                    featureName = featureArray[0]
                    featureValue = featureArray[1]

                    if featureName == 'Gender': #Transfer feature value to head features string
                        headLineArray[5] += "|"+"PossSuffGen="+featureValue
                    if featureName == 'Number':
                        headLineArray[5] += "|"+"PossSuffNum="+featureValue
                    if featureName == 'Person':
                        headLineArray[5] += "|"+"PossSuffPer="+featureValue


                    headLineArray[5] = headLineArray[5].lstrip('|') #Strip off any leading '|'
                    
            if headTokenPOS == 'VERB' and suffTokenPOS == 'PRON': #If head token is a verb, suff a pron
        
            
                #No need to get rid of any features in head
                
                oldSuffFeatures = suffLineArray[5] #Now we need to relabel and transfer the features of the suffix to the head
                oldSuffFeaturesArray = oldSuffFeatures.split('|') #Split up string according to features

                if len(oldSuffFeaturesArray) >= 1: #copy of akk_riao-ud-test.conllu on universaldependencies.org has some errors in it, including one line where the morphological features of a pronominal suffix aren't specified. We put this if condition here to avoid it.
                    for feature in oldSuffFeaturesArray: #Get name, value of each feature
                        featureArray = feature.split('=')
                        featureName = featureArray[0]
                        featureValue = featureArray[1]

                        if featureName == 'Gender':
                            headLineArray[5] += "|"+"VerbSuffGen="+featureValue
                        if featureName == 'Number':
                            headLineArray[5] += "|"+"VerbSuffNum="+featureValue
                        if featureName == 'Person':
                            headLineArray[5] += "|"+"VerbSuffPer="+featureValue

            if headTokenPOS == 'VERB' and suffTokenPOS == 'PART': #If suffix is ma particle or -ni particle

                if  "Subordinative" in suffLineArray[5]: #The ni particle
                    headLineArray[5] += "|"+"Subordinative=Yes"
                elif suffLineArray[1] == 'ma': #Then it is the 'ma' particle. 
                    headLineArray[5] += "|"+"Focus=Yes" #It is possible ma here marks the whole sentence rather than focalizes a single word, but we need a way to store its presence as feature for now.
                    
                            
            if headTokenPOS == 'ADP' and suffTokenPOS == 'PRON': #If head token is a preposition, suff a pron


                if headLineArray[5] == '_': #If first token is a prep
                    headLineArray[5] = "" #That way, we don't ajoin strings to '_'
                    #print("Stripped off _ from prep")
                #No need to get rid of any features in head
                
                oldSuffFeatures = suffLineArray[5] #Now we need to relabel and transfer the features of the suffix to the head
                oldSuffFeaturesArray = oldSuffFeatures.split('|') #Split up string according to features

                if len(oldSuffFeaturesArray) >= 1: #copy of akk_riao-ud-test.conllu on universaldependencies.org has some errors in it, including one line where the morphological features of a pronominal suffix aren't specified. We put this if condition here to avoid it.
                    for feature in oldSuffFeaturesArray: #Get name, value of each feature
                        featureArray = feature.split('=')
                        featureName = featureArray[0]
                        featureValue = featureArray[1]

                        if featureName == 'Gender':
                            headLineArray[5] += "|"+"PrepSuffGen="+featureValue
                        if featureName == 'Number':
                            headLineArray[5] += "|"+"PrepSuffNum="+featureValue
                        if featureName == 'Person':
                            headLineArray[5] += "|"+"PrepSuffPer="+featureValue

                headLineArray[6] = suffLineArray[6] #For this case, where we have prep+pronominal suffix, akk_riao-ud-test has suffix dependent on head (i.e. arrow going from prep to suffix, i.e. number in column 6 of head equals ID of suff. We need to set the head value equal to head of suffix because it is the prominal suffix which connects this composite token to outside tokens.

            if headTokenPOS == 'PART' and suffTokenPOS == 'VERB': #This only seems to happen for precatives in akk_riao-ud-test

                if headLineArray[5] == '_': #A particle should not have any features
                    headLineArray[5] = "" #That way, we don't ajoin strings to '_'

                #We basically need to transfer all features from the suffix (verb) to the head, adding the feature Mood=Prec and removing feature Tense=Past. Note that for whatever reason akk_riao-ud-test does not provide a lemma for the verb token, so we will have to leave that entry blank in the final output.

                    suffLineArray[5] = suffLineArray[5].replace("Mood=Ind","Mood=Prec")
                    suffLineArray[5] = suffLineArray[5].replace("Tense=Past","")
                    suffLineArray[5] = suffLineArray[5].replace("||","|") #In case removing 'Tense=Past' led to '||' in string
                    suffLineArray[5] = suffLineArray[5].strip('|') #In case there is a leading or ending '|'
                   
                    headLineArray[0] = suffLineArray[0] #ID
                    #Already transfered Form field way above
                    headLineArray[2] = "_" #Leave lemma field blank
                    headLineArray[3] = suffLineArray[3] #UPOS
                    headLineArray[4] = suffLineArray[4] #XPOS
                    headLineArray[4] = suffLineArray[4] #XPOS
                    headLineArray[5] = suffLineArray[5] #features
                    headLineArray[6] = suffLineArray[6] #XPOS
                    headLineArray[7] = suffLineArray[7] #XPOS
                    headLineArray[8] = suffLineArray[8] #XPOS
                    headLineArray[9] = suffLineArray[9] #XPOS
                    
            

            headLineArray[5] = headLineArray[5].strip('|') #Strip off any leading or following '|' before constructing output line
                
            outputLine = '\t'.join(headLineArray)
            #print(outputLine)
            print(outputLine, file=outputFile)
            
            lineIndex = lineIndex+3 #skip over subtoken lines and go back to head of loop
            continue
    
        
    else: #If line doesn't have a composite token, just print it out as normal
        print(line.rstrip('\n'), file=outputFile)
        lineIndex = lineIndex+1
        
            
