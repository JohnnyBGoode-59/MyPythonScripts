#-------------------------------------------------------------------------------
# Name: Find-CRCs
# Purpose: Find matching crc files across many crc files.
#   This program can be used to find and remove duplicate files.
#
# Author: John Eichenberger
#
# Created:     1/8/2023
# Copyright:   (c) John Eichenberger 2021
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import glob, os, re, sys
from JsonFile import JsonFile
from Logging import logging, timespent
from CmdFile import CmdFile

crc_filename = "crc.csv"
cleanscript_filename = "remove-duplicates.cmd"
json_filename = "FindCRCs.json"

found = 0
duplicates = 0
order_switched = False

def help():
    print("""
    Find-CRCs [-s] [-r] [folders] [-w]

    -s  Switch the order files are displayed when duplicates are found.
    -r  Reloads a saved set of CRC files from a master json file.
    -w  (Re)creates that master json file.

    Every other parameter should be that of a folder containing crc.csv files.

    *** WARNING ***
    Pathnames saved with -w may be relative. Do not change directories
    and yet continue to use saved data.

    Conversely, to purposely use relative folder names, use a dot prefix.""")
    exit()

def record_duplicate(cmdfile, original, duplicate):
    """ Log and record a script that can be used to remove duplicate files. """
    global cleanscript, duplicates, order_switched

    # Ignore calls with the exact same pathname for both parameters
    if os.path.abspath(original.lower()) == os.path.abspath(duplicate.lower()):
        return

    # Create a command file that will remove all duplicate files
    # But provide comments in that file in case the original files should be removed instead.
    if duplicates == 0:
        cmdfile.remark("{} removes duplicate files.".format(cmdfile.log.logfile))
        cmdfile.remark("Pick which files to remove.")

    # Sometimes the copies are really the ones to keep.
    if order_switched:
        cmdfile.command(original, duplicate)
    else:
        cmdfile.command(duplicate, original)
    duplicates = duplicates + 1

def AddCrc(crcs, cmdfile, filename):
    """ Add CRC values from one file """
    global found
    try:
        f = open(filename)
    except: # open may not find the file
        return crcs

    rootp, crcfn = os.path.split(filename)
    for line in f:
        # First match a quoted pathname, if possible
        m = re.match('([0-9A-F]{8}),"(.*?)"', line)
        # If that fails, match a pathname with no quotes
        if m == None:
            m = re.match('([0-9A-F]{8}),(.*)', line)
        crc = m.group(1)
        found = found + 1
        pn = rootp + '\\' + m.group(2)
        if crc in crcs:
            record_duplicate(cmdfile, crcs[crc], pn)
        else:
            crcs[crc] = pn
    f.close()
    return crcs

def FindCrcs(crcs, cmdfile, folder):
    """ Combine all crcs together from a directory tree """
    count = len(crcs)
    for pn in glob.glob(glob.escape(folder)+'/*'):
        rootp, fn = os.path.split(pn)
        if fn == crc_filename:
            crcs = AddCrc(crcs, cmdfile, pn)
        elif os.path.isdir(pn):
            crcs = FindCrcs(crcs, cmdfile, pn)
    print("{:,}: crcs added from {}".format(len(crcs)-count, cmdfile.log.nickname(folder)))
    return crcs

if __name__ == '__main__':
    timespent()

    # (Re)Create the pathnames (and files) used by this programe
    jsonfile = JsonFile(json_filename)
    cmdfile = CmdFile(cleanscript_filename)
    processed = []
    crcs = {}

    # Combine as many folders and requested
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in ['-?', '/?', '-h', '-H']:
                help()
            elif arg in ['-r', '-R', '/r', '/R']:
                crcs = jsonfile.read()
            elif arg in ['-w', '-W', '/w', '/W']:
                jsonfile.write(crcs)
            elif arg in ['-s', '-S']:
                order_switched = True
            else:
                pn= os.path.expandvars(arg) # expand but leave relative, maybe
                if os.path.isdir(pn):
                    crcs = FindCrcs(crcs, cmdfile, pn)
                    processed += [pn]
                else:
                    help()

    if duplicates == 0:
        print("No duplicates found in {:,} files".format(found))
    else:
        # Add an all important command at the end of the cleanscript
        # It will update the crc files for the effected folders.
        pybackup_update = ""
        for folder in processed:
            pybackup_update += folder
        cmdfile.remark(pybackup_update, "PyBackup -u ")
        print("\n{:,} Duplicates found.\nremove-duplicates ?".format(duplicates))
    print("{:,} CRCs found. Completed in {}".format(found, timespent()))
