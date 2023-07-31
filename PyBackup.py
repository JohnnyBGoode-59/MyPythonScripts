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

import glob, os, sys, time, zlib
from shutil import copyfile
from crc32 import crc32

crc_filename = "crc.csv"        # the control file found in every folder
logfile = "PyBackup.log.txt"    # opened in the %TEMP% folder

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
deleted_fn = 0  # a backed up file has been deleted

now = 0         # This time.time() value is used by display_update()

def logerror(msg, pathname=None):
    """ Log severe errors """
    global logfile

    if pathname == None:
        fullmsg = msg + '\n'
        shortmsg = msg + ' (logged)'
    else:
        fullmsg = pathname + ": " + msg + '\n'
        shortmsg = nickname(pathname) + ": " + msg + ' (logged)'

    if logfile != None:
        log = open(logfile, 'a')
        log.write(fullmsg)
        log.close()
    print(shortmsg)

def timespent(start):
    """ Returns time spent between the specified start time and now, in a printable string. """
    elapsed = time.gmtime(time.time()-start)
    # Add the number of hours in a day for every day since the start time
    hours = elapsed.tm_hour + (elapsed.tm_yday-1) * 24
    return "%02d:%02d:%02d" % (hours, elapsed.tm_min, elapsed.tm_sec)

def display_counter(log, count, msg):
    """ Display a errors in a consistent way. """
    if count == 1:
        print("1 {}.".format(msg))
        log.write("1 {}.\n".format(msg))
    elif count > 1:
        print("{} {}s.".format(count, msg))
        log.write("{} {}s.\n".format(count, msg))

def display_summary(operation, start):
    """ Display a total operational statistics in a consistent way. """
    global folders, found, copied, hashes, corrupted, crc_missing
    global crc_broken, copy_broken, new_dest, deleted_fn
    global logfile
    log = open(logfile, 'a')
    print("\n{} complete.".format(operation))
    log.write("\n{} complete.\n".format(operation))
    display_counter(log, folders, "folder")
    display_counter(log, found, "file")
    display_counter(log, copied, "copied file")
    display_counter(log, hashes, "hashed file")
    display_counter(log, corrupted, "corrupted crc file")
    display_counter(log, crc_missing, "missing crc")
    display_counter(log, crc_broken, "compute crc error")
    display_counter(log, copy_broken, "failure to copy or create error")
    display_counter(log, new_dest, "unexpected new/modified backup file")
    display_counter(log, deleted_fn, "deleted file")
    print("Completed in {}".format(timespent(start)))
    log.write("Completed in {}\n".format(timespent(start)))
    log.close()

def display_update(reset=False):
    """ displays a running count of things when a lot of time has gone by with nothing else printed """
    global now, found
    if reset:
        now = time.time()
    else:
        test = time.time()
        if (test - now) > 5:  # Seconds between updates
            print("{} found".format(found), end='\r')
            now = test

def ReadCrcs(pn):
    """ Return a dictionary of CRC values for every file in a folder """
    global crc_filename, corrupted
    crcs = {}
    filename = pn+'\\'+crc_filename
    try:
        f = open(filename)
    except: # open may not find the file
        return crcs, None

    try:
        for line in f:
            if line[-1] == '\n':
                line = line[:-1]
            list = line.split(',')  # careful, some names have commas
            crc = list[0]
            pn = list[1]
            for more in list[2:]:   # this should fix those names
                pn += ','+more
            rootp, fn = os.path.split(pn)
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
            logerror("corrupt file removed", filename)
        except:
            logerror("corrupt file cannot be removed", filename)
        corrupted = corrupted + 1

    return crcs, last_modified

def AddCrc(pn, crcs, crc = None):
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
        logerror("failed to compute CRC", pn)
        crc_broken = crc_broken + 1

def WriteCrcs(pn, crcs):
    """ Save a dictionary of CRC values for every file in a folder """
    global crc_filename, corrupted, copy_broken
    try:
        filename = pn+'\\'+crc_filename
        f = open(filename, 'w')
        for pn in sorted(crcs):
            f.write(crcs[pn]+','+pn+'\n')
        f.close()
    except: # the above really should work, or else we have no CRCs
        logerror("could not be created", filename)
        copy_broken = copy_broken + 1

def nickname(source):
    """ Shorten really long names when all I really need is the basics. """
    if len(source) > 75:
        return source[0:32] + "[...]" + source[-38:]
    return source

def verify(source):
    """ check crc values for one folder """
    global crc_filename, found, folders, hashes
    global corrupted, crc_missing, crc_broken, copy_broken, deleted_fn

    # Start by reading CRC files, if they exist
    source_crcs, source_modified = ReadCrcs(source)
    if source_modified == None:
        # Don't log errors when the CRC file is missing
        # Simply compute the crc for all the files found
        logerror("missing CRC file", source)
        crc_missing = crc_missing + 1
        missing = True
    else:
        missing = False

        # Prune out the crc values for any files that no longer exist
        rootp, fn = os.path.split(source)
        for fn in dict(source_crcs).keys():
            pn = source + '\\' + fn
            if not os.path.exists(pn):
                logerror("has been deleted", pn)
                deleted_fn = deleted_fn + 1
                source_crcs.pop(fn)

    print("V: {}: {} folders, {} hashed, {} errors".format(\
        nickname(source), folders, hashes, \
        corrupted+crc_missing+crc_broken+copy_broken))
    display_update(True)
    folders = folders + 1

    # Recursively search the source folder
    for pn in glob.glob(source + '\\*'):
        # print("*Debug* Found {}".format(pn))
        rootp, fn = os.path.split(pn)
        if os.path.isfile(pn):
            if fn != crc_filename:  # ignore the CRC control file
                # For every other file in the source folder
                found = found + 1
                display_update()
                rootp, fn = os.path.split(pn)
                try:
                    crc = crc32(pn)
                    if not missing:
                        if fn not in source_crcs:
                            logerror("missing CRC", pn)
                            crc_missing = crc_missing + 1
                        elif source_crcs[fn] != crc:
                            logerror("mismatched CRC", pn)
                            crc_broken = crc_broken + 1
                    AddCrc(pn, source_crcs, crc)
                except: # crc32 may not find the file
                    logerror("failed to compute CRC", pn)
                    crc_broken = crc_broken + 1

        elif os.path.isdir(pn):
            # For every subfolder
            verify(pn)

    # Finish off by replacing CRC files
    WriteCrcs(source, source_crcs)

