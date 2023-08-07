#-------------------------------------------------------------------------------
# Name: PyBackup
# Purpose: Backup files and use crc hashes to keep track of changes.
#
# Author: John Eichenberger
#
# Created:     20/10/2021
# Copyright:   (c) John Eichenberger 2021
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import glob, os, re, sys, time, zlib
from shutil import copyfile
from crc32 import crc32
from Logging import logging, display_update, timespent

ini_filename = "backup.ini"
crc_filename = "crc.csv"        # the control file found in every folder

szFolder = "folder"
szFile = "file"
szHashedFile = "hashed file"
szCopiedFile = "copied file"
stats = {szFolder:0, szFile:0, szHashedFile:0, szCopiedFile: 0}
errors = {}


def display_summary(log, operation, start):
    """ Display a total operational statistics in a consistent way. """
    #global folders, found, copied, hashes
    global stats, errors
    log.msg("\n{} complete.".format(operation))
    log.counters(stats)
    log.counters(errors)
    log.msg("Completed in {}".format(timespent(start)))

def ReadCrcs(log, pn):
    """ Return a dictionary of CRC values for every file in a folder """
    global crc_filename, errors
    crcs = {}
    filename = pn+'\\'+crc_filename
    try:
        f = open(filename)
    except: # open may not find the file
        return crcs, None

    try:
        # Every line in a CRC file is 8 hexadecimal characters, a comma
        # and the filename. The filename may be quoted.
        for line in f:
            # First match a quoted pathname, if possible
            m = re.match('([0-9A-F]{8}),"(.*?)"', line)
            # If that fails, match a pathname with no quotes
            if m == None:
                m = re.match('([0-9A-F]{8}),(.*)', line)
            crc = m.group(1)
            fn = m.group(2)
            crcs[fn] = crc
        f.close()
        last_modified = os.path.getmtime(filename)

    except:
        # The file must be corrupted. Delete it and discard all crcs.
        f.close()
        crcs = {}
        last_modified = None
        try:
            os.remove(filename)
            log.error(errors, "removed (corrupted) file", filename)
        except:
            log.error(errors, "could not remove file", filename)

    return crcs, last_modified

def AddCrc(log, pn, crcs, crc = None):
    """ Add a CRC to a dictionary of CRCs.
        This should only be called for an existing file.
        """
    global stats, errors, szHhashedFile
    rootp, fn = os.path.split(pn)
    try:
        if crc == None:
            crc = crc32(pn)
            log.increment(stats, szHashedFile)
        crcs[fn] = crc
    except: # crc32 must have failed
        if fn in crcs:
            crcs.pop(fn)
        log.error(errors, "crc32 failure", pn)

def WriteCrcs(log, pn, crcs):
    """ Save a dictionary of CRC values for every file in a folder """
    global crc_filename, errors
    try:
        filename = pn+'\\'+crc_filename
        f = open(filename, 'w')
        for fn in sorted(crcs):
            # Quote the pathname to make it work better in Excel
            f.write(crcs[fn]+',"'+fn+'"\n')
        f.close()
    except: # the above really should work, or else we have no CRCs
        log.error(errors, "open failure", filename)

def verify(log, source, update=False):
    """ check crc values for one folder """
    global crc_filename
    global stats, errors, szFolder, szHashedFile, szFile

    # Start by reading CRC files, if they exist
    source_crcs, source_modified = ReadCrcs(log, source)
    if source_modified == None:
        log.error(errors, "missing CRC file", source)
        missing = True
    else:
        missing = False

    print("{}: {}: {} folders, {} hashed, {} errors".format(\
        'U' if update else 'V', log.nickname(source), \
        stats[szFolder], stats[szHashedFile], log.sum(errors)))
    display_update(stats[szFile], szFile, True)
    log.increment(stats, szFolder)

    # Prune out the crc values for any files that no longer exist
    if not missing:
        rootp, fn = os.path.split(source)
        for fn in dict(source_crcs).keys():
            pn = source + '\\' + fn
            if not os.path.exists(pn):
                log.error(errors, "missing source file", pn)
                source_crcs.pop(fn)

    # Recursively search the source folder
    for pn in glob.glob(glob.escape(source) + '\\*'):
        rootp, fn = os.path.split(pn)
        display_update(stats[szFile], szFile)
        if os.path.isfile(pn):
            if fn != crc_filename:  # ignore the CRC control file
                # For every other file in the source folder
                log.increment(stats, szFile)
                rootp, fn = os.path.split(pn)
                if update and fn in source_crcs \
                    and source_modified != None \
                    and os.path.getmtime(pn) <= source_modified:
                    continue;   # -u: skip old files
                print("{}: checking".format(log.nickname(pn)))
                display_update(stats[szFile], szFile)
                try:
                    crc = crc32(pn)
                except: # crc32 may not find the file
                    log.error(errors, "crc32 failure", pn)
                    continue;

                log.increment(stats, szHashedFile)
                if not missing:
                    if fn not in source_crcs:
                        log.count(stats, "new source file", pn)
                    elif source_crcs[fn] != crc:
                        log.error(errors, "modified source file", pn)
                AddCrc(log, pn, source_crcs, crc)

        elif os.path.isdir(pn):
            # For every subfolder
            verify(log, pn, update)

    # Finish off by replacing CRC files
    WriteCrcs(log, source, source_crcs)

