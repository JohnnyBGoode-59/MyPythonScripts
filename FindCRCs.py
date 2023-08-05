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
import time

crc_filename = "crc.csv"
cleanscript = "remove-duplicates.cmd"
found = 0
duplicates = 0
order_switched = False
from PyBackup import timespent

def nickname(source):
    """ Shorten really long names when all I really need is the basics. """
    if len(source) > 50:
        return source[0:10] + "[...]" + source[-40:]
    return source

def log(original, duplicate):
    """ Log and record a script that can be used to remove duplicate files. """
    global cleanscript, duplicates, switch_order

    # Ignore calls with the exact same pathname for both parameters
    if os.path.abspath(original) == os.path.abspath(duplicate):
        return

    # Create a command file that will remove all duplicate files
    # But provide comments in that file in case the original files should be removed instead.
    log = open(cleanscript, 'a')
    if duplicates == 0:
        log.write("@Rem {} removes duplicate files\n".format(cleanscript))
        log.write("@Rem Pick which files to remove.\n")
    # Sometimes the copies are really the ones to keep.
    if order_switched:
        log.write('del  "{}"\n'.format(original))
        log.write('@Rem "{}"\n'.format(duplicate))
    else:
        log.write('del  "{}"\n'.format(duplicate))
        log.write('@Rem "{}"\n'.format(original))
    log.close()

    print("{} == {}".format(nickname(duplicate), nickname(original)))
    duplicates = duplicates + 1

def AddCrc(crcs, filename):
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
            log(crcs[crc], pn)
        else:
            crcs[crc] = pn
    f.close()
    return crcs

def help():
    print("Find-CRCs [-r] [folders] [-w]\n")
    print("-r\tReloads a saved set of CRC files from a master json file")
    print("-s\tSometimes the copies are really the ones to keep.")
    print("-w\t(Re)Creates that master json file")
    print("\nEvery other parameter should be that of a folder containing crc.csv files.")
    print("\n*** WARNING ***")
    print("Pathnames saved with -w may be relative.")
    print("Do not change directories and continue to use saved data.")
    print("Conversely, to purposely use relative folder names, use a dot prefix.")
    exit()

def FindCrcs(crcs, pn):
    """ Combine all crcs together from a directory tree """
    global found

    print("Adding from {} -- {:,} found so far".format(nickname(pn), found))
    for pn in glob.glob(glob.escape(pn)+'/*'):
        rootp, fn = os.path.split(pn)
        if fn == crc_filename:
            crcs = AddCrc(crcs, pn)
        elif os.path.isdir(pn):
            crcs = FindCrcs(crcs, pn)
    return crcs

def Init(rootp, fn, clean=True):
    if rootp is None:
        print("No root path to initialize output files. TEMP not defined?")
        exit()
    pn = rootp + '\\' + fn
    try:
        if clean:
            os.remove(pn)
    except:
        pass
    return pn

if __name__ == '__main__':
    start = time.time()

    # (Re)Create the pathnames (and files) used by this programe
    temp = os.environ.get('TEMP')
    cleanscript = Init(temp, cleanscript)
    jsonfile = JsonFile("FindCRCs.json")
    processed = []

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
            elif os.path.isdir(arg):
                crcs = FindCrcs(crcs, arg)
                processed += [arg]

    if duplicates == 0:
        print("No duplicates found in {:,} files".format(found))
    else:
        # Add an all important command at the end of the cleanscript
        # It will update the crc files for the effected folders.
        with open(cleanscript, 'a') as fh:
            fh.write("PyBackup -u ")
            for folder in processed:
                fh.write("{} ".format(folder))
            fh.write("\n")
            fh.close()
        print("\n\n")
        with open(cleanscript) as fh:
            print(fh.read())

        print("\n{:,} Duplicates found.\nremove-duplicates ?".format(duplicates))
    print("{:,} CRCs found. Completed in {}".format(found, timespent(start)))
