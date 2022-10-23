import os

FOLDER_PATH = "./test/files/"


def clean_files_folder():
    for file in os.listdir(FOLDER_PATH+"received"):
        if file != ".gitignore":
            os.remove(FOLDER_PATH+"received/"+file)
    for file in os.listdir(FOLDER_PATH+"square"):
        if file != ".gitignore":
            os.remove(FOLDER_PATH+"square/"+file)
