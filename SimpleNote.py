#-------------------------------------------------------------------------------
# Name: SimpleNote.py
# Purpose: Split SimpleNote files up into multiple Json files
# Author: John Eichenberger
#-------------------------------------------------------------------------------

import glob, os, sys, tempfile, json

active = 'activeNotes'
trashed = 'trashedNotes'

def update(fn, newdata):
    """ Update (or create) a file with a set of notes.
        Note: The newdata gets saved which can cause previous notes to be removed.
    """

    # Read in the current file, if it exists
    report = None
    if os.path.exists(fn):
        with open(fn) as f:
            data = json.load(f)

        # Were any notes deleted?
        for note in data[active]:
            if not note in newdata[active]:
                report = "Removing notes from {}"
                break

        # Were any notes added?
        for note in newdata[active]:
            if not note in data[active]:
                report = "Adding notes to {}"
                break
    else:
        report = "Creating {}"

    if len(newdata[trashed]) > 0:
        newdata[trashed] = []
        emptymsg = "Emptying the trash from {}"
        if report == None:
            report = emptymsg
        else:
            print(emptymsg.format(fn))

    if report == None:
        return

    # (Re)Create a file
    print(report.format(fn))
    if os.path.exists(fn):
        os.remove(fn)
    newContent = json.dumps(newdata, indent=4)
    with open(fn, "w") as outfile:
        outfile.write(newContent)
    pass


def main(pn):
    """ Open a SimpleNote Json file and split it into one file per tag. """
    with open(pn) as f:
        try:
            data = json.load(f)
        except:
            print("Failed to load {}".format(pn))
            return
    rootp, fn = os.path.split(pn)
    os.chdir(rootp)

    # Create a list of tags
    tags = []
    newdata = { active:[], trashed:[] }
    for note in data[active]:
        if 'tags' in note:
            t = note['tags'][0]
            if not t in tags:
                tags += [t]
        else:
            # Remove untagged notes
            newdata[active] += [note]
    for note in newdata[active]:
        data[active].remove(note)
    update("untagged.json", newdata)

    # For each tag, create a new file containing just the notes for those tags
    for tag in tags:
        newdata = { active:[], trashed:[] }

        # Extract notes for each tag
        for note in data[active]:
            if tag == note['tags'][0]:
                newdata[active] += [note]
        for note in newdata[active]:
            data[active].remove(note)

        # Create a file
        update(tag+".json", newdata)
    update(fn, data)

if __name__ == '__main__':
    count = 0

    for arg in sys.argv[1:]:
        main(os.path.abspath(arg))
        count += 1

    if count == 0:
        main("C:\\Users\\janita\\Documents\\Archive\\SimpleNote\\notes.json")
