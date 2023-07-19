#!/bin/bash

gsed -s -e $'$a\\\n' ./$1/*.csv > line_count.csv
#cat ./$1/*.conllu > akk_mcong-ud-$1.conllu
