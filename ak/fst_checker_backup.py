#from spacy.lang.ak import Akkadian
#from spacy.language import Language
import json
from spacy.tokens import Doc

#@Language.factory("fst_checker")
#def make_fst_checker(nlp: Language, name: string):
#    return FSTChecker

class FSTChecker:

    file = open("eval_dict_general.json", 'r')
    lookup_dict = json.load(file)
    file2 = open("fst_comparison_log.txt",'w')

    dialect = "stdbab"

    def __init__(self, nlp, name: str = "fst_checker") -> None:


        self.name = name
        self.nlp = nlp
        #self.vocab = vocab
        #self.model = model
        #self.lookup_dict = lookup_dict

    def __call__(self, doc: Doc) -> Doc:
        result_doc = self.apply_fst_checker(doc)
        return result_doc


        # Define a function that compares a parse dictionary to a list of possible parse dictionaries of the same form and returns
        # the one that is 'closest'

    def apply_fst_checker(self, doc: Doc)-> Doc:

        dialect_dict = self.lookup_dict[self.dialect]  # Get appropriate dialect dictionary

        for token in doc:
            token_form = token.text  # Get str representation of token
            token_morph_dict = token.morph.to_dict()

            if token_form not in dialect_dict.keys():
                # If form isn't in lookup dict, don't change anything
                continue
            # Possibly correct only these forms, including X pos
            if token.pos_ in ["VERB", "ADJ", "NOUN", "X"]:

                list_of_parses = dialect_dict[token_form]
                suggested_parse_dict = token_morph_dict.items()
                suggested_parse_list = list(suggested_parse_dict)

                print("Token:",file=self.file2)
                print(token.text,file=self.file2)
                print("Suggested parse:",file=self.file2)
                print(suggested_parse_list,file=self.file2)
                print("list_of_parses",file=self.file2)
                print(list_of_parses,file=self.file2)

                # We want to skip updating tokens that spacy things are 3.m.s nouns in bound state because BabyFST often asserts these are nouns in th stative
                # Note here also the pesky alternation of NounStem and NounBase labels which we need to include. Hopefully this will be cleared up later
                if (token.pos_ == "NOUN") and (('NounStem', 'Bound') in token_morph_dict.items() or (
                'NounBase', 'Bound') in token_morph_dict.items()) and (
                        ('Gender', 'Masc') in token_morph_dict.items()) and (
                        ('Number', 'Sing') in token_morph_dict.items()):
                    continue

                # Array for storing size of intersections
                size_list = []
                # Array fo storing pos's of tokens
                pos_list = []
                for index in range(0, len(list_of_parses)):
                    parse = list_of_parses[index]

                    # If parse is empty dictionary, no reason to compare it
                    if len(parse) == 0:
                        continue

                    print("parse",file=self.file2)
                    print(parse,file=self.file2)

                    parse_pos = "X"  # Set pos of parse equal to X if parse does't have it

                    if "POS" in parse.keys():
                        parse_pos = parse["POS"]  # Get POS of token to compare against suggestions
                        parse.pop(
                            "POS")  # Pop the POS key-value pair so that t doesn't show up in the final annotations in the conllu file

                    # print("Post-pop")
                    # print(parse)
                    parse_list = list(parse.items())

                    print("parse_list:",file=self.file2)
                    print(parse_list,file=self.file2)
                    print("Intersection:",file=self.file2)
                    print("set(suggested_parse_list).intersection(parse_list))",file=self.file2)
                    print(set(suggested_parse_list).intersection(parse_list),file=self.file2)

                    size_list.append(len(set(suggested_parse_list).intersection(parse_list)))
                    pos_list.append(parse_pos)

                print("size_list",file=self.file2)
                print(size_list,file=self.file2)
                print("pos_list",file=self.file2)
                print(pos_list,file=self.file2)

                max_val = 0
                #Sometimes the list of recommended parses is empty, so we need to check if size_list = 0
                if len(size_list) > 0:
                    max_val = max(size_list)  # Get max size of intersection
                max_indices = [i for i in range(0, len(size_list)) if size_list[i] == max_val]

                print("max_indices",file=self.file2)
                print(max_indices,file=self.file2)

                # Get all parses with max intersection and same pos with token
                new_parse_list = []
                for i in max_indices:
                    # Check for parses with same pos tag assigned
                    if pos_list[i] == token.tag_:
                        new_parse_list.append(list_of_parses[i])

                likely_analysis = {}
                if len(new_parse_list) > 0:
                    # For now, just get the first element of list
                    likely_analysis = new_parse_list[0]
                # Otherwise, take first parse with max intersection regardless of pos type
                else:
                    #We also need to watch out for cases where list_of_parses consists only of the empty dictionary
                    # (b/c eval dictionary doesn't have a parse for it)
                    if len(max_indices) > 0:
                        #print("max_indices[0]")
                        #print(max_indices[0])
                        likely_analysis = list_of_parses[max_indices[0]]

                print("Likely analysis:",file=self.file2)
                print(likely_analysis,file=self.file2)

                # In the case that the suggested parse includes case feature but the likely analysis does not, we want to include it the final analysis
                if "Case" in token_morph_dict.keys() and "Case" not in likely_analysis.keys():
                    case_value = token_morph_dict["Case"]
                    likely_analysis.update({"Case": case_value})

                print("------------------",file=self.file2)

                token.set_morph(likely_analysis)
        return doc