def backup(src, dst):
    """ backup one source file """
    global copied, copy_broken
    rootp, srcfn = os.path.split(src)
    print("BC: {}".format(nickname(dst)))   # Backup Copy
    try:
        copyfile(src, dst)
        copied = copied + 1
        return 1
    except:
        logerror("copyfile(" + src + ',' + dst + "): failed")
        copy_broken = copy_broken + 1
        return 0

def recursive_mkdir(pn):
    if not os.path.isdir(pn):
        rootp, fn = os.path.split(pn)
        if not os.path.isdir(rootp) and len(rootp) > 0:
            recursive_mkdir(rootp)
        os.mkdir(pn)

##############################################################################
def main(source, dest):
    """ backup one source folder """
    global crc_filename, copied, found, folders, new_dest
    global corrupted, crc_missing, crc_broken, copy_broken, deleted_fn

    # Start by reading CRC files, if they exist
    print("B: {}: {} folders, {} copied, {} errors".format( \
        nickname(source), folders, copied, \
        corrupted+crc_missing+crc_broken+copy_broken ))
    display_update(True)
    folders = folders + 1
    source_crcs, source_modified = ReadCrcs(source)
    recursive_mkdir(dest)
    dest_crcs, dest_modified = ReadCrcs(dest)

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
                logerror("has been deleted", pn)
                deleted_fn = deleted_fn + 1
                dest_crcs.pop(fn)

    # Recursively search the source folder
    for pn in glob.glob(source + '\\*'):
        rootp, fn = os.path.split(pn)
        if os.path.isfile(pn):
            if fn == crc_filename:
                pass
            else:
                # For every file in the source folder
                dest_pn = dest + '\\' + fn
                found = found + 1
                display_update()

                # When source_modified is None, source_crcs is empty
                # Update the source CRC if it is unknown or the file has changed
                if not fn in source_crcs or os.path.getmtime(pn) > source_modified:
                    AddCrc(pn, source_crcs)

                # Update the destination CRC for existing destination files
                # if the CRC is unknown or the file has changed
                if os.path.exists(dest_pn):
                    if fn not in dest_crcs:
                        logerror("is new", dest_pn)
                        new_dest = new_dest + 1
                        AddCrc(dest_pn, dest_crcs)
                    elif os.path.getmtime(dest_pn) > dest_modified:
                        logerror("has been changed", dest_pn)
                        new_dest = new_dest + 1
                        AddCrc(dest_pn, dest_crcs)

                # Forget destination crc files if the file no longer exists
                elif fn in dest_crcs:
                    logerror("has been deleted", dest_pn)
                    deleted_fn = deleted_fn + 1
                    dest_crcs.pop(fn)

                # Backup new or modified source files
                if fn in source_crcs:   # do we have a CRC?
                    # backup files with no known crc or a different crc
                    if fn not in dest_crcs or source_crcs[fn] != dest_crcs[fn]:
                        if backup(pn, dest_pn):
                            AddCrc(dest_pn, dest_crcs)  # replace the crc
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
            main(pn, dest+'\\'+fn)

    # Finish off by replacing CRC files
    WriteCrcs(source, source_crcs)
    WriteCrcs(dest, dest_crcs)

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
    temp = os.environ.get('TEMP')
    if temp is None:
        print("TEMP is not defined as an environment variable")
        logfile = None
    else:
        logfile = temp + '\\' + logfile
        try:
            os.remove(logfile)
        except:
            pass

    # First look for the new -? switch
    # PyBackup -?
    if len(sys.argv) >= 2 and sys.argv[1] == "-?":
        print(  "\nPyBackup can be used three ways"
                "\n1) no parameters\t-- backup folders using ~\\backup.ini"
                "\n2) souce dest\t\t-- backup one folder"
                "\n3) -v [folders]\t\t-- check crcs in a list of folders")
        print("\nValidation details:")
        print("A crc file is counted as corrupted when an exception occurs while reading or writing a control file.")
        print("A crc is counted as missing once for each control file or once for each data file.")
        print("A crc/file error is counted when an crc exception occurs or the wrong crc is computed.")
        print("Whenever possible the crc control file will be updated to match the current data.")
        exit()

    # Next look for the new -v switch, used to check CRCs for each folder listed
    # PyBackup -v [folders]
    if len(sys.argv) >= 2 and sys.argv[1] == "-v":
        for pn in sys.argv[2:]:
            verify(pn)
        display_summary("Verify", start)

        # The rest below is specific to backup operations
        exit()

    # If a source and destination is specified on the command line, backup one folder
    # PyBackup source destination
    if len(sys.argv) == 3:
        """ Backup one folder """
        main(sys.argv[1], sys.argv[2])

    if len(sys.argv) == 1:
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
            f = open("Backup.ini")
        except:
            print("{}\Backup.ini not found")
            exit()

        for line in f:
            if line[0] != '#':
                if line[-1] == '\n':
                    line = line[:-1]
                source, dest = line.split(',')
                main(source, dest)
        f.close()

    display_summary("Backup", start)
