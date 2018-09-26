# Copyright Marco Inacio 2018
# Licensed under GNU GPL 3 https://www.gnu.org/licenses/gpl-3.0.en.html

import urllib.request
import shutil
import re
import os
import csv

# Set the location where the csv file is
fname = "export_list_8397eng.csv"

# Set audio language
audio_language = "hun"

# What must we do with duplicated sentences (multiple translations)?
# Options:
# "merge" to keep one card with all translations merged on it
# "remove" to keep only a single card with a single translation
# "nothing" to keep all duplicated cards
duplicates = "merge"

# Instructions:
# download your list in CSV format on the Tatoeba website
# enable id and translation while downloading and the run this script.
# Once the script is finshed, you will have a file with the same
# name of the original one plus a suffix "_with_audio_tatoeba.csv"
# and an audio folder "audio_files" on the same directory
# of the original file.
# Import this new csv file to using Anki menu "File > Import..."
# and move the audio files (not the folder) into the
# "collection.media" folder on your Anki profile data directory
# (in Linux this folder might be located at
# /home/your_username/.local/share/Anki2/User\ 1


# Read CSV file
with open(fname) as f:
    cards = csv.reader(f, delimiter='\t', quotechar='"')
    cards = [list(card) for card in cards]

# Get path of the CSV file
path_csv_file = os.path.dirname(fname)

# Create dir to store audio files
try:
    os.mkdir(os.path.join(path_csv_file, "audio_files"))
except FileExistsError:
    pass

tatoeba_id = None
no_cards_removed = 0
for i in range(len(cards)):
    print("Proccessing card", i+1, "out of", len(cards))
    i -= no_cards_removed
    new_tatoeba_id = cards[i][0]
    if re.match('^\d+$', new_tatoeba_id) is None:
        raise("Unable to parse sentence id. Did you enable sentece id?")

    if new_tatoeba_id == tatoeba_id:
        if duplicates == "remove":
            cards.pop(i)
            no_cards_removed += 1
            print("Removed a duplicated card")
            continue
        elif duplicates == "merge":
            cards[i-1][2] += " " + cards[i][2]
            cards.pop(i)
            no_cards_removed += 1
            print("Merged a duplicated card")
            continue
        elif duplicates == "nothing":
            print("Keeping a duplicated card")
        else:
            raise("invalid duplicate variable")



    tatoeba_id = new_tatoeba_id

    mp3_uname = str(tatoeba_id) + ".mp3"
    mp3_fname = "tatoeba_" + mp3_uname
    mp3_fname_plus_path = os.path.join(path_csv_file, "audio_files",
        mp3_fname)

    url = "https://audio.tatoeba.org/sentences/"
    url += audio_language + "/" + mp3_uname

    if not os.path.isfile(mp3_fname_plus_path):
        try:
            with urllib.request.urlopen(url) as response:
                with open(mp3_fname_plus_path, 'wb') as mp3_stream:
                    shutil.copyfileobj(response, mp3_stream)
        except urllib.request.HTTPError:
            print("Notice: could not find audio fo Tatoeba sentence",
                  url)
            cards[i][0] = ''
            continue

    cards[i][0] = '[sound:' + mp3_fname + ']'

with open(fname + "_with_audio_tatoeba.csv", 'w') as f:
    cards = ['"'+'"\t"'.join(card)+'"' for card in cards]
    f.write('\n'.join(cards))

