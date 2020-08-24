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
    if os.path.isdir(pn):
        for fn in glob.glob(pn + "\\*"):
            # Compute the CRC for each file in a folder
            # or each file in a subfolder if -r is specified
            if not os.path.isdir(fn) or recursive:
                crc32pn(fn, recursive)
    else:
        # Compute the CRC for one file
        rootp, fn = os.path.split(pn)
        print("0x{},{},{}".format(crc32(pn), fn, pn))

def main(filespec, recursive):
    """ Compute the CRC32 for a set of files and folders """
    if os.path.isdir(filespec):
        crc32pn(filespec, recursive) # CRC all files in a folder
    else:
        for pn in glob.glob(filespec):
            crc32pn(pn, recursive) # CRC all files in a filespec

if __name__ == '__main__':
    """ CRC32 [-r] {filenames}
        -r  Recursively process subfolders
    """
    recursive = False

    # Print a header for the CSV file style output
    print("CRC,Filename,Pathname")
    for arg in sys.argv[1:]:
        if arg[0] == '-':
            if arg[1].lower() == 'r':
                recursive = True
        else:
            main(os.path.abspath(arg), recursive)
