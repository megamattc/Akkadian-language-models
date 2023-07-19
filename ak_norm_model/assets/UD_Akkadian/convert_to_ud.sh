#!/usr/bin/env

python convert_conllu_to_ud.py test
python convert_conllu_to_ud.py train
python convert_conllu_to_ud.py dev

python rollup_conllu_ud.py dev_ud
python rollup_conllu_ud.py test_ud
python rollup_conllu_ud.py train_ud   
