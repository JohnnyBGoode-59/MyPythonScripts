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

archive_pictures = "\\Pictures" # the default destination for photo archives
picture_exts = ['.jpg', '.jpeg',  '.heic',  '.png']

archive_videos = "\\Movies" # the default destination for movie archives
movie_exts = ['.avi',  '.mpg',  '.mp3',  '.mp4', '.mov',  '.3gp']

months = [ "01Jan", "02Feb", "03Mar", "04Apr", "05May", "06Jun",
            "07Jul", "08Aug", "09Sep", "10Oct", "11Nov", "12Dec" ]

crcs = {}       # a dictionary of previously backed up files

found = 0       # Count files found
archived = 0    # Count files archived
removed = 0     # Count files removed due to matching CRC
filespec = "\\*"# which files get archived?

import glob, re, os, sys
from crc32 import crc32

from EXIF_Dating import GetExifDate, GetFileDate

def read_crcs():
    global crcs

    # Read %Pictures%/crc.txt when it is present
    pn = os.environ.get('Pictures')
    if pn is None:
        # Or ~/Photos/Pictures/crc.txt
        pn = os.environ.get('USERPROFILE')
        if pn  is None:
            # Or /Pictures/crc.txt
            filespec = '\\Pictures'
    pn = os.path.expandvars(pn+"\\crc.txt")

    # Read the CRC file to create a dictionary
    if not os.path.isfile(pn):
        return
    f = open(pn)
    next(f) # skip header line
    for line in f:
        sline = line.split(',')
        crc = sline[0]
        sline = line.split('"')
        fn = sline[1]
        pn = sline[3]

        # Add one dictionary value per crc
        if crc not in crcs:
            crcs[crc] = [pn]
    f.close()

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

def archive(pn, recursive):
    """ Archive one picture or movie in it's proper place """
    global archive_pictures, picture_exts
    global archive_videos, movie_exts
    global months, found, archived, removed, crcs

    # Optionally process folders recursively
    if os.path.isdir(pn):
        if recursive:
            for fn in glob.glob(pn + filespec):
                if os.path.isfile(fn):
                    archive(fn, recursive)
            for fn in glob.glob(pn + '\\*'):
                if os.path.isdir(fn):
                    archive(fn, recursive)
        return

    # only archive some types of files
    rootp, ext = os.path.splitext(pn)
    rootp, fn = os.path.split(pn)
    if ext.lower() not in picture_exts + movie_exts:
        print("Not archiving {}".format(pn))
        return
    found = found + 1

    # If a duplicate CRC exists then delete this file
    crc = crc32(pn)
    if crc in crcs:
        if os.path.isfile(crcs[crc]):
            os.remove(pn)
            removed += 1
            print("{} removed as a duplicate".format(pn))

    # Decide where to archive the file
    if ext.lower() in picture_exts:
        date = GetExifDate(pn)
        dir_archives = archive_pictures
    else:
        date = GetFileDate(fn)
        dir_archives = archive_videos
    if date is None:
        print("No date found to archive {}".format(pn))
        return

    # Archive pn using computed date
    year = date[0]
    month = months[int(date[1])-1]
    #dbg print("The date in {} is {}".format(fn, ymd))
    folder = dir_archives + '\\' + year + '\\' + month
    make_path(folder)
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

def getfolder(folder, filetype):
    """ Pick which folder to use to archive files of a particular file type """

    # The returned value must be on the same drive
    drive = folder[:2].upper()

    # Start by looking for an environment variable with the same name
    folder = os.environ.get(filetype)
    if folder is not None:
        folder = os.path.expandvars(folder)
        if folder[:2].upper() == drive:
            return folder

    # Next look for a folder under USERPROFILE
    folder = os.environ.get('USERPROFILE')
    if folder is not None:
        folder = os.path.expandvars(folder)
        if folder[:2].upper() == drive:
            return folder + '\\' + filetype

    # If all else fails, use a folder based upon the root with the same name
    return '\\' + filetype

def main():
    pass

if __name__ == '__main__':
    """ Process command line arguments """

    # Read in the CRCs of every file previously backed up
    read_crcs()

    # Process the command line arguments
    folder = os.getcwd();   # <path>: use a path other than the current working directory
    recursive = False       # -r: recursively process subfolders
    unique_filespec = False # only matters when -r and no folder specified
    for arg in sys.argv[1:]:
        if arg[0] == '-':
            if arg[1].lower() == 'r':
                recursive = True
        elif os.path.isdir(arg):
            folder = os.path.abspath(arg)
        else:
            filespec = '\\' + arg
            unique_filespec = True

    # Define the alternative locations to archive pictures and movies
    archive_pictures = getfolder(folder, 'Pictures')
    archive_videos = getfolder(folder, 'Videos')

    # Find and process files
    for pn in glob.glob(folder + filespec):
        archive(pn, recursive)
    if recursive and unique_filespec:
        archive(folder, recursive)

    # Print the result
    print("Found {}, archived {}, and removed {}".format(found, archived, removed))
