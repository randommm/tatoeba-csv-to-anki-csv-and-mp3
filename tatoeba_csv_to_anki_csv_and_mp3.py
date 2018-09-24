# Copyright Marco Inacio 2018
# Licensed under GNU GPL 3 https://www.gnu.org/licenses/gpl-3.0.en.html

import urllib.request
import shutil
import re
import os

# Set the location where the csv file is
fname = "export_list_8397eng.csv"
# Set audio language
audio_language = "hun"

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
    content = f.readlines()
cards = [x.strip() for x in content]

# Get path of the CSV file
path_csv_file = os.path.dirname(fname)

# Create dir to store audio files
try:
    os.mkdir(os.path.join(path_csv_file, "audio_files"))
except FileExistsError:
    pass


for i in range(len(cards)):
    print("Proccessing card", i+1, "out of", len(cards))
    try:
        tatoeba_id = re.search('\d+?\\t', cards[i]).group()[:-1]
        cards[i] = re.sub('\d+?\\t', "", cards[i], 1)
    except AttributeError:
        print("Warning: unable to get a sentence id")
        continue

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
            cards[i] = '""\t' + cards[i]
            continue

    cards[i] = '"[sound:' + mp3_fname + ']"\t' + cards[i]

with open(fname + "_with_audio_tatoeba.csv", 'w') as f:
    f.write('\n'.join(cards))

