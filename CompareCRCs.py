#-------------------------------------------------------------------------------
# Name: CompareCRCs
# Purpose: Compare crc files in two folders, looking for new and different files.
#
# Author: John Eichenberger
#
# Created:     25/08/2020
# Copyright:   (c) John Eichenberger 2020
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import glob, os, sys

from JsonFile import JsonFile
from CmdFile import CmdFile
from FindCRCs import FindCrcs
from PyBackup import ReadCrcs
from Logging import logging

counters = {}

def help():
    print("""There are two ways to use this program.

CompareCRCs <folder1> <folder2>
    Using this method folder1 and folder2 will be compared, one subfolder at a time.
    That works well for finding files that have the same name at each location,
    but different CRCs values.
e.g. CompareCRCs . %temp%\copy

CompareCRCs -a [<folder1> | -r] [-w]  [<folder2> | -r] [-w]
    Using this method a monolithic CRC dictionary is computed for each folder
    before being compared. This method will discover duplicate files within each
    foldera nd report which CRC values exist only in one set or the other.
    That makes it harder to notice files in both locations but with different CRC values.
    The monolithic dictonaries can be read and written using -r and -w.
    When any of the command line switches are used, this method is selected.

Examples:
    CompareCRCs -a c:\\users\\george\\pictures -w z:\\archive\\pictures
        Compares CRCs on drive C and drive Z.
        Drive C is saved as the first dictionary.

    CompareCRCs -r v:\\archive\pictures -w
        Compares CRCs on drive C (using a saved dictonary) and drive V.
        Drive V is saved as the second dictionary.

    CompareCRCs -a z:\\archive\\pictures -r
        Compares CRCs on drive Z and drive V (using a saved dictonary).
    """)
    exit()

def find_unique(log, crcs1, crcs2):
    """ Find CRCs that are only in crcs1 """
    global counters
    for crc in crcs1:
        if crc == "pathname":
            continue
        if crc not in crcs2:
            log.error(counters, "unique crc", crcs1[crc])
        else:
            log.increment(counters, "identical crc")

def compare_dictionaries(log, crcs1, crcs2, cmdfile):
    """ compare two dictionaries created from two folders """
    global counters
    for crcs in [crcs1, crcs2]:
        crcs = FindCrcs(crcs, cmdfile, crcs["pathname"])
    find_unique(log, crcs1, crcs2)
    identical = "identical crc"
    if identical in counters:
        identical_crcs = counters[identical]
    else:
        identical = 0
    find_unique(log, crcs2, crcs1)
    counters[identical] = identical_crcs

def compare_folders(log, pn1, pn2, cmdfile):
    """ Compare crc files in two folder """
    global counters
    print('"{}": comparing'.format(pn1))
    crcs1, lm1 = ReadCrcs(log, pn1)
    crcs2, lm2 = ReadCrcs(log, pn2)

    # look for differences and unique pn1 files
    for fn in crcs1:
        if fn in crcs2:
            if crcs1[fn] != crcs2[fn]:
                counters = log.error(counters, "different file", pn1 + '\\' + fn)
            else:
                log.increment(counters, "identical file")
        else:
            counters = log.error(counters, "unique file", pn1 + '\\' + fn)

    # look for unique pn2 files
    for fn in crcs2:
        if fn not in crcs1:
            counters = log.error(counters, "unique file", pn2 + '\\' + fn)

    # Recursively look through subfolders in pn1
    dirs1 = []
    for pn in glob.glob(glob.escape(pn1)+'/*'):
        rootp, fn = os.path.split(pn)
        if os.path.isdir(pn):
            if os.path.isdir(pn2+'\\'+fn):
                dirs1 += [fn]
                compare_folders(log, pn, pn2+'\\'+fn)
            else:
                counters = log.error(counters, "unique folder", pn)

    # Recursively look through subfolders in pn2
    for pn in glob.glob(glob.escape(pn2)+'/*'):
        rootp, fn = os.path.split(pn)
        if os.path.isdir(pn) and fn not in dirs1:
            counters = log.error(counters, "unique folder", pn)


if __name__ == '__main__':
    accumulate = False  # Until a switch is processed
    crcs = []

    # (Re)Create the pathnames (and files) used by this programe
    file1 = JsonFile("Compare.Crcs1.json")
    file1crcs = None
    file2 = JsonFile("Compare.Crcs2.json")
    file2crcs = None
    log = logging("CompareCRCs.txt")
    cmdfile = CmdFile("CompareCRCs.cmd")

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in ['-?', '/?', '-h', '-H']:
                help()

            elif arg in ['-a', '-A']:
                accumulate = True

            elif arg in ['-r', '-R', '/r', '/R']:
                accumulate = True
                if len(crcs) == 0:
                    crcs += [{"pathname": pathname}]
                    crcs[-1] += file1.read()
                elif len(folders) == 1:
                    crcs += [{"pathname": pathname}]
                    crcs[-1] += file2.read()
                else:
                    help()

            elif arg in ['-w', '-W', '/w', '/W']:
                accumulate = True
                if len(crcs) == 0:
                    help()
                elif len(crcs) == 1:
                    file1.write(crcs[0])
                else:
                    file2.write(crcs[1])

            else:
                pathname = os.path.abspath(os.path.expandvars(arg))
                if not os.path.isdir(pathname):
                    log.error(counters, "does not exist", pathname)
                    help()
                if len(crcs) < 2:
                    crcs += [{"pathname": pathname}]
                else:
                    help()

    if len(crcs) < 2:
        help()

    if accumulate:
        compare_dictionaries(log, crcs[0], crcs[1], cmdfile)
        log.msg("\nFindCRCs dictionaries complete.")
        log.counters(counters)

    else:
        compare_folders(log, crcs[0]["pathname"], crcs[1]["pathname"])
        log.msg("\nFindCRCs folder comparison complete.")
        log.counters(counters)
