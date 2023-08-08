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
from Logging import logging, display_update

errors = {}

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
    global errors
    for crc in crcs1:
        if crc == "pathname":
            continue
        if crc not in crcs2:
            log.error(errors, "unique crc", crcs1[crc])
        else:
            log.increment(errors, "identical crc")

def compare_dictionaries(log, crcs1, crcs2, cmdfile):
    """ compare two dictionaries created from two folders """
    global errors
    for crcs in [crcs1, crcs2]:
        crcs = FindCrcs(crcs, cmdfile, crcs["pathname"])
    find_unique(log, crcs1, crcs2)
    identical = "identical crc"
    if identical in errors:
        identical_crcs = errors[identical]
    else:
        identical = 0
    find_unique(log, crcs2, crcs1)
    errors[identical] = identical_crcs

def compare_folders(log, pn1, pn2, cmdfile):
    """ Compare crc files in two folder """
    global errors
    print('"{}": comparing, errors:{}'.format(log.nickname(pn1), log.sum(errors)))
    display_update(0, "", True)
    crcs1, lm1 = ReadCrcs(log, pn1)
    crcs2, lm2 = ReadCrcs(log, pn2)

    # look for differences and unique pn1 files
    for fn, crc in crcs1.items():
        srcfpn = pn1 + '\\' + fn
        if fn in crcs2:
            if crc != crcs2[fn]:
                log.error(errors, "different file", srcfpn)
                # copy src to dest? -- not real safe
            else:
                log.increment(errors, "identical file")
        else:
            log.error(errors, "unique file", srcfpn, silent=True)
            cmdfile.command(srcfpn, pn2)

    # look for unique pn2 files
    for fn in crcs2:
        destfpn = pn2 + '\\' + fn
        if fn not in crcs1:
            srcpn = pn1 + '\\' + fn
            log.error(errors, "unique file", destfpn, silent=True)
            cmdfile.command(destfpn, pn1)

    # Recursively look through subfolders in pn1
    dirs1 = []
    folders = 0
    for pn in glob.glob(glob.escape(pn1)+'/*'):
        rootp, fn = os.path.split(pn)
        if os.path.isdir(pn):
            folders += 1
            display_update(folders, "folders")
            if os.path.isdir(pn2+'\\'+fn):
                # This handles folders found in both trees
                dirs1 += [fn]
                compare_folders(log, pn, pn2+'\\'+fn, cmdfile)
            else:
                log.error(errors, "unique folder", pn)

    # look for unique subfolders in pn2, this need not be recursive
    for pn in glob.glob(glob.escape(pn2)+'/*'):
        if os.path.isdir(pn):
            rootp, fn = os.path.split(pn)
            if fn not in dirs1:
                log.error(errors, "unique folder", pn)

if __name__ == '__main__':
    accumulate = False  # Until a switch is processed
    crcs = []
    display_update(0, "Reset")

    # (Re)Create the pathnames (and files) used by this programe
    file1 = JsonFile("Compare.Crcs1.json")
    file1crcs = None
    file2 = JsonFile("Compare.Crcs2.json")
    file2crcs = None
    log = logging("CompareCRCs.txt")

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
                    log.error(errors, "does not exist", pathname)
                    help()
                if len(crcs) < 2:
                    crcs += [{"pathname": pathname}]
                else:
                    help()

    if len(crcs) < 2:
        help()

    # Rebuild the command line
    rootp, cmdline = os.path.split(sys.argv[0])
    for arg in sys.argv[1:]:
        cmdline += ' ' + arg

    if accumulate:
        cmdfile = CmdFile("CompareCRCs.cmd")
        cmdfile.remark("{}".format(os.getcwd() + "> " + cmdline), silent=True)
        cmdfile.remark("{} removes duplicate files.".format(cmdfile.log.logfile), silent=True)
        cmdfile.remark("Pick which files to remove.", silent=True)
        compare_dictionaries(log, crcs[0], crcs[1], cmdfile)
        log.msg("\nFindCRCs dictionaries complete.")
        log.counters(errors)

    else:
        cmdfile = CmdFile("CompareCRCs.cmd", prefixes=["replace /a",""])
        cmdfile.remark("{}".format(os.getcwd() + "> " + cmdline), silent=True)
        cmdfile.remark("{} adds missing files using replace /a.".format(cmdfile.log.logfile), silent=True)
        compare_folders(log, crcs[0]["pathname"], crcs[1]["pathname"], cmdfile)
        log.msg("\nFindCRCs folder comparison complete.")
        log.counters(errors)
