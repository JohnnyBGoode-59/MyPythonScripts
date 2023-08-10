#-------------------------------------------------------------------------------
# Name: Photo-Renamer
# Purpose:  Rename photos based upon the EXIF date for those photos.
#   Add a EXIF date when the filename contains a date but the EXIF data is missing.
#
# Author: John Eichenberger
#
# Created:     12/08/2020
# Copyright:   (c) John Eichenberger 2020
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import glob, re, os, sys, time
from EXIF_Dating import GetExifDate, SetExifDate, GetFileDate
from Logging import logging, display_update

szFile = "file"
stats = {szFile:0}
errors = {}
log = None

filespec = '*'              # can be changed by the command prompt
use_modified_date = False   # -m: reset the date based upon the file date
picture_exts = ['.jpg', '.jpeg',  '.heic', '.png']

def help():
    print("""
    PhotoRenamer [options] [filespec]
    Rename files to include a datestamp in the filename.
    When add exif date data when it does not exist.

    -s  Strip any existing date found in the current filename
    -f  ignore existing exif data and use the date found in the Filename instead
    -m  use the Modified date if no other date is available
    -r  Recursively process subfolders""")

def rename(pn, strip, reset):
    """ Rename one file """
    global use_modified_date, picture_exts
    global log, stats, errors, szFile

    # Just in case...
    if os.path.isdir(pn):
        return

    # Define filename pattern matching first
    sep = "[\-\._~ ]*?" # optional separators: the dash has to be escaped
    rootp, ext = os.path.splitext(pn)
    rootp, fn = os.path.split(pn)

    # Avoid processing some files
    if ext.lower() in [".db", ".csv"]:
        return
    log.increment(stats, szFile)
    display_update(stats[szFile], szFile)

    if not strip:
        # Try to get both EXIF date and File date
        if reset:
            exif_date = None # ignore a bad EXIF date
        else:
            exif_date = GetExifDate(pn)

        # Get a file date either from the filename or the parent folder name
        file_date = true_file_date = GetFileDate(fn)
        if file_date is None:
            file_date = GetFileDate(pn.split('\\')[-2])

        # If the file has no EXIF date
        if exif_date is None:
            # and a file date is not available either
            if file_date is None:
                # Use the file modification date when requested to do so
                if use_modified_date:
                    modt = os.path.getmtime(pn) # create time epoch for date
                    mts = time.localtime(modt)
                    file_date = [ str(mts.tm_year),
                                ("0"+str(mts.tm_mon))[-2:],
                                ("0"+str(mts.tm_mday))[-2:],
                                ("0"+str(mts.tm_hour))[-2:],
                                ("0"+str(mts.tm_min))[-2:],
                                ("0"+str(mts.tm_sec))[-2:] ]
                else:
                    log.error(errors, "undated file", pn)
                    return

            # but a file date is available
            # so set the EXIF date using the file date
            if ext.lower() in picture_exts:
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
        if true_file_date is not None and exif_date is not None:
            # Just compare dates, not times
            if (exif_date[:3] == true_file_date[:3]):
                log.count(stats, "well named and dated picture", pn, silent=True)
                return

        # Use the file date if no exif date is available
        if exif_date is None:
            if true_file_date is None:
                exif_date = file_date # i.e. rename the file using the file name
            else:
                exif_date = true_file_date # or just use the file date

        # Define the new prefix for the filename
        prefix = exif_date[0]+'_'+exif_date[1]+exif_date[2]+'_'

        # Don't rename a file that is already renamed (this should be redundant now)
        if fn[0:len(prefix)] == prefix:
            log.count(stats, "well named file", pn, silent=True)
            return

        # Remove any previous date prefix
        if file_date is not None:
            date_group = '('+file_date[0]+sep+file_date[1]+sep+file_date[2]+')'
            m = re.search("^([A-Z])*?"+sep+date_group+"(.*)", fn)
            if m is not None and len(m.groups()) == 3:
                fn = m.group(3)     # 1=prefix, 2=date, 3=filename.ext
                if len(fn) <= 4:    # period in file extension may get stripped
                    if len(fn) < 4: # or perhaps the filename is just gone
                        fn = '.'+fn
                    prefix = prefix[:-1]
                else:
                    m = re.search("^([\-\._~ ])*(.*)", fn)
                    fn = m.group(2)
                log.count(stats, "truncated filename", fn, silent=True)
        else:
            # Strip any a prefix that has just the year
            m = re.search("^(19|20)[0-9][0-9]"+sep[:-1]+"(.*)", fn)
            if m is not None:
                fn = m.groups()[-1]

    else: # Simply strip the previous datestamps
        prefix = ""
        yyyy = "(19[0-9][0-9]|20[0-9][0-9])"+sep
        mm = dd = "([0-9][0-9])"+sep
        m = re.search("^("+yyyy+mm+dd+")(.*)", fn)
        while m is not None:
            fn = m.groups()[-1]
            m = re.search("^([\-\._~ ])*(.*)", fn)
            fn = m.group(2)
            m = re.search("^"+sep+"("+yyyy+mm+dd+")(.*)", fn)

    # Rename the file to match the date
    # If a matching file exists, add a number to make the new file unique
    for i in range(10): # limit of ten duplicates
        filename, ext = os.path.splitext(prefix+fn)
        if i == 0:
            number = ''
        else:
            number = '('+str(i)+')'
        newname = rootp + '\\' + filename + number + ext
        if pn == newname:
            break
        if os.path.isfile(newname):
            continue
        try:
            os.rename(pn, newname)
            log.count(stats, "renamed file", newname)
        except:
            log.error(errors, "rename failure", newname, silent=True)
        break

    if i > 9:
        log.error(errors, "rename limit failure", newname)

def main(pn, strip, reset, recursive):
    """ Rename files in a folder, possibly recursively """
    global filespec

    # Process files in a folder with no recursion
    for fn in glob.glob(glob.escape(pn) + '\\' + filespec):
        if os.path.isfile(fn):
            rename(fn, strip, reset)

    # Process folders recursively, when requested
    if recursive:
        # Note that the saved filespec cannot be used here
        for pn in glob.glob(glob.escape(pn) + "\\*"):
            if os.path.isdir(pn):
                main(pn, strip, reset, recursive)

if __name__ == '__main__':
    """ Process command line arguments """
    log = logging()
    pn = os.getcwd();   # <path>: use a path other than the current working directory
    strip = False       # -s: simply strip any date in the current filenames
    reset = False       # -f: ignore the EXIF date and use the filename date instead
    recursive = False   # -r: recursively process subfolders
    use_modified_date = False   # -m: reset the date based upon the file date

    for arg in sys.argv[1:]:
        if arg[0] in ['-', '/']:
            if arg[1].lower() == 's':
                strip = True
            elif arg[1].lower() == 'f':
                reset = True
            elif arg[1].lower() == 'r':
                recursive = True
            elif arg[1].lower() == 'm':
                use_modified_date = True
            else:
                help()
        else:
            pn = os.path.abspath(os.path.expandvars(arg))
            if not os.path.isdir(pn):
                pn, filespec = os.path.split(pn)
                if not os.path.isdir(pn):
                    log.error(errors, "folder error", pn)
                    help()

    # -f is ignored if -s is also supplied
    # one cannot strip date info from the filename and also use it
    if strip:
        reset = False

    main(pn, strip, reset, recursive) # rename all files in a folder
    log.counters(stats)
    log.counters(errors)
