import os
import shutil

directory = 'annotation'

destinationPath = os.getcwd() + '/' + 'conllu_transliterations'

for rootdir, dirs, files in os.walk(directory):
    for subdir in dirs:
        currentPath = os.getcwd() + '/' + directory + '/' + subdir
        subdirFiles = os.listdir(currentPath)
        adminFile = subdirFiles[0] #Only one file in these subdirectories, named admin.conllu

        filePrefix = subdir.strip('.txt')
        conlluFileName = filePrefix+'Transliteration.conllu'
        shutil.copyfile(currentPath + '/' + adminFile,destinationPath + '/' + conlluFileName)
