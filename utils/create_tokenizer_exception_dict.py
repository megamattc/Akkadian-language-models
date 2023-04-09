import json

tokenizer_exceptions_extract_file = open("tokenizer_exceptions_extract.json",'r',encoding="utf-8")
tokenizer_exceptions_dict_file = open("tokenizer_exceptions_dict.json",'w',encoding="utf-8")

tokenizer_exceptions_extract_json = json.load(tokenizer_exceptions_extract_file)
#tokenizer_exceptions_dict_json = json.load(tokenizer_exceptions_dict_file)

tokenizer_dict = {}

for token in tokenizer_exceptions_extract_json.keys():
    orth = tokenizer_exceptions_extract_json[token][0]
    token_value = orth["ORTH"]
    tokenizer_dict.update({token:token_value})

print(tokenizer_dict,file=tokenizer_exceptions_dict_file)

