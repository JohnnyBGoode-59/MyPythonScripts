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

def rename(pn):
    """ Archive one picture or movie in it's proper place """
    global found, renamed, dated
    found = found + 1

    # Try to get both EXIF date and File date
    exif_date = GetExifDate(pn)
    rootp, fn = os.path.split(pn)
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
    prefix = exif_date[0]+'-'+exif_date[1]+exif_date[2]+'_'

    # Don't rename a file that is already renamed (this should be redundant now)
    if fn[0:len(prefix)] == prefix:
        print("{} is already renamed".format(fn))
        return

    # Remove any previous date prefix
    if file_date is not None:
        sep = "[\-\._~ ]*?" # optional separators: the dash has to be escaped
        date_group = '('+file_date[0]+sep+file_date[1]+sep+file_date[2]+')'
        m = re.search("^([A-Z])*?_"+date_group+"(.*)", fn)
        if m is not None and len(m.groups()) == 3:
            fn = m.group(3)     # 1=prefix, 2=date, 3=filename.ext
            if len(fn) < 4:     # period in file extension may get stripped
                fn = '.'+fn
                prefix = prefix[:-1]
            if fn[0]=='_':
                fn = fn[1:]
            print('Truncated filename: {}'.format(fn))

    # Rename the file to match the date
    # If a matching file exists, add a number to make the new file unique
    for i in range(10): # limit of ten duplicates
        filename, ext = os.path.splitext(prefix+fn)
        if i == 0:
            number = ''
        else:
            number = '('+str(i)+')'
        newname = rootp + '\\' + filename + number + ext
        if(os.path.isfile(newname)):
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

def rename_everything(pn):
    """ find everything and archive all pictures and movies """
    if(os.path.isdir(pn)):
        for fn in glob.glob(pn + "\\*"):
            if(not os.path.isdir(fn)):
                rename(fn)
    else:
        print("{} is not a folder".format(pn))

def main(pn):
    global found, renamed
    rename_everything(pn)
    print("Found {}, renamed {}, and added dates to {}".format(found, renamed, dated))

if __name__ == '__main__':
    # if a command line parameter is supplied it is used
    # as the name of the folder to process
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main(os.getcwd())
