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
found = 0
archived = 0

import glob, re, os, sys

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

def archive(pn, useFileDate):
    """ Archive one picture or movie in it's proper place """
    global dir_archives, found, archived, archive_exts

    # only archive some types of files
    found = found + 1
    path, ext = os.path.splitext(pn)
    if ext.lower() not in archive_exts:
        print("Not archiving {}".format(pn))
        return

    # Decide where to archive the file
    months = [ "01Jan", "02Feb", "03Mar", "04Apr", "05May", "06Jun",
               "07Jul", "08Aug", "09Sep", "10Oct", "11Nov", "12Dec" ]
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
        print("{} could not be archived to {}".format(pn, folder))
        return
    print("{} archived to {}".format(pn, folder))

def archive_everything(pn, useFileDate):
    """ find everything and archive all pictures and movies """
    if(os.path.isdir(pn)):
        for fn in glob.glob(pn + "\\*"):
            if(not os.path.isdir(fn)):
                archive(fn, useFileDate)
    else:
        print("{} is not a folder".format(pn))

def main(pn, useFileDate):
    global dir_archives, found, archived

    # Archive to "%Photos%" when it is defined
    home = os.environ.get('Photos')
    if home is None:
        # Or archive to ~/Photos
        home = os.environ.get('USERPROFILE')
        if home is not None:
            home = home + '\\Pictures'
            if not os.path.exists(home):
                home = None

    # Archive to the home folder defined above if it is on the same drive
    # Otherwise use the program default location which has no drive letter
    if home is not None and home[:2].lower() == pn[:2].lower():
        dir_archives = home

    # Start archiving
    archive_everything(pn, useFileDate)
    print("Found {} and archived {}".format(found, archived))

if __name__ == '__main__':
    """ Process command line arguments """
    path = os.getcwd(); # <path>: use a path other than the current working directory
    useFileDate = False # -f: use a filename date when no exif date is available
    for arg in sys.argv[1:]:
        if arg[0] == '-':
            if arg[1].lower() == 'f':
                useFileDate = True
        elif os.path.isdir(arg):
            path = os.path.abspath(arg)

    main(path, useFileDate)
