#-------------------------------------------------------------------------------
# Name: SimpleNote.py
# Purpose: Split SimpleNote files up into multiple Json files
# Author: John Eichenberger
#-------------------------------------------------------------------------------

import glob, os, sys, tempfile, json

active = 'activeNotes'
trashed = 'trashedNotes'

def main(pn):
    """ Open a SimpleNote Json file and split it into one file per tag. """
    with open(pn) as f:
        data = json.load(f)
    rootp, fn = os.path.split(pn)
    os.chdir(rootp)

    # Create a list of tags
    tags = []
    for note in data[active]:
        if 'tags' in note:
            t = note['tags'][0]
            if not t in tags:
                tags += [t]

    # For each tag, create a new file containing just the notes for those tags
    for tag in tags:
        newdata = { active:[], trashed:[] }

        # Extract notes for each tag
        for note in data[active]:
            if 'tags' in note:
                if tag == note['tags'][0]:
                    newdata[active] += [note]

        # Create a file
        fn = tag+".json"
        if not os.path.exists(fn):
            print("Creating {}".format(fn))
            newContent = json.dumps(newdata, indent=4)
            with open(fn, "w") as outfile:
                outfile.write(newContent)
        else:
            print("not replacing {}".format(fn))
        pass
    pass

if __name__ == '__main__':
    count = 0

    for arg in sys.argv[1:]:
        main(os.path.abspath(arg))
        count += 1

    if count == 0:
        os.chdir('C:\\Users\\janita\\Documents\\Archive\\SimpleNote')
        main(os.path.abspath("notes.json"))
