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

found = 0
renamed = 0
dated = 0

import glob, re, os, sys

from EXIF_Dating import GetExifDate, SetExifDate, GetFileDate

def rename(pn, strip, reset):
    """ Rename one file """
    global found, renamed, dated
    found = found + 1

    # Define filename pattern matching first
    sep = "[\-\._~ ]*?" # optional separators: the dash has to be escaped
    rootp, fn = os.path.split(pn)

    if not strip:
        # Try to get both EXIF date and File date
        if reset:
            exif_date = None
        else:
            exif_date = GetExifDate(pn)
        file_date = GetFileDate(fn)

        # If the file has no EXIF date
        if exif_date is None:
            # but a file_date is available
            if file_date is None:
                print("{} has no date".format(pn))
                return

            # set the EXIF date
            try:
                SetExifDate(pn, file_date)
                print("Added date to {}".format(pn))
                dated = dated + 1
            except:
                print("{} cannot be updated".format(pn))
            return

        else:
            # If the two dates match, do nothing
            if file_date is not None:
                # Just compare dates, not times
                if (exif_date[:3] == file_date[:3]):
                    print("{} is well named".format(pn))
                    return

        # Define the new prefix for the filename
        prefix = exif_date[0]+'_'+exif_date[1]+exif_date[2]+'_'

        # Don't rename a file that is already renamed (this should be redundant now)
        if fn[0:len(prefix)] == prefix:
            print("{} is already renamed".format(fn))
            return

        # Remove any previous date prefix
        if file_date is not None:
            date_group = '('+file_date[0]+sep+file_date[1]+sep+file_date[2]+')'
            m = re.search("^([A-Z])*?"+sep+date_group+"(.*)", fn)
            if m is not None and len(m.groups()) == 3:
                fn = m.group(3)     # 1=prefix, 2=date, 3=filename.ext
                if len(fn) < 4:     # period in file extension may get stripped
                    fn = '.'+fn
                    prefix = prefix[:-1]
                else:
                    m = re.search("^([\-\._~ ])*(.*)", fn)
                    fn = m.group(2)
                #dbg print('Truncated filename: {}'.format(fn))

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
            renamed = renamed + 1
            print("{} renamed {}".format(pn, newname))
        except:
            print("{} cannot be renamed {}".format(pn, newname))
        break

    if i > 9:
        print("{} cannot be renamed {}".format(pn, newname))

def rename_everything(pn, strip, reset):
    """ find everything and archive all pictures and movies """
    if(os.path.isdir(pn)):
        for fn in glob.glob(pn + "\\*"):
            if(not os.path.isdir(fn)):
                rename(fn, strip, reset)
    else:
        print("{} is not a folder".format(pn))

def main(pn, strip, reset):
    global found, renamed
    rename_everything(pn, strip, reset)
    print("Found {}, renamed {}, and added dates to {}".format(found, renamed, dated))

if __name__ == '__main__':
    """ Process command line arguments """
    path = os.getcwd(); # <path>: use a path other than the current working directory
    strip = False       # -s: simply strip any date in the current filenames
    reset = False       # -r: reset the date based upon the current filenames

    # -r is ignored if -d is also supplied
    if strip:
        reset = False

    for arg in sys.argv[1:]:
        if arg[0] == '-':
            if arg[1].lower() == 's':
                strip = True
            elif arg[1].lower() == 'r':
                reset = True
        elif os.path.isdir(arg):
            path = arg

    main(path, strip, reset)
