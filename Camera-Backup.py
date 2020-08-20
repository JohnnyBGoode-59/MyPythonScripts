#-------------------------------------------------------------------------------
# Name: Camera-Backup
# Purpose: Backup photos based upon the date of those photos
#
# Author: John Eichenberger
#
# Created:     12/08/2020
# Copyright:   (c) John Eichenberger 2020
#-------------------------------------------------------------------------------

dir_archives = "\\Pictures"
archive_exts = ['.jpg', '.JPG',
                '.jpeg', 'JPEG',
                '.avi', '.AVI',
                '.bmp', '.BMP',
                '.mpg', '.MPG',
                '.mp3', 'MP3',
                '.mp4', '.MP4',
                '.mov', '.MOV',
                '.heic', '.HEIC',
                '.png', '.PNG',
                '.3gp', '.3GP']
found = 0
archived = 0

import glob, re, os, sys

from PIL import Image
from PIL.ExifTags import TAGS

from EXIF_Dating import GetExifDate

def date(fn):
    """ Use a series of regular expressions to extract the date from a filename """
    months = [ "Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec" ]

    # Start with standard Android photo names
    d = re.search("IMG_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_", fn)
    if d is not None:
        return [ d.group(0)[4:8], d.group(0)[8:10], d.group(0)[10:12] ]

    # Include standard Android video names
    d = re.search("VID_[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]_", fn)
    if d is not None:
        return [ d.group(0)[4:8], d.group(0)[8:10], d.group(0)[10:12] ]

    # Include files that start with yyyy-mm-dd in the name
    # Note: This is the format used by photo-renamer.py
    d = re.search("^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]", fn)
    if d is not None:
        return [ d.group(0)[0:4], d.group(0)[5:7], d.group(0)[8:10] ]

    # Try to access EXIF data
    # Note: if the date has been messed up the file can be renamed
    # using one of the name formats above in order to ignore the EXIF data
    d = get_date_taken(fn)
    if d is not None:
        return [ d[0:4], d[5:7], d[8:10] ]

    # Include files that start with yyyy_mmdd or yyyy-mmdd in the name
    d = re.search("^[0-9][0-9][0-9][0-9][_-][0-9][0-9][0-9][0-9]", fn)
    if d is not None:
        return [ d.group(0)[0:4], d.group(0)[5:7], d.group(0)[7:9] ]

    # Include files that include Mon-dd-yyyy in the name
    for m in range(len(months)):
        d = re.search(months[m]+"-[0-9][0-9]-[0-9][0-9][0-9][0-9]", fn)
        if d is not None:
            return [ d.group(0)[7:11], ('0'+str(m+1))[-2:], d.group(0)[4:6] ]

    # Include files that include yyyy-mm-dd in the name
    # so long as yyyy starts with 19 or 20, mm is less than 13,
    # and dd is less than 32
    for m in (['19', '20']):
        d = re.search(m+"[0-9][0-9]-[0-9][0-9]-[0-9][0-9]", fn)
        if d is not None:
            year = d.group(0)[0:4]
            mon = d.group(0)[5:7]
            day = d.group(0)[8:10]
            if int(mon) < 13 and int(day) < 32:
                return [ year, mon, day ]

    # Include files that start with yyyymmddhhmmss in the name
    # so long as yyyy starts with 19 or 20, mm is less than 13,
    # and dd is less than 32
    for m in (['^19', '^20']):
        d = re.search(m+"[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]", fn)
        if d is not None:
            year = d.group(0)[0:4]
            mon = d.group(0)[4:6]
            day = d.group(0)[6:8]
            if int(mon) < 13 and int(day) < 32:
                return [ year, mon, day ]

    # Include files that start with yyyymmdd in the name
    # so long as yyyy starts with 19 or 20, mm is less than 13,
    # and dd is less than 32
    for m in (['^19', '^20']):
        d = re.search(m+"[0-9][0-9][0-9][0-9][0-9][0-9]", fn)
        if d is not None:
            year = d.group(0)[0:4]
            mon = d.group(0)[4:6]
            day = d.group(0)[6:8]
            if int(mon) < 13 and int(day) < 32:
                return [ year, mon, day ]

    # Include files that start with mmddyy in the name
    # so long as yy is less than 50, mm is less than 13,
    # and dd is less than 32
    d = re.search("^[0-9][0-9][0-9][0-9][0-9][0-9]", fn)
    if d is not None:
        year = d.group(0)[4:6]
        mon = d.group(0)[0:2]
        day = d.group(0)[2:4]
        if int(year) < 50 and int(mon) < 13 and int(day) < 32:
            return [ '20'+year, mon, day ]
        d = None

    return d

def make_path(pn):
    """ Create all folders required to create a full pathname to a folder """
    # if the folder already exists, we are done without doing a thing
    if os.path.exists(pn):
        return

    # Find the parent pathname, abort if that is not possible
    rootp = os.path.split(pn)
    if len(rootp) != 2:
        return

    # Create the parent folder if it does not yet exist
    if not os.path.exists(rootp[0]):
        make_path(rootp[0])

    # Create the child folder
    os.mkdir(pn)
    return

def archive(pn):
    """ Archive one picture or movie in it's proper place """
    global dir_archives, found, archived, archive_exts

    # only archive some types of files
    found = found + 1
    path, ext = os.path.splitext(pn)
    if ext not in archive_exts:
        print("Not archiving {}".format(fn))
        return

    # Decide where to archive the file
    months = [ "01Jan", "02Feb", "03Mar", "04Apr", "05May", "06Jun",
               "07Jul", "08Aug", "09Sep", "10Oct", "11Nov", "12Dec" ]
    date = GetExifDate(pn)
    if date is not None:
        year = date[0]
        month = months[int(date[1])-1]
        # print("The date in {} is {}".format(fn, ymd))
        folder = dir_archives + '\\' + year + '\\' + month
    else:
        print("No date found to archive {}".format(fn))
        return

    make_path(folder)
    rootp, fn = os.path.split(pn)
    try:
        os.rename(fn, folder + '\\' + fn)
        archived = archived + 1
    except:
        print("{} could not be archived to {}".format(fn, folder))
        return
    print("{} archived to {}".format(fn, folder))

def archive_everything(pn):
    """ find everything and archive all pictures and movies """
    if(os.path.isdir(pn)):
        for fn in glob.glob(pn + "\\*"):
            if(not os.path.isdir(fn)):
                archive(fn)
    else:
        print("{} is not a folder".format(pn))

def main(pn):
    global found, archived
    archive_everything(pn)
    print("Found {} and archived {}".format(found, archived))

if __name__ == '__main__':
    # if a command line parameter is supplied it is used
    # as the name of the folder to archive
    if len(sys.argv) > 1:
        os.chdir(sys.argv[1])

    # Archive to ~/Photos or /Pictures
    home = os.environ.get('USERPROFILE')
    cwd = os.getcwd()
    if cwd[1:2] == ':' and home[:2] == cwd[:2]:
        # Running on the same drive as ~/Photos
        if os.path.exists(home + '\\Pictures'):
            dir_archives = home + '\\Pictures'

    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main(os.getcwd())