def backup(log, src, dst):
    """ backup one source file """
    global copied, stats, errors, szCopiedFile
    rootp, srcfn = os.path.split(src)
    print("BC: {}".format(log.nickname(dst)))   # Backup Copy
    try:
        copyfile(src, dst)
    except:
        log.error(errors, "copyfile failure", src)
        log.msg('\t"{}": not replaced'.format(dst))
        return 0
    log.count(stats, szCopiedFile, dst)
    return 1

def recursive_mkdir(pn):
    """ Create a folder, recursively if necessary """
    if not os.path.isdir(pn):
        rootp, fn = os.path.split(pn)
        if not os.path.isdir(rootp) and len(fn) > 0:
            recursive_mkdir(rootp)
        os.mkdir(pn)

##############################################################################
def main(log, source, dest):
    """ backup one source folder """
    global crc_filename
    global stats, errors, szFolder, szCopiedFile, szFile

    # Start by reading CRC files, if they exist
    print("B: {}: {} folders, {} copied, {} errors".format( \
        log.nickname(source), stats[szFolder], stats[szCopiedFile], log.sum(errors)))
    display_update(stats[szFile], szFile, True)
    log.increment(stats, szFolder)
    source_crcs, source_modified = ReadCrcs(log, source)
    recursive_mkdir(dest)
    dest_crcs, dest_modified = ReadCrcs(log, dest)

    # Prune out the crc values for any files that no longer exist
    if source_modified != None:
        for fn in dict(source_crcs).keys():
            pn = source + '\\' + fn
            if not os.path.exists(pn):
                log.error(errors, "missing source file", pn)
                source_crcs.pop(fn)

    # Prune out the crc values for any files that no longer exist
    if dest_modified != None:
        for fn in dict(dest_crcs).keys():
            pn = dest + '\\' + fn
            if not os.path.exists(pn):
                log.error(errors, "missing destination file", pn)
                dest_crcs.pop(fn)

    # Recursively search the source folder
    for pn in glob.glob(glob.escape(source) + '\\*'):
        rootp, fn = os.path.split(pn)
        display_update(stats[szFile], szFile)
        if os.path.isfile(pn):
            if fn == crc_filename:
                pass
            else:
                # For every file in the source folder
                dest_pn = dest + '\\' + fn
                log.increment(stats, szFile)

                # When source_modified is None, source_crcs is empty
                # Update the source CRC if it is unknown or the file has changed
                if not fn in source_crcs or os.path.getmtime(pn) > source_modified:
                    log.increment(stats, "new source crc")  # Not really an error
                    AddCrc(log, pn, source_crcs)

                # Update the destination CRC for existing destination files
                # if the CRC is unknown or the file has changed
                if os.path.exists(dest_pn):
                    if fn not in dest_crcs:
                        if dest_modified != None:
                            log.error(errors, "new destination file", dest_pn)
                        AddCrc(log, dest_pn, dest_crcs)
                    elif os.path.getmtime(dest_pn) > dest_modified:
                        log.error(errors, "modified destination file", dest_pn)
                        AddCrc(log, dest_pn, dest_crcs)

                # Forget destination crc files if the file no longer exists
                elif fn in dest_crcs:
                    log.error(errors, "missing destination file", dest_pn)
                    dest_crcs.pop(fn)

                # Backup new or modified source files
                if fn in source_crcs:   # do we have a CRC?
                    # backup files with no known crc or a different crc
                    if fn not in dest_crcs or source_crcs[fn] != dest_crcs[fn]:
                        if backup(log, pn, dest_pn):
                            AddCrc(log, dest_pn, dest_crcs)  # replace the crc
                        else:
                            # Don't keep a CRC if the backup fails
                            if fn in dest_crcs:
                                log.error(errors, "removed crc", dest_pn)
                                dest_crcs.pop(fn)
                else:
                    # The only explaination for a missing source CRC
                    # is that it could not be computed
                    pass

        elif os.path.isdir(pn):
            # For every subfolder
            main(log, pn, dest+'\\'+fn)

    # Finish off by replacing CRC files
    WriteCrcs(log, source, source_crcs)
    WriteCrcs(log, dest, dest_crcs)

