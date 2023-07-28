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

crc_filename = "crc.csv"
copied = 0
found = 0
folders = 0
hashes = 0
corrupted = 0   # used just for CRC files that cannot be read or written correctly
crc_missing = 0 # source files found with no matching CRC
                # or destination files found with an existing CRC file but no CRC
crc_broken = 0  # actual CRC is different than CRC file, or crc32 failed
copy_broken = 0 # a copy failed or a CRC file failed to be created
logfile = "backup.log.txt"  # opened in the %TEMP% folder

def logerror(msg, pathname=None):
    """ Log severe errors """
    global logfile

    if pathname == None:
        fullmsg = msg + '\r'
        shortmsg = msg + ' (logged)'
    else:
        fullmsg = pathname + ": " + msg + '\r'
        shortmsg = nickname(pathname) + ": " + msg + ' (logged)'

    if logfile != None:
        log = open(logfile, 'a')
        log.write(fullmsg)
        log.close()
    print(shortmsg)

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
            list = line.split(',') # careful, some names have commas
            crc = list[0]
            pn = list[1]
            for more in list[2:]:
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
            crcs.remove(fn)
        logerror("failed to compute CRC", pn)
        crc_broken = crc_broken + 1

def WriteCrcs(pn, crcs):
    """ Save a dictionary of CRC values for every file in a folder """
    global crc_filename, corrupted, copy_broken
    try:
        filename = pn+'\\'+crc_filename
        f = open(filename, 'w')
        for pn in crcs:
            f.write(crcs[pn]+','+pn+'\n')
        f.close()
    except: # the above really should work, or else we have no CRCs
        logerror("could not be created", filename)
        corrupted = corrupted + 1
        copy_broken = copy_broken + 1

def nickname(source):
    """ Shorten really long names when all I really need is the basics. """
    if len(source) > 75:
        return source[0:32] + "[...]" + source[-38:]
    return source

def verify(source):
    """ check crc values for one folder """
    global crc_filename, found, folders
    global corrupted, crc_missing, crc_broken

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

    print("Processing {}: {} folders, {} files, {} errors".format(\
        nickname(source), folders, found, corrupted+crc_missing+crc_broken))
    folders = folders + 1

    # Recursively search the source folder
    for pn in glob.glob(source + '\\*'):
        # print("*Debug* Found {}".format(pn))
        rootp, fn = os.path.split(pn)
        if os.path.isfile(pn):
            if fn != crc_filename:  # ignore the CRC control file
                # For every other file in the source folder
                found = found + 1
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
    print('copy "{}"'.format(srcfn))
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
    global crc_filename, copied, found, folders

    # Start by reading CRC files, if they exist
    print("Processing {}: {} folders, {} files, {} hashed, {} copied".format(\
        nickname(source), folders, found, hashes, copied))
    folders = folders + 1
    source_crcs, source_modified = ReadCrcs(source)
    recursive_mkdir(dest)
    dest_crcs, dest_modified = ReadCrcs(dest)

    # Recursively search the source folder
    for pn in glob.glob(source + '\\*'):
        # print("*Debug* Found {}".format(pn))
        rootp, fn = os.path.split(pn)
        if os.path.isfile(pn):
            if fn == crc_filename:
                pass
            else:
                # For every file in the source folder
                dest_pn = dest + '\\' + fn
                found = found + 1

                # Compute CRCs as needed
                last_modified = os.path.getmtime(pn)
                if source_modified == None:
                    # print("*debug* {}".format(last_modified))
                    pass
                # When source_modified is None, source_crcs is empty
                if not fn in source_crcs or last_modified > source_modified:
                    AddCrc(pn, source_crcs)
                if not fn in dest_crcs or last_modified > dest_modified:
                    if os.path.exists(dest_pn):
                        AddCrc(dest_pn, dest_crcs)

                # Only backup files for which a CRC has been computed
                # with no matching destination file
                if fn in source_crcs:   # do we have a CRC?
                    if fn in dest_crcs: # does the file exist at the destination?
                        if source_crcs[fn] != dest_crcs[fn]:    # is it a matching file?
                            if backup(pn, dest_pn):
                                AddCrc(dest_pn, dest_crcs)  # replace the crc
                    else:   # Adding a file to the destination
                        if backup(pn, dest_pn):
                            AddCrc(dest_pn, dest_crcs)  # add the crc

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
        print("\nVerify complete")
        print( "{} files,".format(found))
        print( "{} corrupted crc files".format(corrupted))
        print( "{} missing crcs".format(crc_missing))
        print( "{} crc/file errors".format(crc_broken))
        if copy_broken != 0:
            print("{} crc failed to be created.".format(copy_broken))
        elapsed = time.gmtime(time.time()-start)
        print("Completed in %02d:%02d:%02d" %(elapsed.tm_hour, elapsed.tm_min, elapsed.tm_sec))
        exit()

    # If a source and destination is specified on the command line, backup one folder
    # PyBackup source destination
    if len(sys.argv) == 3:
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

    print("\nBackup complete.\n{} files found. {} files copied.".format(found, copied))
    if corrupted != 0:
        print("{} corrupted crc files replaced.".format(corrupted))
    if copy_broken != 0:
        print("{} files failed to copy.".format(copy_broken))
    elapsed = time.gmtime(time.time()-start)
    print("Completed in %02d:%02d:%02d" %(elapsed.tm_hour, elapsed.tm_min, elapsed.tm_sec))
