#-------------------------------------------------------------------------------
# Name: Camera-Backup
# Purpose: Backup photos based upon the date of those photos
#
# Author: John Eichenberger
#
# Created:     12/08/2020
# Copyright:   (c) John Eichenberger 2020
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

dir_archives = "\\Pictures" # the default destination for photo archives
archive_exts = ['.jpg', '.jpeg',  '.avi',  '.bmp',  '.mpg',  '.mp3',  '.mp4',
                '.mov',  '.heic',  '.png',  '.3gp']
months = [ "01Jan", "02Feb", "03Mar", "04Apr", "05May", "06Jun",
            "07Jul", "08Aug", "09Sep", "10Oct", "11Nov", "12Dec" ]

found = 0
archived = 0
removed = 0 # files with matching CRC are removed

import glob, re, os, sys
from crc32 import crc32

from EXIF_Dating import GetExifDate, GetFileDate

def make_path(pn):
    """ Create all folders required to create a full pathname to a folder """
    # if the folder already exists, we are done without doing a thing
    if os.path.exists(pn):
        return

    # Find the parent pathname, abort if that is not possible
    rootp = os.path.split(pn)
    if len(rootp) != 2:
        return

    # Create the parent folder if it does not yet exist
    if not os.path.exists(rootp[0]):
        make_path(rootp[0])

    # Create the child folder
    os.mkdir(pn)
    return

def archive(pn, useFileDate, recursive):
    """ Archive one picture or movie in it's proper place """
    global dir_archives, archive_exts, months, found, archived, removed

    # Optionally process folders recursively
    if os.path.isdir(pn):
        if recursive:
            for fn in glob.glob(pn + "\\*"):
                archive(fn, useFileDate, recursive)
        return

    # only archive some types of files
    path, ext = os.path.splitext(pn)
    if ext.lower() not in archive_exts:
        print("Not archiving {}".format(pn))
        return
    found = found + 1

    # Decide where to archive the file
    date = GetExifDate(pn)
    if date is None:
        if useFileDate:
            rootp, fn = os.path.split(pn)
            date = GetFileDate(fn)
    if date is not None:
        year = date[0]
        month = months[int(date[1])-1]
        #dbg print("The date in {} is {}".format(fn, ymd))
        folder = dir_archives + '\\' + year + '\\' + month
    else:
        print("No date found to archive {}".format(pn))
        return

    make_path(folder)
    rootp, fn = os.path.split(pn)
    try:
        os.rename(pn, folder + '\\' + fn)
        archived = archived + 1
    except:
        if crc32(pn) == crc32(folder + '\\' + fn):
            os.remove(pn)
            removed += 1
            print("{} removed as a duplicate".format(pn))
        else:
            print("{} could not be archived to {}".format(pn, folder))
        return
    print("{} archived to {}".format(pn, folder))

def main(pn, useFileDate, recursive):
    global dir_archives

    # Archive to "%Pictures%" when it is defined
    home = os.environ.get('Pictures')
    if home is None:
        # Or archive to ~/Photos
        home = os.environ.get('USERPROFILE')
        if home is not None:
            home += '\\Pictures'
    if home is not None:
        home = os.path.expandvars(home)
        if not os.path.exists(home):
            home = None

    # archiving is performed using a rename, to another place on the same drive
    dir_archives = "\\Pictures" # the default destination for photo archives

    # Archive to the home folder defined above if it is on the same drive
    # Otherwise use the program default location which has no drive letter
    if home is not None and home[:2].lower() == pn[:2].lower():
        dir_archives = home

    # Start archiving a folder or a file
    archive(pn, useFileDate, recursive) # a file

if __name__ == '__main__':
    """ Process command line arguments """
    filespec = os.getcwd(); # <path>: use a path other than the current working directory
    useFileDate = False     # -f: use a filename date when no exif date is available
    recursive = False       # -r: recursively process subfolders
    for arg in sys.argv[1:]:
        if arg[0] == '-':
            if arg[1].lower() == 'f':
                useFileDate = True
            elif arg[1].lower() == 'r':
                recursive = True
        elif os.path.isdir(arg):
            filespec = os.path.abspath(arg)

    # Convert a single filespec to a set of files
    if os.path.isdir(filespec):
        filespec = filespec + "\\*" # process every file in a top level folder
    for pn in glob.glob(filespec):
        main(pn, useFileDate, recursive)

    # Print the result
    print("Found {}, archived {}, and removed {}".format(found, archived, removed))
