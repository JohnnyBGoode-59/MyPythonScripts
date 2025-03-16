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

import glob, re, os, sys
from crc32 import crc32
from EXIF_Dating import GetExifDate, GetFileDate, GetExifDimensions
from PyBackup import logging, ReadCrcs, recursive_mkdir, display_update
import porting

# the default destination for photo archives
archive_pictures = porting.abspath("~/Pictures")
picture_exts = ['.jpg', '.jpeg', '.heic', '.png']

# the default destination for video archives
archive_videos = porting.abspath("~/Videos")
video_exts = ['.avi', '.mp', '.mpg', '.mp3', '.mp4', '.mov', '.3gp', '.m4v']

months = [ "01Jan", "02Feb", "03Mar", "04Apr", "05May", "06Jun",
            "07Jul", "08Aug", "09Sep", "10Oct", "11Nov", "12Dec" ]

filespec = "*"  # which files get archived?
szFile = "file"
errors = {}
stats = {szFile:0}
log = None      # logging class instantiations
record = None

def help():
    print("""
    Photo-Backup [-r] [filespec]
    -r  recursively process folders

    This program moves files to pictures and videos folders based upon the
    date they were recorded. The Pictures and Videos environment variables
    can be modified to change the root folders used to archive files.""")
    exit()

def remove_file(src, dest, reason):
    """ Remove a source file that does not need to be backed up """
    global log, stats, errors
    try:
        # Don't try to remove a file when the new pathname is identical
        if src.lower() == dest.lower():
            return
        os.remove(src)
        log.error(errors, "removed {} file".format(reason), src)
        log.count(stats, "original file", dest)
    except:
        log.error(errors, "remove error", src)

def replace_destination(src, dest, reason):
    """ Replace a destination file with a source file for a specified reason """
    global log, stats, errors, record

    # Don't try to replace a file when the new pathname is identical
    if src.lower() == dest.lower():
        return
    try:
        if os.path.exists(dest):
            os.remove(dest)
            log.count(stats, "replaced {} file".format(reason), dest)
    except:
        log.error(errors, "remove error", src)
        return
    try:
        os.rename(src, dest)
        record.count(stats, "archived file", dest)
    except:
        log.error(errors, "rename error", src)

def archive(pn, recursive):
    """ Archive one picture or movie in its proper place """
    global archive_pictures, picture_exts
    global archive_videos, video_exts
    global months
    global log, stats, errors, szFile

    # Only archive some types of files
    rootp, ext = os.path.splitext(pn)
    rootp, fn = os.path.split(pn)
    if ext.lower() not in picture_exts + video_exts:
        log.count(stats, "ignored file", pn)
        return
    record.increment(stats, szFile)

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
        log.error(errors, "undated (not archived) file", pn)
        return

    # Archive pn using computed date
    year = date[0]
    month = months[int(date[1])-1]
    #dbg print("The date in {} is {}".format(fn, ymd))
    folder = porting.addpath(dir_archives, year, month)

    # A destination pathname has been computed
    # if it is the same as the source, we are done.
    backup_pn = porting.addpath(folder, fn)
    if pn.lower() == backup_pn.lower():
        return
    recursive_mkdir(folder)

    # Read the CRCs at the destination.
    # If a duplicate CRC exists then delete the source file and done
    crc = crc32(pn)
    crcs, last_modified = ReadCrcs(log, folder)
    if fn in crcs:
        if crc == crcs[fn]:
            remove_file(pn, porting.addpath(folder, fn), "duplicate")
            return

    # Try to archive a file simply by renaming it and done
    # That should work if the destination file is not currently present
    if not os.path.exists(backup_pn):
        replace_destination(pn, backup_pn, "new")
        return

    # Just because two identically named different files exist does not mean we are done.

    # Keep larger files
    if os.path.getsize(backup_pn) > os.path.getsize(pn):
        remove_file(pn, backup_pn, "smaller")
        return

    # Replace the backup files with higher resolution files
    # Remove lower resolution files
    src_dim = GetExifDimensions(pn)
    dest_dim = GetExifDimensions(backup_pn)
    update = False
    if src_dim is not None and dest_dim is not None:
        if dest_dim[0] < src_dim[0] and dest_dim[1] < src_dim[1]:
            replace_destination(pn, backup_pn, "low res")
        else:
            remove_file(pn, backup_pn, "low res")
        return

    # Replace files with no exif date if a date is now available
    src_date = GetExifDate(pn)
    dest_date = GetExifDate(backup_pn)
    if src_date is not None and dest_date is None:
        replace_destination(pn, backup_pn, "add date")
        return

    log.count(errors, "unarchived file", pn)
    return

def main(pn, recursive):
    """ Process files and possibly folders starting with a folder """
    found = 0

    # Process just the files in a folder
    for fn in glob.glob(porting.addpath(glob.escape(pn), filespec)):
        found += 1
        display_update(found, "found")
        if os.path.isfile(fn):
            archive(fn, recursive)

    # Process folders recursively, when requested
    if recursive:
        # Note that the saved filespec cannot be used here
        print("{}: scanning".format(pn))
        display_update(found, True)
        for pn in glob.glob(porting.addpath(glob.escape(pn), "*")):
            found += 1
            display_update(found, "found")
            if os.path.isdir(pn):
                main(pn, recursive)

if __name__ == '__main__':
    # Create a logfile
    log = logging("Photo-Backup.errors.txt")
    record = logging("Photo-Backup.log.txt")    # keep success out of the error log

    # Process the command line arguments
    folder = os.getcwd();   # <path>: use a path other than the current working directory
    recursive = False       # -r: recursively process subfolders
    for arg in sys.argv[1:]:
        pn = porting.abspath(arg)
        if arg[0] == '-':
            if arg[1].lower() == 'r':
                recursive = True
            else:
                help()
        elif os.path.isdir(pn):
            folder = pn
        else:
            folder, filespec = os.path.split(pn)
            if not os.path.isdir(folder):
                log.error(errors, "not a folder", folder)
                help()

    # Find and process folders
    display_update(0, True)
    main(folder, recursive)

    # Print the result
    log.msg("\nPhotoBackup complete")
    stats.pop(szFile)
    log.counters(stats)
    log.counters(errors)
