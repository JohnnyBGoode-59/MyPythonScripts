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

copied = 0      # files copied
found = 0       # files found
folders = 0     # folders processed
hashes = 0      # hashes computed
corrupted = 0   # used just for CRC files that cannot be read or written correctly
crc_missing = 0 # source files found with no matching CRC
                # or destination files found with an existing CRC file but no CRC
crc_broken = 0  # actual CRC is different than CRC file, or crc32 failed
copy_broken = 0 # a copy failed or a CRC file failed to be created
new_dest = 0    # a destination file is newer than the corresponding crc file
deleted_fn = 0  # a backed up file was deleted

def display_summary(log, operation, start):
    """ Display a total operational statistics in a consistent way. """
    global folders, found, copied, hashes, corrupted, crc_missing
    global crc_broken, copy_broken, new_dest, deleted_fn

    log.msg("\n{} complete.".format(operation))
    log.counter(folders, "folder")
    log.counter(found, "file")
    log.counter(copied, "copied file")
    log.counter(hashes, "hashed file")
    log.counter(corrupted, "corrupted crc file")
    log.counter(crc_missing, "missing crc")
    log.counter(crc_broken, "compute crc error")
    log.counter(copy_broken, "failure to copy or create error")
    log.counter(new_dest, "unexpected new/modified backup file")
    log.counter(deleted_fn, "deleted file")
    log.msg("Completed in {}".format(timespent(start)))

def ReadCrcs(log, pn):
    """ Return a dictionary of CRC values for every file in a folder """
    global crc_filename, corrupted
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
            log.error("corrupt file removed", filename)
        except:
            log.error("corrupt file cannot be removed", filename)
        corrupted = corrupted + 1

    return crcs, last_modified

def AddCrc(log, pn, crcs, crc = None):
    """ Add a CRC to a dictionary of CRCs.
        This should only be called for an existing file.
        """
    global hashes, crc_broken
    rootp, fn = os.path.split(pn)
    try:
        if crc == None:
            crc = crc32(pn)
            hashes = hashes + 1
        crcs[fn] = crc
    except: # crc32 must have failed
        if fn in crcs:
            crcs.pop(fn)
        log.error("failed to compute CRC", pn)
        crc_broken = crc_broken + 1

def WriteCrcs(log, pn, crcs):
    """ Save a dictionary of CRC values for every file in a folder """
    global crc_filename, corrupted, copy_broken
    try:
        filename = pn+'\\'+crc_filename
        f = open(filename, 'w')
        for fn in sorted(crcs):
            # Quote the pathname to make it work better in Excel
            f.write(crcs[fn]+',"'+fn+'"\n')
        f.close()
    except: # the above really should work, or else we have no CRCs
        log.error("could not be created", filename)
        copy_broken = copy_broken + 1

def verify(log, source, update=False):
    """ check crc values for one folder """
    global crc_filename, found, folders, hashes
    global corrupted, crc_missing, crc_broken, copy_broken, deleted_fn

    # Start by reading CRC files, if they exist
    source_crcs, source_modified = ReadCrcs(log, source)
    if source_modified == None:
        # Don't log errors when the CRC file is missing
        # Simply compute the crc for all the files found
        log.error("missing CRC file", source)
        crc_missing = crc_missing + 1
        missing = True
    else:
        missing = False

    print("{}: {}: {} folders, {} hashed, {} errors".format(\
        'U' if update else 'V', log.nickname(source), folders, hashes, \
        corrupted+crc_missing+crc_broken+copy_broken))
    display_update(found, "found", True)
    folders = folders + 1

    # Prune out the crc values for any files that no longer exist
    if not missing:
        rootp, fn = os.path.split(source)
        for fn in dict(source_crcs).keys():
            pn = source + '\\' + fn
            if not os.path.exists(pn):
                log.error("was deleted", pn)
                deleted_fn = deleted_fn + 1
                source_crcs.pop(fn)

    # Recursively search the source folder
    for pn in glob.glob(glob.escape(source) + '\\*'):
        rootp, fn = os.path.split(pn)
        display_update(found, "found")
        if os.path.isfile(pn):
            if fn != crc_filename:  # ignore the CRC control file
                # For every other file in the source folder
                found = found + 1
                rootp, fn = os.path.split(pn)
                if update and fn in source_crcs \
                    and source_modified != None \
                    and os.path.getmtime(pn) <= source_modified:
                    continue;   # -u: skip old files
                print("{}: checking".format(log.nickname(pn)))
                display_update(found, "found", True)
                try:
                    crc = crc32(pn)
                except: # crc32 may not find the file
                    log.error("failed to compute CRC", pn)
                    crc_broken = crc_broken + 1
                    continue;
                hashes = hashes + 1
                if not missing:
                    if fn not in source_crcs:
                        log.error("missing CRC", pn)
                        crc_missing = crc_missing + 1
                    elif source_crcs[fn] != crc:
                        log.error("mismatched CRC", pn)
                        crc_broken = crc_broken + 1
                AddCrc(log, pn, source_crcs, crc)

        elif os.path.isdir(pn):
            # For every subfolder
            verify(log, pn, update)

    # Finish off by replacing CRC files
    WriteCrcs(log, source, source_crcs)

