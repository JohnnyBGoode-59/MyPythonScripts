#-------------------------------------------------------------------------------
# Name: RemoveEmpty
# Purpose: Find empty folders and Remove them.
#
# Author: John Eichenberger
#
# Created:     7/8/2023
# Copyright:   (c) John Eichenberger 2021
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import glob, os, sys
from Logging import logging, timespent, display_update
from CmdFile import CmdFile

szScanned = "scanned folder"
szRemoved = "removed folder"
stats = {szScanned:0, szRemoved:0}
errors = {}
crc_filename = "crc.csv"

def help(log):
    print("""
    PruneEmpty [folders]

    For every folder listed on the command line this program will first
    recursively process subfolders and then check to see if the folder is empty.
    If a crc file is the only file left it will remove that file
    and then the folder.""")
    log.remove()
    exit()

def RemoveEmpty(log, cmd, folder):
    """ Remove a folder if it is empty.
        Returns False if all is well.
        Returns True if a command script is required to remove folders.
    """
    global crc_filename, stats, errors, szScanned, szRemoved

    display_update(stats[szScanned], szScanned)
    useScript = False

    # Remove subfolders first
    for pn in glob.glob(glob.escape(folder)+'/*'):
        if os.path.isdir(pn):
            useScript = RemoveEmpty(log, cmd, pn)

    # See what is left
    log.increment(stats, szScanned)
    for pn in glob.glob(glob.escape(folder)+'/*'):
        if os.path.isdir(pn):
            if not useScript:
                return useScript
        elif os.path.isfile(pn):
            rootp, fn = os.path.split(pn)
            if fn.lower() != crc_filename:
                return useScript
        else:
            log.error(errors, "exception", fn)

    if os.path.exists(folder+'\\'+crc_filename):
        os.remove(folder+'\\'+crc_filename)
    try:
        os.rmdir(folder)
    except:
        # If permissions prevent removal, add a line to a script
        cmd.command(folder)
        useScript = True
        return useScript

    log.count(stats, szRemoved, folder)
    return useScript

if __name__ == '__main__':
    timespent()
    log = logging("RemoveEmpty.txt")
    cmd = CmdFile("RemoveFolders.cmd", prefixes=["Rd", None])
    cmd.remark("This script might work when RemoveEmpty fails", silent=True)

    pybackup_update = ""
    if len(sys.argv) < 2:
        help()
    else:
        for arg in sys.argv[1:]:
            if arg in ['-?', '/?', '-h', '-H']:
                help()
            else:
                pn = os.path.expandvars(arg)
                if os.path.isdir(pn):
                    RemoveEmpty(log, cmd, pn)
                    pybackup_update += ' ' + pn
                else:
                    log.error(errors, "is not a folder", arg)
                    help(cmdfile)

    cmd.remark(pybackup_update, prefix="PyBackup -u ", silent=True)
    log.msg("\nRemoveEmpty complete.", silent=True)
    log.counters(errors)
    log.msg("Completed in {}".format(timespent()))
