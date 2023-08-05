#-------------------------------------------------------------------------------
# Name: Music-Renamer
# Purpose:  Rename MP3 files based upon the tag data for those files.
#
# Author: John Eichenberger
#
# Created:     08/07/2021
# Copyright:   (c) John Eichenberger 2021
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

found = 0
renamed = 0

import glob, re, os, sys, time
from random import randint
from math import log

# !pip install mutagen
from mutagen.mp3 import MP3

rename_list = []

def normalize_filename(rootp, fn):
    """ Strip any characters not allowed in a MS-DOS filename """
    for exclude in '"*+,/:;<=>?\\[]|':
        fn = fn.replace(exclude,'-')
    return os.path.abspath(rootp + '\\' + fn)

def get_names(pn):
    """ Return the filename, title, and artist for an MP3 file """
    tags = MP3(pn)

    try:
        title = tags['TIT2'][0][0:40] # limit to 40 characters
    except:
        title = 'unknown'

    try:
        artist = '(' + tags['TPE1'][0][0:30] + ')' # limit to 30 characters
    except:
        artist = '(unknown)'

    return [pn, title, artist]

def main():
    pass

if __name__ == '__main__':
    """ Process command line arguments """
    pn = os.getcwd();   # <path>: use a path other than the current working directory
    filespec = '*.mp3'  # file
    namespec = 'rta'    # Default naming specification: r=random numbers, s=sequential numbers, t=title, a=author

    # Parse the command line
    for arg in sys.argv[1:]:
        if arg[0] == '-':
            sw = arg[1].lower()
            if sw in 'arst':
                namespec = arg[1:]
            else:
                print(  "<filespec> defines which files to rename"
                        "-namespec: any of 'rsat;\n"
                        "    r: random number\n"
                        "    s: sequential number\n"
                        "    a: artist\n"
                        "    t: title\n")
                exit()
        else:
            pn = os.path.abspath(arg)
            if not os.path.isdir(pn):
                pn, filespec = os.path.split(pn)

    # Find files and get the names for them all
    if os.path.isdir(pn):
        for fn in glob.glob(os.path.abspath(pn + '\\' + filespec)):
            if os.path.isfile(fn):
                found = found + 1
                rename_list += [get_names(fn)]
    else:
        print("{} is not a folder".format(pn))

    # Rename those files
    number = 1
    fill = int(log(len(rename_list), 10)+1)
    while(len(rename_list)):
        # pop the first item or a random item
        if namespec[0] == 'r':
            item = randint(0, len(rename_list)-1)
        else:
            item = 0
        name = rename_list.pop(item)

        # Construct the old and new names
        oldname = name[0]
        rootp, ext = os.path.splitext(oldname)
        rootp, fn = os.path.split(oldname)
        newname = ''
        for c in namespec:
            if c == 'r' or c == 's':
                newname = newname + str(number).zfill(fill) + ' '
            elif c == 't':
                newname = newname + name[1]
            elif c == 'a':
                newname = newname + name[2]
        newname = normalize_filename(rootp, newname + ext)

        # Rename the file
        try:
            os.rename(oldname, newname)
            renamed = renamed + 1
            print("{} renamed {}".format(oldname, newname))
        except:
            print("{} cannot be renamed {}".format(oldname, newname))
        number += 1

    print("Found {}, renamed {}".format(found, renamed))
