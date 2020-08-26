#-------------------------------------------------------------------------------
# Name: Compare-CRCs
# Purpose: Read a file of CRC values and display lines with matching values
#
# Author: John Eichenberger
#
# Created:     25/08/2020
# Copyright:   (c) John Eichenberger 2020
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import glob, os, sys, zlib

duplicates = 0

def main(crcfile):
    global duplicates
    crcs = {}

    # Read the CRC file to create a dictionary
    f = open(crcfile)
    next(f) # skip header line
    for line in f:
        sline = line.split(',')
        crc = sline[0]
        sline = line.split('"')
        fn = sline[1]
        pn = sline[3]

        # Add one dictionary value
        if crc in crcs:
            crcs[crc]['count'] += 1
            crcs[crc]['pns'] += [pn]
            duplicates += 1
        else:
            crcs[crc] = {}
            crcs[crc]['count'] = 1
            crcs[crc]['pns'] = [pn]
    f.close()

    # Print duplicates
    for crc in crcs:
        if crcs[crc]['count'] > 1:
            for pn in crcs[crc]['pns']:
                print("{},{}".format(crc,pn))

if __name__ == '__main__':
    """ Compare-CRCs {filename}
        Read a CRC CSV file and report any matching CRCs.
    """
    # Read %Pictures%/crc.txt when it is present
    filespec = os.environ.get('Pictures')
    if filespec is None:
        # Or ~/Photos/Pictures/crc.txt
        filespec = os.environ.get('USERPROFILE')
        if filespec is None:
            # Or /Pictures/crc.txt
            filespec = '\\Pictures'
    filespec = os.path.expandvars(filespec+"\\crc.txt")

    # Parse the command line for a specific pathname
    for arg in sys.argv[1:]:
        if arg[0] == '-':
            pass
        elif os.path.isfile(arg):
            filespec = os.path.abspath(arg)

    main(filespec)
    print("{} duplicate CRC's found".format(duplicates))
