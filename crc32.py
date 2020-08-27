#-------------------------------------------------------------------------------
# Name: crc32
# Purpose: Compute the CRC32 for a set of files
#
# Author: John Eichenberger
#
# Created:     23/08/2020
# Copyright:   (c) John Eichenberger 2020
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import glob, os, sys, zlib

filespec = '*'  # By default all files are processed

def crc32(pn):
    """ Compute the CRC32 for a single file.
        Returns a hexadecimal string.
    """
    crc = 0
    with open(pn, 'rb') as fh:
        while True:
            rdata = fh.read(65536)
            if not rdata:
                break
            crc = zlib.crc32(rdata, crc)
    return "%08X" % (crc & 0xFFFFFFFF)

def crc32pn(pn, recursive):
    """ Compute the CRC for one file or all files in one folder """
    global filespec

    if os.path.isdir(pn):
        # Use filespec to find files and folders within a folder
        for fn in glob.glob(pn + '\\' + filespec):
            if os.path.isfile(fn):
                crc32pn(fn, recursive)  # process files

        # Perform recursion
        if recursive:
            for fn in glob.glob(pn + "\\*"):
                if os.path.isdir(fn):
                    crc32pn(fn, recursive)
    else:
        # Compute the CRC for one file
        rootp, fn = os.path.split(pn)
        print('0x{},"{}","{}"'.format(crc32(pn), fn, pn))

def main(pn, recursive):
    """ Compute the CRC32 for a set of files and folders """
    if os.path.isdir(pn) or os.path.isfile(pn):
        crc32pn(pn, recursive) # CRC all files in a folder
    else:
        global filespec
        pn, filespec = os.path.split(pn)
        crc32pn(pn, recursive) # use a modified filespec

if __name__ == '__main__':
    """ CRC32 [-r] [{pathname}]
        -r  Recursively process subfolders
    """
    path = os.getcwd(); # <pathname>: use the current working directory by default
    recursive = False

    # Print a header for the CSV file style output
    print("CRC,Filename,Pathname")
    for arg in sys.argv[1:]:
        if arg[0] == '-':
            if arg[1].lower() == 'r':
                recursive = True
        else:
            path = os.path.abspath(arg)

    main(path, recursive)
