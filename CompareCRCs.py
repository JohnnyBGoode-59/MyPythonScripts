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

import glob, os, sys, zlib

import time
from JsonFile import JsonFile
from CmdFile import CmdFile
from FindCRCs import FindCrcs

def help():
    print("Compare-CRCs [-r | folder1 [-w]] [-r | folder2 [-w]]\n")
    print("-r\tReloads a saved set of CRC files from a json file")
    print("-w\t(Re)Creates a json file")
    print("\nFor each of the two folders one can use -r instead of naminig the folder.")
    print("-w is optional. It will save results in two different files.")
    exit()

def onlyinfirst(crcs1, crcs2, cmdfile):
    """ Find CRCs that are only in crcs1 """
    count = 0
    for crc in crcs1:
        if crc == 'pathname':
            continue
        if crc not in crcs2:
            if count == 0:
                cmdfile.write("These files are only in {}".format(crcs1['pathname']))
            cmdfile.write(crcs1[crc])
            count += 1
    return count

def different(crcs1, crcs2, cmdfile):
    """ Find CRCs that are different """
    cmdfile.write("CRCs for these files are different".format(crcs1['pathname']))
    cmdfile.write(crcs1['pathname'])
    cmdfile.write(crcs2['pathname'])
    for crc in crcs1:
        if crc == 'pathname':
            continue
        if crc in crcs2 and crc != crcs2[crc]:
            cmdfile.write(crcs1[crc])

if __name__ == '__main__':
    start = time.time()

    # (Re)Create the pathnames (and files) used by this programe
    file1 = JsonFile("Compare.Crcs1.json")
    file1crcs = None
    file2 = JsonFile("Compare.Crcs2.json")
    file2crcs = None
    crcs = []

    # Combine as many folders and requested
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in ['-?', '/?', '-h', '-H']:
                help()

            elif arg in ['-r', '-R', '/r', '/R']:
                if len(crcs) == 0:
                    crcs += [{"pathname": pathname}]
                    crcs[-1] += file1.read()
                elif len(folders) == 1:
                    crcs += [{"pathname": pathname}]
                    crcs[-1] += file2.read()
                else:
                    help()

            elif arg in ['-w', '-W', '/w', '/W']:
                if len(crcs) == 0:
                    help()
                elif len(crcs) == 1:
                    file1.write(crcs[0])
                else:
                    file2.write(crcs[1])

            else:
                pathname = os.path.abspath(arg)
                if not os.path.isdir(pathname):
                    print("{} does not exist\n".format(pathname))
                    help()
                if len(crcs) < 2:
                    crcs += [{"pathname": pathname}]
                    crcs[-1] = FindCrcs(crcs[-1], pathname)
                else:
                    help()

    if len(crcs) < 2:
        help()

    cmdfile = CmdFile("Compare.Crcs.cmd", "Rem 1 ", clean=True)
    count = onlyinfirst(crcs[0], crcs[1], cmdfile)
    cmdfile = CmdFile("Compare.Crcs.cmd", "Rem 2 ")
    count += onlyinfirst(crcs[1], crcs[0], cmdfile)
    print("{} differences found".format(count))


    # C:\Users\janita\AppData\Local\Temp\pybackup\step0 -w C:\Users\janita\AppData\Local\Temp\pybackup\step1 -w