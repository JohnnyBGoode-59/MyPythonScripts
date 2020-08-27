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
removed = 0
deleted = 0

def main(crcfile, auto_delete):
    global duplicates, removed, deleted

    # Read the CRC file to create a dictionary
    f = open(crcfile)
    next(f) # skip header line
    crcs = {}
    for line in f:
        sline = line.split(',')
        crc = sline[0]
        sline = line.split('"')
        fn = sline[1]
        pn = sline[3]

        # Add one dictionary value
        if crc in crcs:
            crcs[crc] += [pn]
            duplicates += 1
        else:
            crcs[crc] = [pn]
    f.close()

    # Print duplicates, select which one to keep, delete the others
    for crc in crcs:
        # Check to make sure duplicates still exist
        if len(crcs[crc]) > 1:
            for pn in crcs[crc]:
                if not os.path.isfile(pn):
                    crcs[crc].remove(pn)
                    removed += 1

            # Select duplicates to delete
            while len(crcs[crc]) > 1:
                # auto delete duplicates as requested
                if auto_delete != "":
                    try:
                        # Remove one file
                        pn = crcs[crc][int(auto_delete)]
                        os.remove(pn)
                        print("{} deleted".format(pn))
                        deleted += 1
                    except:
                        removed += 1
                    crcs[crc].remove(pn)
                continue

                # Display the list
                for i in range(len(crcs[crc])):
                    print('{}: {}'.format(i, crcs[crc][i]))
                try:
                    num = input("Select a file to remove: ")
                    if num == "":
                        num = None
                        break

                    # Remove one file
                    pn = crcs[crc][int(num)]
                    os.remove(pn)
                    crcs[crc].remove(pn)
                    deleted += 1
                except:
                    pass

if __name__ == '__main__':
    """ Compare-CRCs {filename}
        Read a CRC CSV file and report any matching CRCs.
    """
    # Read %Pictures%/crc.txt when it is present
    filespec = os.environ.get('Pictures')
    if filespec is None:
        # Or ~/Photos/Pictures/crcs.csv
        filespec = os.environ.get('USERPROFILE')
        if filespec is None:
            # Or /Pictures/crcs.csv
            filespec = '\\Pictures'
    filespec = os.path.expandvars(filespec+"\\crcs.csv")
    auto_delete = ""

    # Parse the command line for a specific pathname
    for arg in sys.argv[1:]:
        if arg[0] == '-':
            if arg[1] == 'a':
                if arg[2] in "01":
                    auto_delete = arg[2]
        elif os.path.isfile(arg):
            filespec = os.path.abspath(arg)

    main(filespec, auto_delete)
    print("{} duplicate CRC's found".format(duplicates))
    print("{} were previously deleted".format(removed))
    print("{} were just now deleted".format(deleted))
