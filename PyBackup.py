#-------------------------------------------------------------------------------
# Name: PyBackup
# Purpose: A custom file backup program
#
# Author: John Eichenberger
#
# Created:     20/10/2021
# Copyright:   (c) John Eichenberger 2021
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import glob, os, sys, time, zlib
from shutil import copyfile
from crc32 import crc32

crc_filename = "crc.csv"
copied = 0
found = 0

def ReadCrcs(pn):
    """ Return a dictionary of CRC values for every file in a folder """
    global crc_filename
    crcs = {}
    try:
        filename = pn+'\\'+crc_filename
        f = open(filename)
        for line in f:
            if line[-1] == '\n':
                line = line[:-1]
            list = line.split(',') # carefull, some names have commas
            crc = list[0]
            pn = list[1]
            for more in list[2:]:
                pn += ','+more
            crcs[pn] = crc
        f.close()
        last_modified = os.path.getmtime(filename)
    except:
        last_modified = None
    return crcs, last_modified

def AddCrc(pn, crcs):
    """ Add a CRC to a dictionary of CRCs """
    try:
        crcs[pn] = crc32(pn)
    except:
        crcs[pn] = None

def WriteCrcs(pn, crcs):
    """ Save a dictionary of CRC values for every file in a folder """
    global crc_filename
    try:
        filename = pn+'\\'+crc_filename
        f = open(filename, 'w')
        for pn in crcs:
            f.write(crcs[pn]+','+pn+'\n')
        f.close()
    except:
        pass

##############################################################################
def backup(src, dst):
    """ backup one source file """
    global copied
    print("copy {} {}".format(src, dst))
    copyfile(src, dst)
    copied = copied + 1

##############################################################################
def main(source, dest):
    """ backup one source folder """
    global crc_filename, found

    # Start by reading CRC files, if they exist
    print("Processing {}".format(source))
    source_crcs, source_modified = ReadCrcs(source)
    if not os.path.isdir(dest):
        # print("*Debug* mkdir {}".format(dest))
        os.mkdir(dest)
    dest_crcs, dest_modified = ReadCrcs(dest)

    # Recursively search the source folder
    for pn in glob.glob(source + '\\*'):
        # print("*Debug* Found {}".format(pn))
        rootp, fn = os.path.split(pn)
        if os.path.isfile(pn):
            if fn == crc_filename:
                pass
            else:
                # For every file in the source folder
                dest_pn = dest + '\\' + fn
                found = found + 1

                # Compute CRCs as needed
                last_modified = os.path.getmtime(pn)
                if source_modified == None:
                    # print("*debug* {}".format(last_modified))
                    pass
                # When source_modified is None, source_crcs is empty
                if not pn in source_crcs or last_modified > source_modified:
                    AddCrc(pn, source_crcs)
                if not dest_pn in dest_crcs or last_modified > dest_modified:
                    AddCrc(dest_pn, dest_crcs)

                # Skip files that have matching CRCs
                if source_crcs[pn] == dest_crcs[dest_pn]:
                    continue    # matching files need not be backed up

                # Backup the rest
                backup(pn, dest_pn)
                AddCrc(dest_pn, dest_crcs)

        elif os.path.isdir(pn):
            # For every subfolder
            main(pn, dest+'\\'+fn)

    # Finish off by replacing CRC files
    WriteCrcs(source, source_crcs)
    WriteCrcs(dest, dest_crcs)

##############################################################################
if __name__ == '__main__':
    """ Use an ini file that identifies source and destination folders.
        Copy all files in the source that do not exist in the destination.
        Skip all files with matching CRCs in both locations.
        Create a batch file that will copy newer files over older files,
        but do not run that batch file.
        Advanced ideas:
            1. In the same folder as a file, save the CRC values for each file.
            2. Use those values any time the CRC file is newer than the file.
    """

    # Time the backup
    start = time.time()

    # Switch to the %USERPROFILE% folder where Backup.ini should reside.
    userprofile = os.environ.get('USERPROFILE')
    if userprofile is None:
        print("USERPROFILE is not defined as an environment variable")
        exit()
    os.chdir(userprofile)

    # If a source and destination is specified on the command line, use those
    if len(sys.argv) == 3:  # command source destination
        main(sys.argv[1], sys.argv[2])

    else:
        try:
            f = open("Backup.ini")
        except:
            print("{}\Backup.ini not found")
            exit()

        for line in f:
            if line[0] != '#':
                if line[-1] == '\n':
                    line = line[:-1]
                source, dest = line.split(',')
                main(source, dest)
        f.close()

    print("\nBackup complete. {} files found. {} files copied.".format(found, copied))
    elapsed = time.gmtime(time.time()-start)
    print("Completed in %02d:%02d:%02d" %(elapsed.tm_hour, elapsed.tm_min, elapsed.tm_sec))
