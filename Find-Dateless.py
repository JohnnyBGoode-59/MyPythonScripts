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

filespec = '*'

def Finder(pn, recursive):
    """ Check a file or folder for files with no date """
    global filespec

    if os.path.isdir(pn):
        # find files
        for fn in glob.glob(pn + '\\' + filespec):
            if os.path.isfile(fn):
                Finder(fn, recursive)

        # perform recursion
        if recursive:
            for fn in glob.glob(pn + "\\*"):
                if os.path.isdir(fn):
                    Finder(fn, recursive)
    else:
        # Each file is processed here
        path, ext = os.path.splitext(pn)
        if ext.lower() in [".jpg", ".jpeg"]:
            if GetExifDate(pn) is None:
                print("{}".format(pn))

def main(pn, recursive):
    """ Find files with no date in a set of files and folders """
    global filespec

    if os.path.isdir(pn):
        Finder(pn, recursive) # CRC all files in a folder
    else:
        pn, filespec = os.path.split(pn)
        Finder(pn, recursive) # use a modified filespec

if __name__ == '__main__':
    """ Find-Dateless [-r] [{filenames}]
        -r  Recursively process subfolders
    """
    path = os.getcwd(); # <path>: use a path other than the current working directory
    recursive = False

    for arg in sys.argv[1:]:
        if arg[0] == '-':
            if arg[1].lower() == 'r':
                recursive = True
        else:
            path = os.path.abspath(arg)

    main(path, recursive)
