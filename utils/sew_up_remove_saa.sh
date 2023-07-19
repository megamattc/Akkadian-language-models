for f in ./conllu_files/*.conllu; do
  python sew_up.py "$f"
done
