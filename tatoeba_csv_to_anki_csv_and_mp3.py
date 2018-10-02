# Copyright Marco Inacio 2018
# Licensed under GNU GPL 3 https://www.gnu.org/licenses/gpl-3.0.en.html

# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

# This is script works natively with Python 3 on
# and should also work with lastest Python 2.7 (except on Windows)
from __future__ import print_function

try:
    try:
        from urllib.request import urlopen
        from urllib.request import HTTPError
        dir_error = FileExistsError
        openf = open
    except ImportError:
        from urllib2 import urlopen
        from urllib2 import HTTPError
        dir_error = OSError
        input = raw_input
        openf = lambda file, mode='r', encoding='': open(file, mode)
    import shutil
    import re
    import os
    import csv

    import platform
    if platform.system() == "Windows":
        # Workaround since Python does not work with Let's Encrypt certs
        # on Windows yet.
        import ssl
        if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
            getattr(ssl, '_create_unverified_context', None)):
            ssl._create_default_https_context = ssl._create_unverified_context


    print("""
    ----------- Instructions ------------

    download your list in CSV format on the Tatoeba website,
    enable id and translation while downloading and the run this script.
    Once the script is finshed, you will have a file with the same
    name of the original one plus a suffix "_with_audio_tatoeba.csv"
    and an audio folder "audio_files" on the same directory
    of the original file.

    Import this new csv file to using Anki menu "File > Import..."
    and move the audio files (not the folder itself) into the
    "collection.media" folder of your Anki profile data directory

    You can find your Anki profile folder by openining Anki, then
    Tools > Preferences, open tab backup and then clicking
    "Open backup folder"
    It will open the file explorer, you need to go one folder up and
    then to folder "collection.media"

    On Linux this folder might be located at
    /home/your_username/.local/share/Anki2/User\ 1
    """)

    # Set the location where the csv file is
    fname = ""

    # Set audio language
    audio_language = ""

    # What must we do with duplicated sentences (multiple translations)?
    # Options:
    # "merge" to keep one card with all translations merged on it
    # "remove" to keep only a single card with a single translation
    # "nothing" to keep all duplicated cards
    duplicates = ""

    while fname == "":
        print("Type the name of the csv file then press ENTER.")
        print("The name must contain the file extension.")
        print("Example: export_list_8397eng.csv")
        fname = input("")

    while audio_language == "":
        print("Type the acronym of language in which you want the",
              "audio to be")
        print("Example: hun")
        audio_language = input("")

    while duplicates == "":
        print("Type what to do with duplicated translations.")
        print("Options:")
        print("merge: to keep one card with all translations merged on it")
        print("remove: to keep only a single card with a single translation")
        print("nothing: to keep all duplicated cards")
        print("Example: merge")
        duplicates = input("")
        if duplicates != "merge" and duplicates != "remove" and duplicates != "nothing":
            print("Invalid option! Must be either merge, remove or nothing")
            duplicates = ""



    # Read CSV file
    with openf(fname, encoding="utf8") as f:
        cards = csv.reader(f, delimiter='\t', quotechar='"')
        cards = [list(card) for card in cards]

    # Get path of the CSV file
    path_csv_file = os.path.dirname(fname)

    # Create dir to store audio files
    try:
        os.mkdir(os.path.join(path_csv_file, "audio_files"))
    except dir_error:
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
                with urlopen(url) as response:
                    with open(mp3_fname_plus_path, 'wb') as mp3_stream:
                        shutil.copyfileobj(response, mp3_stream)
            except HTTPError:
                print("Notice: could not find audio for Tatoeba sentence",
                      url)
                cards[i][0] = ''
                continue
        cards[i][0] = '[sound:' + mp3_fname + ']'

    with openf(fname + "_with_audio_tatoeba.csv", 'w', encoding="utf8") as f:
        cards = ['"'+'"\t"'.join(card)+'"' for card in cards]
        f.write('\n'.join(cards))

    print("Script finished sucefully!")
    input("Press ENTER to exit.")

except Exception as err:
    print("Script failed with error:\n\n", err)
    input("Press ENTER to exit.")
    raise err
