#-------------------------------------------------------------------------------
# Name: Find-Dateless
# Purpose: Find jpeg files that do not have any EXIF date within
#
# Author: John Eichenberger
#
# Created:     23/08/2020
# Copyright:   (c) John Eichenberger 2020
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import glob, os, sys

from EXIF_Dating import GetExifDate

def Finder(pn, recursive):
    """ Check a file or folder for files with no date """
    if os.path.isdir(pn):
        # One folder deep is ok
        for fn in glob.glob(pn + "\\*"):
            # But recursion requires -r
            if not os.path.isdir(fn) or recursive:
                Finder(fn, recursive)
    else:
        # Each file is processed here
        path, ext = os.path.splitext(pn)
        if ext.lower() in [".jpg", ".jpeg"]:
            if GetExifDate(pn) is None:
                print("{}".format(pn))

def main(filespec, recursive):
    """ Find files with no date in a set of files and folders """
    if os.path.isdir(filespec):
        Finder(filespec, recursive) # CRC all files in a folder
    else:
        for pn in glob.glob(filespec):
            Finder(pn, recursive) # CRC all files in a filespec

if __name__ == '__main__':
    """ Find-Dateless {filenames}
        -r  Recursively process subfolders
    """
    recursive = False

    for arg in sys.argv[1:]:
        if arg[0] == '-':
            if arg[1].lower() == 'r':
                recursive = True
        else:
            main(os.path.abspath(arg), recursive)
