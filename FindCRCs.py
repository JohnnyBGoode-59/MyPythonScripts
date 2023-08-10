#-------------------------------------------------------------------------------
# Name: FindCRCs
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
from Logging import timespent, logging
from CmdFile import CmdFile

log = None
cmdfile = None
szDuplicates = "duplicate file"
stats = {szDuplicates:0}
order_switched = False

def help():
    global log, cmdfile
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
    log.remove()
    cmdfile.remove()
    exit()

def record_duplicate(original, duplicate):
    """ Log and record a script that can be used to remove duplicate files. """
    global log, cmdfile, szDuplicates, stats, order_switched

    # Ignore calls with the exact same pathname for both parameters
    original = os.path.abspath(original.lower())
    duplicate = os.path.abspath(duplicate.lower())
    if original == duplicate:
        return

    # Sometimes the copies are really the ones to keep.
    if order_switched:
        cmdfile.command(original, duplicate)
    else:
        cmdfile.command(duplicate, original)
    log.increment(stats, szDuplicates)

def AddCrc(crcs, filename):
    """ Add CRC values from one file """
    global log, cmdfile, szDuplicates, stats, order_switched
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
        pn = rootp + '\\' + m.group(2)
        if crc in crcs:
            record_duplicate(crcs[crc], pn)
        else:
            crcs[crc] = pn
            log.increment(stats, "original file")
    f.close()
    return crcs

def FindCrcs(crcs, folder):
    """ Combine all crcs together from a directory tree """
    global log, cmdfile, szDuplicates, stats, order_switched
    count = len(crcs)
    for pn in glob.glob(glob.escape(folder)+'/*'):
        rootp, fn = os.path.split(pn)
        if fn == "crc.csv":
            crcs = AddCrc(crcs, pn)
        elif os.path.isdir(pn):
            crcs = FindCrcs(crcs, pn)
    log.msg("{:,}: crcs added from {}".format(len(crcs)-count, cmdfile.log.nickname(folder)))
    return crcs

if __name__ == '__main__':
    timespent()

    # (Re)Create the pathnames (and files) used by this programe
    log = logging("FindCRCs.txt")
    jsonfile = JsonFile("FindCRCs.json")
    cleanscript_filename = "RemoveDuplicates.cmd"
    cmdfile = CmdFile(cleanscript_filename)
    processed = []
    crcs = {}

    # Start off the command file with a few details.
    # But provide comments in that file in case the original files should be removed instead.
    rootp, cmdline = os.path.split(sys.argv[0])
    for arg in sys.argv[1:]:
        cmdline += ' ' + arg
    log.msg("{}".format(os.getcwd() + "> " + cmdline), silent=True)
    cmdfile.remark("{}".format(os.getcwd() + "> " + cmdline), silent=True)
    cmdfile.remark("{} removes duplicate files.".format(cmdfile.log.logfile), silent=True)
    cmdfile.remark("Pick which files to remove.", silent=True)

    # Combine as many folders and requested
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in ['-?', '/?', '-h', '-H']:
                help()
            elif arg in ['-r', '-R', '/r', '/R']:
                crcs = jsonfile.read()
                log.msg("Read jsonfile")
            elif arg in ['-w', '-W', '/w', '/W']:
                jsonfile.write(crcs)
                log.msg("Wrote jsonfile")
            elif arg in ['-s', '-S']:
                order_switched = True
            else:
                pn= os.path.expandvars(arg) # expand but leave relative, maybe
                if os.path.isdir(pn):
                    crcs = FindCrcs(crcs, pn)
                    processed += [os.path.abspath(pn)]
                else:
                    help()

    log.msg("FindCrcs complete.")
    log.counters(stats)
    if stats[szDuplicates] == 0:
        log.msg("No duplicates found in {:,} files".format(log.sum(stats)))
        cmdfile.remove()
    else:
        # Add an all important command at the end of the cleanscript
        # It will update the crc files for the effected folders.
        pybackup_update = ""
        for folder in processed:
            pybackup_update += ' ' + folder
        cmdfile.remark(pybackup_update, "PyBackup -u ")
        cmdfile.remark("{:,} Duplicates found.  {} ?".format(stats[szDuplicates], cleanscript_filename))
    cmdfile.remark("{:,} CRCs found.".format(log.sum(stats)))
    cmdfile.remark("Completed in {}".format(timespent()))