def help():
    """ display command line help and exit """
    print(  "\nPyBackup can be used several ways"
            "\n1) no parameters\t-- backup folders using ~\\backup.ini"
            "\n2) souce dest\t\t-- backup one folder"
            "\n3) -u [folders]\t\t-- update recorded crcs in a list of folders"
            "\n4) -v [folders]\t\t-- validate current crcs in a list of folders")
    print("\nValidation details:")
    print("A crc file is counted as corrupted when an exception occurs while reading or writing a control file.")
    print("A crc is counted as missing once for each control file or once for each data file.")
    print("A crc/file error is counted when an crc exception occurs or the wrong crc is computed.")
    print("Whenever possible the crc control file will be updated to match the current data.")
    exit()

##############################################################################
if __name__ == '__main__':
    """ There are three ways to use this program.
        You can backup a single folder (and children) to a specified destination.
        You can backup a set of folders to respective destinations using an ini file.
        Or you can check the CRC integrety for a list of folders.

        CRC values are used to make it possible to skip copying files that
        have not changed since a previous backup.
    """

    # Time the backup
    start = time.time()

    # (Re)Create a logfile used for severe errors
    log = logging("PyBackup.log.txt")

    # First look for command line switches
    if len(sys.argv) >= 2 and sys.argv[1][0] in ['-', '/']:

        # PyBackup -v [folders]
        # Verify CRCs for each folder listed
        if sys.argv[1][1] in ['u', 'U', 'v', 'V']:
            for pn in sys.argv[2:]:
                pathname = os.path.abspath(os.path.expandvars(pn))
                update = sys.argv[1][1] in ['u', 'U']   # True or False
                verify(log, pathname, update)
            display_summary(log, "Verify", start)
            exit()  # The rest below is specific to backup operations

        # Anything else is either a request for help or shows a need for it.
        # PyBackup -?
        help()

    # If a source and destination is specified on the command line, backup one folder
    # PyBackup source destination
    if len(sys.argv) == 3:
        """ Backup one folder """
        srcp = os.path.abspath(os.path.expandvars(sys.argv[1]))
        destp = os.path.abspath(os.path.expandvars(sys.argv[2]))
        main(log, srcp, destp)
        display_summary(log, "Backup", start)
        exit()

    elif len(sys.argv) != 1:
        help()

    """ No command line parameters were provided.
        Use an ini file that identifies source and destination folders.
        Copy all files in the source that do not exist in the destination.
        Skip all files with matching CRCs in both locations.
        Create a batch file that will copy newer files over older files,
        but do not run that batch file.
        Advanced ideas:
            1. In the same folder as a file, save the CRC values for each file.
            2. Use those values any time the CRC file is newer than the file.
    """

    # Switch to the %USERPROFILE% folder where Backup.ini should reside.
    userprofile = os.environ.get('USERPROFILE')
    if userprofile is None:
        print("USERPROFILE is not defined as an environment variable")
        exit()

    try:
        os.chdir(userprofile)
        f = open(ini_filename)
    except:
        print("{} not found", ini_filename)
        exit()

    # Allow exceptions for the rest
    for line in f:
        if line[0] != '#':
            # Match two quoted names separated by a comma
            m = re.match('"(.*?)","(.*?)"', line)
            if m != None:
                main(log, os.path.abspath(m.group(1)), os.path.abspath(m.group(2)))
            else:
                log.error(errors, "inifile syntax error", line[:-1])
    f.close()
    display_summary(log, "Backup", start)
