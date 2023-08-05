#-------------------------------------------------------------------------------
# Name: count-files
# Purpose: Simply count how many files are in each folder within a tree.
#
# Author: John Eichenberger
#
# Created:     31/07/2023
# Copyright:   (c) John Eichenberger 2023
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import glob, os, sys, zlib
import time

now = 0
found = 0

def display_update(reset=False):
    """ displays a running count of things when a lot of time has gone by with nothing else printed """
    global now, found
    if reset or now == 0:
        now = time.time()
    else:
        test = time.time()
        if (test - now) > 5:  # Seconds between updates
            print("{} found".format(found), end='\r')
            now = test

def main(pn):
    """ Count files in every folder of a directory tree """
    global found
    count = 0
    # display_update()
    # for fn in os.listdir(pn):
    # fpn = pn + '\\' + fn
    for fpn in glob.glob(glob.escape(pn)+'/*'):
        if os.path.isfile(fpn):
            found = found + 1
            count = count + 1
            # print("{}".format(fpn))
        elif os.path.isdir(fpn):
            main(fpn)
    print('{},"{}"'.format(count, pn))


if __name__ == '__main__':
    print("Count,Pathname")
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if os.path.isdir(arg):
                main(arg)
    else:
        home = os.environ.get('HOMEDRIVE')+'\\'+os.environ.get('HOMEPATH')
        main(home + '\\' + "Pictures")
    print("{:,} found".format(found))
