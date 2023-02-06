import json

lte_dict = json.load(open("eval_dict_ltebab.json",'r'))
std_dict = json.load(open("eval_dict_stdbab.json",'r'))
old_dict = json.load(open("eval_dict_oldbab.json",'r'))
mbperi_dict = json.load(open("eval_dict_mbperi.json",'r'))
neo_dict = json.load(open("eval_dict_neobab.json",'r'))

general_dict = {"ltebab":lte_dict, "stdbab":std_dict,"oldbab":old_dict,"mbperi":mbperi_dict,"neobab":neo_dict}

output_file = open("eval_dict_general.json",'w')
print(general_dict, file=output_file)
