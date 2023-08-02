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

import glob, os, sys, zlib
import json

crc_filename = "crc.csv"
logfile = "duplicates.csv"
jsonfile = "duplicate-crcs.json" # for -r and -w
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
    if os.path.abspath(original) == os.path.abspath(duplicate):
        return
    print("{} == {}".format(nickname(duplicate), nickname(original)))

    log = open(logfile, 'a')
    if duplicates == 0:
        log.write('Original,Duplicate\n')
    log.write('"{}","{}"\n'.format(original, duplicate))
    log.close()

    log = open(cleanscript, 'a')
    if duplicates == 0:
        log.write("Rem {} removes duplicate files\n".format(cleanscript))
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

def ReadJson(filename):
    """ Read a dictionary from a json file or return an empty dictionary """
    try:
        print("Resetting from:", filename)
        with open(filename) as jf:
            data = json.load(jf)
        return json.loads(data)
    except:
        return {}

def WriteJson(data, filename):
    """ Write a dictionary to a json file """
    try:
        print("Saving to:", filename)
        with open(filename, 'w') as fh:
            js = json.dumps(data)
            json.dump(js, fh)
    except:
        pass

def help():
    print("duplicate-crcs -r [folders] -w\n")
    print("\n-r\tReloads a saved set of CRC files from a master file")
    print("\n-w\t(Re)Creates a master file")
    print("\nEvery other parameter should be that of a folder containing crc.csv files.")
    print("\n\n*** WARNING ***")
    print("Pathnames saved with -w may be relative.")
    print("Do not directories and continue to saved data.")
    print("Conversely to purposely use relative folder names use a dot prefix.")

def main(pn):
    """ Combine all crcs together for a directory tree in order to find duplicates """
    global found

    print("Adding from {}".format(nickname(pn)))
    for pn in glob.glob(glob.escape(pn)+'/*'):
        rootp, fn = os.path.split(pn)
        if fn == crc_filename:
            AddCrcs(pn)
        elif os.path.isdir(pn):
            main(pn)

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
    # (Re)Create a logfile used to record duplicates
    temp = os.environ.get('TEMP')
    logfile = Init(temp, logfile)
    cleanscript = Init(temp, cleanscript)
    jsonfile = Init(temp, jsonfile, False)  # Not erased but not read unless requested
    processed = []

    # Combine as many folders and requested
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in ['-?', '/?', '-h', '-H']:
                help()
            elif arg in ['-r', '-R', '/r', '/R']:
                crcs = ReadJson(jsonfile)
            elif arg in ['-w', '-W', '/w', '/W']:
                WriteJson(crcs, jsonfile)
            elif os.path.isdir(arg):
                main(arg)
                processed += [arg]

    if not duplicates:
        print("No duplicates found")
    else:
        # Add an all important command at the end of the cleanscript
        with open(cleanscript, 'a') as fh:
            fh.write("PyBackup -u ")
            for folder in processed:
                fh.write("{} ".format(folder))
            fh.write("\n")
            fh.close()
        print("\n\n")
        with open(cleanscript) as fh:
            print(fh.read())

        print("\n{} Duplicates found.\nremove-duplicates ?".format(duplicates))
