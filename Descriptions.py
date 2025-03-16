#-------------------------------------------------------------------------------
# Name: Descriptions
# Purpose:  Find and print description information found in Json files
#
# Author: John Eichenberger
#
# Created:     15/03/2025
# Copyright:   (c) John Eichenberger 2025
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import glob, re, os, sys, time
from Logging import logging, display_update
from JsonFile import JsonFile

szFile = "file"
stats = {szFile:0}
errors = {}
log = None

def main(pn):
    global log

    # Process files in a folder with no recursion
    for fn in glob.glob(glob.escape(pn) + os.sep + '*.json'):
        if os.path.isfile(fn):
            log.increment(stats, szFile)
            jf = JsonFile(fn)
            mydict = jf.read()
            if 'description' in mydict:
                if len(mydict['description']) > 1:
                    log.msg("{}: {}".format(fn, mydict['description']))

    for pn in glob.glob(glob.escape(pn) + os.sep + '*'):
        if os.path.isdir(pn):
            main(pn)

if __name__ == '__main__':
    """ Process command line arguments """
    log = logging()

    for arg in sys.argv[1:]:
        pn = os.path.abspath(os.path.expandvars(os.path.expanduser(arg)))
        if os.path.isdir(pn):
            main(pn)

    log.counters(stats)
    log.counters(errors)
