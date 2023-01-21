

#Check conllu format by checking if every line not a comment or empty line has ten entries split by tabs.

inputFile = open("akk_riao-ud-testConverted.conllu", 'r')

lines = inputFile.readlines()

for line in lines:
    line = line.rstrip('\n')
    #print(line)
    if len(line) == 0:
        continue
    elif "#" in line:
        continue
    elif len(line.split('\t')) != 10:
        print(line)
