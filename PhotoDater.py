#-------------------------------------------------------------------------------
# Name: PhotoDater
# Purpose:  Add EXIF date information for to photos.
#
# Author: John Eichenberger
#
# Created:     15/03/2025
# Copyright:   (c) John Eichenberger 2025
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import glob, re, os, sys, time

from EXIF_Dating import GetExifDate, SetExifDate, GetFileDate
from Logging import logging, display_update
from JsonFile import JsonFile

szFile = "file"
stats = {szFile:0}
errors = {}
log = None

filespec = '*'              # can be changed by the command prompt
picture_exts = ['.jpg', '.jpeg',  '.heic', '.png']

def help():
    print("""
    PhotoDater [options] [filespec]
    Add exif date data to files.
    -r  Recursively process subfolders
    -n  Deduce the date from the filename
    -m  Deduce the date from the file modification date""")

def date_format(mts):
    """ Create a list of strings from a timestamp: [YYYY, MM, DD, HH, MM, SS] """
    return [str(mts.tm_year), ("0" + str(mts.tm_mon))[-2:], ("0" + str(mts.tm_mday))[-2:],
            ("0" + str(mts.tm_hour))[-2:], ("0" + str(mts.tm_min))[-2:], ("0" + str(mts.tm_sec))[-2:]]

def process(pn, how='j'):
    """ Add exif data to one file.
        Google Takeout can provide Json files with the date information.
    """
    global picture_exts
    global log, stats, errors, szFile

    # Just in case...
    if os.path.isdir(pn):
        return

    # Define filename pattern matching first
    sep = "[\\-\\._~ ]*?" # optional separators: the dash has to be escaped
    rootp, ext = os.path.splitext(pn)
    rootp, fn = os.path.split(pn)

    # Avoid processing non-picture files
    if ext.lower() not in picture_exts:
        return
    log.increment(stats, szFile)
    display_update(stats[szFile], szFile)
    file_date = GetExifDate(pn)
    check_date = None

    # If a file is already dated, skip over it
    if not file_date == None:
        return

    # Find out if there is a matching Json file for the picture file.
    # If so, pull a timestamp from that file.
    if how == 'j':
        for jfn in glob.glob(os.sep.join([glob.escape(rootp), fn+".supplem*.json"])):
            try:
                jf = JsonFile(jfn)
                mydict = jf.read()
                timestamp = time.localtime(int(mydict['photoTakenTime']['timestamp']))
                file_date = date_format(timestamp)
                break
            except:
                log.error(stats, "Json file is missing a date", jfn)

        if file_date == None:
            log.error(stats, "No Json file date found", pn)
            return

    elif how == 'n':
        # Get a file date either from the filename or the parent folder name
        # Returns a list of [YYYY, MM, DD, HH, MM, SS], all text string numbers.
        file_date = true_file_date = GetFileDate(fn)
        if file_date is None:
            file_date = GetFileDate(pn.split('\\')[-2])

    elif how == 'm':
        # Use the file modification date when requested to do so
        modt = os.path.getmtime(pn) # create time epoch for date
        timestamp = time.localtime(modt)
        file_date = date_format(timestamp)


    # Time to set a file date
    # so set the EXIF date using the file date
    try:
        SetExifDate(pn, file_date)
        check_date = GetExifDate(pn)
        if check_date is not None and check_date[0:3] == file_date[0:3]:
            log.count(stats, "added Exif date", pn)
        else:
            log.count(errors, "failed adding Exif date", pn)
    except:
        log.count(errors, "SetExifDate exception", pn)

    # If the two dates match, do nothing
    if file_date is not None and check_date is not None:
        # Just compare dates, not times
        if (file_date[:3] == check_date[:3]):
            log.count(stats, "well named and dated picture", pn, silent=True)
            return

def main(pn, recursive, method):
    """ Add date info to files in a folder, possibly recursively """
    global filespec

    # Process files in a folder with no recursion
    for fn in glob.glob(glob.escape(pn) + os.sep + filespec):
        if os.path.isfile(fn):
            process(fn, method)

    # Process folders recursively, when requested
    if recursive:
        # Note that the saved filespec cannot be used here
        for pn in glob.glob(glob.escape(pn) + os.sep + '*'):
            if os.path.isdir(pn):
                main(pn, recursive, method)

if __name__ == '__main__':
    """ Process command line arguments """
    log = logging()
    pn = os.getcwd()    # <path>: use a path other than the current working directory
    recursive = False   # -r: recursively process subfolders
    method = 'j'

    for arg in sys.argv[1:]:
        if arg[0] == '-':
            if arg[1].lower() == 'r':
                recursive = True
            elif arg[1].lower() in ['n', 'm']:
                method = arg[1].lower()
            else:
                help()
        else:
            pn = os.path.abspath(os.path.expandvars(os.path.expanduser(arg)))
            if not os.path.isdir(pn):
                pn, filespec = os.path.split(pn)
                if not os.path.isdir(pn):
                    log.error(errors, "folder error", pn)
                    help()

    main(pn, recursive, method)
    log.counters(stats)
    log.counters(errors)
