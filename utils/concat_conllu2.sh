#!/bin/bash

gsed -s -e $'$a\\\n' ./$1/*.conllu > Q003230Joined.conllu
#cat ./$1/*.conllu > akk_mcong-ud-$1.conllu
