#-------------------------------------------------------------------------------
# Name: Photo-Backup
# Purpose: Backup photos and videos based upon the date they were recorded
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
video_exts = ['.avi',  '.mpg',  '.mp3',  '.mp4', '.mov',  '.3gp']

months = [ "01Jan", "02Feb", "03Mar", "04Apr", "05May", "06Jun",
            "07Jul", "08Aug", "09Sep", "10Oct", "11Nov", "12Dec" ]

found = 0       # Count files found
archived = 0    # Count files archived
not_archived = 0 # Count files that could not be archived
removed = 0     # Count files removed due to matching CRC
filespec = "*"  # which files get archived?

import glob, re, os, sys
from crc32 import crc32
from EXIF_Dating import GetExifDate, GetFileDate, GetExifDimensions
from PyBackup import ReadCrcs, recursive_mkdir

def remove_duplicate(src, dest):
    """ Remove a source file that does not need to be backed up """
    global archived, removed, not_archived
    try:
        os.remove(src)
        print("{} removed as a duplicate of {}".format(src, dest))
        removed += 1
    except:
        print("exception: {} cannot be removed ".format(src))
        not_archived += 1

def replace_destination(src, dest, reason):
    """ Replace a destination file with a source file for a specified reason """
    global archived, not_archived
    try:
        os.remove(dest)
    except:
        print("{}: cannot remove ".format(dest))
        not_archived += 1
        return
    try:
        os.rename(src, dest)
        archived += 1
        print("{} replaced: {}".format(dest, reason))
    except:
        print("{} cannot rename to {}".format(src, dest))
        not_archived += 1

def archive(pn, recursive):
    """ Archive one picture or movie in it's proper place """
    global archive_pictures, picture_exts
    global archive_videos, video_exts
    global months, found, archived, not_archived, removed

    # Only archive some types of files
    rootp, ext = os.path.splitext(pn)
    rootp, fn = os.path.split(pn)
    if ext.lower() not in picture_exts + video_exts:
        print("{}: ignoring this type of file".format(pn))
        return
    found = found + 1

    # Decide where to archive the file
    if ext.lower() in picture_exts:
        date = GetExifDate(pn)
        dir_archives = archive_pictures
    elif ext.lower() in video_exts:
        # fn is correct for this function
        date = GetFileDate(fn)
        dir_archives = archive_videos
    else:
        date = None
    if date is None:
        print("{}: No archive date".format(pn))
        not_archived += 1
        return

    # Archive pn using computed date
    year = date[0]
    month = months[int(date[1])-1]
    #dbg print("The date in {} is {}".format(fn, ymd))
    folder = dir_archives + '\\' + year + '\\' + month
    recursive_mkdir(folder)

    # Read the CRCs at the destination.
    # If a duplicate CRC exists then delete this file
    crc = crc32(pn)
    crcs, last_modified = ReadCrcs(folder+"\\crc.csv")
    backup_pn = folder + '\\' + fn
    for crcfn in crcs:
        if crc == crcs[crcfn]:
            remove_duplicate(pn, folder+'\\'+crcfn)
            return

    # Try to archive a file simply by renaming it
    if not os.path.exists(backup_pn):
        os.rename(pn, backup_pn)
        print("{} archived to {}".format(pn, folder))
        archived = archived + 1
        return

    # Just because the files are named the same yet different does not mean we are done.

    # Replace the backup files with higher resolution files
    # Remove lower resolution files
    src_dim = GetExifDimensions(pn)
    dest_dim = GetExifDimensions(backup_pn)
    update = False
    if src_dim is not None and dest_dim is not None:
        if dest_dim[0] < src_dim[0] and dest_dim[1] < src_dim[1]:
            replace_destination(pn, backup_pn, "Improve resolution")
        else:
            remove_duplicate(pn, backup_pn)
        return

    # Replace files with no exif date if a date is now available
    src_date = GetExifDate(pn)
    dest_date = GetExifDate(backup_pn)
    if src_date is not None and dest_date is None:
        replace_destination(pn, backup_pn, "add date")
        return

    print("{} could not be archived to {}".format(pn, folder))
    not_archived = not_archived + 1
    return

def getfolder(folder, filetype):
    """ Pick which folder to use to archive files of a particular file type """

    # The returned value must be on the same drive because rename is used
    folder = os.path.abspath(folder)
    drive = folder[0:2].upper()

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

def main(pn, recursive):
    """ Process files and possibly folders starting with a folder """

    # Process just the files in a folder
    for fn in glob.glob(glob.escape(pn) + '\\' + filespec):
        if os.path.isfile(fn):
            archive(fn, recursive)

    # Process folders recursively, when requested
    if recursive:
        # Note that the saved filespec cannot be used here
        for pn in glob.glob(glob.escape(pn) + "\\*"):
            if os.path.isdir(pn):
                main(pn, recursive)

def help():
    print("Photo-Backup [-r] [filespec]")
    print("\nThis program moves files to pictures and videos folders based")
    print("upon the date they were recorded.")
    print("\n-r\trecursively process folders")
    exit()

if __name__ == '__main__':
    # Process the command line arguments
    folder = os.getcwd();   # <path>: use a path other than the current working directory
    recursive = False       # -r: recursively process subfolders
    for arg in sys.argv[1:]:
        if arg[0] in ['-', '/']:
            if arg[1].lower() == 'r':
                recursive = True
            else:
                help()
        elif os.path.isdir(arg):
            folder = arg
        else:
            folder, filespec = os.path.split(arg)
            folder = os.path.abspath(arg)

    # Define the alternative locations to archive pictures and movies
    archive_pictures = getfolder(folder, 'Pictures')
    archive_videos = getfolder(folder, 'Videos')

    # Find and process folders
    main(folder, recursive)

    # Print the result
    print("Found {:,}, archived {:,}, removed {:,}, {:,} could not be archived".format(found, archived, removed, not_archived))