def backup(log, src, dst):
    """ backup one source file """
    global copied, copy_broken
    rootp, srcfn = os.path.split(src)
    print("BC: {}".format(log.nickname(dst)))   # Backup Copy
    try:
        copyfile(src, dst)
        copied = copied + 1
        return 1
    except:
        log.error("copyfile(" + src + ',' + dst + "): failed")
        copy_broken = copy_broken + 1
        return 0

def recursive_mkdir(pn):
    """ Create a folder, recursively if necessary """
    if not os.path.isdir(pn):
        rootp, fn = os.path.split(pn)
        if not os.path.isdir(rootp) and len(rootp) > 0:
            recursive_mkdir(rootp)
        os.mkdir(pn)

##############################################################################
def main(log, source, dest):
    """ backup one source folder """
    global crc_filename, copied, found, folders, new_dest
    global corrupted, crc_missing, crc_broken, copy_broken, deleted_fn

    # Start by reading CRC files, if they exist
    print("B: {}: {} folders, {} copied, {} errors".format( \
        log.nickname(source), folders, copied, \
        corrupted+crc_missing+crc_broken+copy_broken ))
    display_update(found, "found", True)
    folders = folders + 1
    source_crcs, source_modified = ReadCrcs(log, source)
    recursive_mkdir(dest)
    dest_crcs, dest_modified = ReadCrcs(log, dest)

    # Prune out the crc values for any files that no longer exist
    if source_modified != None:
        for fn in dict(source_crcs).keys():
            pn = source + '\\' + fn
            if not os.path.exists(pn):
                source_crcs.pop(fn)

    # Prune out the crc values for any files that no longer exist
    if dest_modified != None:
        for fn in dict(dest_crcs).keys():
            pn = dest + '\\' + fn
            if not os.path.exists(pn):
                log.error("was deleted", pn)
                deleted_fn = deleted_fn + 1
                dest_crcs.pop(fn)

    # Recursively search the source folder
    for pn in glob.glob(glob.escape(source) + '\\*'):
        rootp, fn = os.path.split(pn)
        display_update(found, "found")
        if os.path.isfile(pn):
            if fn == crc_filename:
                pass
            else:
                # For every file in the source folder
                dest_pn = dest + '\\' + fn
                found = found + 1

                # When source_modified is None, source_crcs is empty
                # Update the source CRC if it is unknown or the file has changed
                if not fn in source_crcs or os.path.getmtime(pn) > source_modified:
                    AddCrc(log, pn, source_crcs)

                # Update the destination CRC for existing destination files
                # if the CRC is unknown or the file has changed
                if os.path.exists(dest_pn):
                    if fn not in dest_crcs:
                        log.error("is new", dest_pn)
                        new_dest = new_dest + 1
                        AddCrc(log, dest_pn, dest_crcs)
                    elif os.path.getmtime(dest_pn) > dest_modified:
                        log.error("was changed", dest_pn)
                        new_dest = new_dest + 1
                        AddCrc(log, dest_pn, dest_crcs)

                # Forget destination crc files if the file no longer exists
                elif fn in dest_crcs:
                    log.error("was deleted", dest_pn)
                    deleted_fn = deleted_fn + 1
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
                verify(log, pn, sys.argv[1][1] in ['u', 'U'])
            display_summary(log, "Verify", start)
            exit()  # The rest below is specific to backup operations

        # Anything else is either a request for help or shows a need for it.
        # PyBackup -?
        help()

    # If a source and destination is specified on the command line, backup one folder
    # PyBackup source destination
    if len(sys.argv) == 3:
        """ Backup one folder """
        main(log, sys.argv[1], sys.argv[2])
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
            if line[-1] == '\n':
                line = line[:-1]
            source, dest = line.split(',')
            main(log, source, dest)
    f.close()
    display_summary(log, "Backup", start)
