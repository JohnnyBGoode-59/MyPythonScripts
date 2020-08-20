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
        print("Add a date to {}".format(pn))
        SetExifDate(pn, file_date)
        dated = dated + 1
        return

    else:
        # If the two dates match, do nothing
        if file_date is not None:
            if (exif_date[:len(file_date)] == file_date):
                print("{} is well named".format(pn))
                return

    # Define the new prefix for the filename
    # prefix = d[0:4]+'-'+d[5:7]+'-'+d[8:10]+'_'+d[11:13]+'-'+d[14:16]+'-'+d[17:19]+'_' # yyyy-dd-mm_hhmmss_
    prefix = exif_date[0]+'-'+exif_date[1]+exif_date[2]+'_'+exif_date[3]+exif_date[4]+exif_date[5]+'_'

    # Don't rename a file that is already renamed (this should be redundant now)
    if fn[0:len(prefix)] == prefix:
        print("{} is already renamed".format(fn))
        return

    # Remove any previous date prefix
    m = re.search("^([0-9~_\-\.]*)(.*)", fn)
    if m is not None:
        fn = m.group(2)

    # Rename
    newname = prefix + fn
    os.rename(pn, rootp + '\\' + newname)
    renamed = renamed + 1
    print("{} renamed {}".format(pn, newname))

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
