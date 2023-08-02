#-------------------------------------------------------------------------------
# Name: duplicate-crcs
# Purpose: Find matching crc files across many crc files.
#   This program can be used to find and remove duplicate files.
#
# Author: John Eichenberger
#
# Created:     1/8/2023
# Copyright:   (c) John Eichenberger 2021
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import glob, os, sys, zlib

crc_filename = "crc.csv"
logfile = "duplicates.csv"
cleanscript = "remove-duplicates.cmd"
crcs = {}
duplicates = 0

def nickname(source):
    """ Shorten really long names when all I really need is the basics. """
    if len(source) > 50:
        return source[0:10] + "[...]" + source[-40:]
    return source

def log(original, duplicate):
    """ Log severe errors """
    global logfile, cleanscript, duplicates
    if original == duplicate:
        return
    print("{} == {}".format(nickname(duplicate), nickname(original)))

    log = open(logfile, 'a')
    if duplicates == 0:
        log.write('Original,Duplicate\n')
    log.write('"{}","{}"\n'.format(original, duplicate))
    log.close()

    log = open(cleanscript, 'a')
    if duplicates == 0:
        log.write('Rem Remove Duplicate files\n')
    log.write('del "{}"\n'.format(duplicate))
    log.close()

    duplicates = duplicates + 1

def AddCrcs(filename):
    """ Add CRC values from one file """
    global crcs, duplicates
    try:
        f = open(filename)
    except: # open may not find the file
        return

    rootp, crcfn = os.path.split(filename)
    for line in f:
        if line[-1] == '\n':
            line = line[:-1]
        list = line.split(',')  # careful, some names have commas
        crc = list[0]
        pn = rootp + '\\' + list[1] # pn is the new pathname
        for more in list[2:]:   # this should fix those names
            pn += ','+more
        if crc in crcs:
            log(crcs[crc], pn)
        else:
            crcs[crc] = pn
    f.close()

def main(pn):
    """ Combine all crcs together for a directory tree in order to find duplicates """
    global found

    print("Processing {}".format(nickname(pn)))
    for pn in glob.glob(glob.escape(pn)+'/*'):
        rootp, fn = os.path.split(pn)
        if fn == crc_filename:
            AddCrcs(pn)
        elif os.path.isdir(pn):
            main(pn)

if __name__ == '__main__':
    # (Re)Create a logfile used to record duplicates
    temp = os.environ.get('TEMP')
    if temp is None:
        print("TEMP is not defined as an environment variable")
        exit()
    logfile = temp + '\\' + logfile
    cleanscript  = temp + '\\' + cleanscript
    try:
        os.remove(logfile)
    except:
        pass

    # Combine as many folders and requested
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if os.path.isdir(arg):
                main(arg)

    print(duplicates, "duplicates found")
