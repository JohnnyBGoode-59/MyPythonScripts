#-------------------------------------------------------------------------------
# Name: EXIF-Dating
# Purpose: Use pattern matching to determine the date of a file from the filename
#
# Author: John Eichenberger
#
# Created: 19/08/2020
# Copyright:   (c) John Eichenberger 2020
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import re, os
from PIL import Image
from PIL.ExifTags import TAGS
import piexif

today = ["2020", "08", "19", "12", "00", "00"]

def get_exif(fn):
    """ Get the EXIF data from a file, if it is available """
    ret = {}
    try:
        i = Image.open(fn)
    except:
        #dbg print("failed: Image.open({})".format(fn))
        return ret
    try:
        info = i._getexif()
    except:
        print("failed: _getexif: {}".format(fn))
        return ret

    if info is not None:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            #dbg if decoded != tag:
            #dbg    print("{} {}({})={}".format(fn, decoded, tag, value))
            ret[decoded] = value
        #dbg print("{} has {} EXIF data elements".format(fn, len(ret)))
    else:
        #dbg print("{} has no EXIF data".format(fn))
        pass
    return ret

def GetExifDate(pn):
    """ Get a date from a picture using EXIF data """
    exif = get_exif(pn)
    # print(exif)
    ret = exif.get('DateTimeOriginal')
    if ret is None:
        ret = exif.get('DateTimeDigitized')
    if ret is not None:
        ret = [ ret[0:4], ret[5:7], ret[8:10], ret[11:13], ret[8:10], ret[11:13] ]
    return ret

def SetExifDate(pn, date):
    """ Add EXIF data to set a date """
    if len(date) == 6:
        dstr = date[0]+':'+date[1]+':'+date[2]+' '+date[3]+':'+date[4]+':'+date[5]
    else:
        dstr = date[0]+':'+date[1]+':'+date[2]+' 12:00:00'

    # Add DateTimeOriginal and DateTimeDigitized to the Exif data
    DATE_TIME_ORIGINAL = 36867
    DATE_TIME_DIGITIZED = 36868
    exif = piexif.load(pn)
    dstr = bytes(dstr, 'utf-8')
    for tag in [DATE_TIME_ORIGINAL, DATE_TIME_DIGITIZED]:
        if 'Exif' in exif and tag in exif['Exif']:
            dstr = dstr[:11]+exif['Exif'][tag][11:]
        exif['Exif'][tag] = dstr
    exif_encoded = piexif.dump(exif)

    # Replace the original file with the new file and exif
    im = Image.open(pn)
    im.save(pn, "jpeg", exif=exif_encoded)
    return

def GetFileDate(fn):
    """ Use a series of regular expressions to extract the date from a filename """
    global today

    # Allow any separator in this list
    sep = "[\-\._~ ]*?" # optional separators: the dash has to be escaped

    # yyyy-mm-dd_hh-mm-ss (yyyy must start with 19 or 20)
    yyyy = "(19[0-9][0-9]|20[0-9][0-9])"+sep
    mm = dd = "([0-9][0-9])"+sep
    hr = min = sec = "([0-9][0-9])"+sep
    m = re.search("^"+yyyy+mm+dd+hr+min+sec, fn)
    if m is not None:
        for i in range(6):
            if m.group(i+1) is not None:
                today[i] = m.group(i+1)
        return today

    # IMG_yyyy-mm-dd_ (yyyy must start with 19 or 20)
    m = re.search("^([A-Z])*?_"+yyyy+mm+dd, fn)
    if m is not None:
        for i in range(3):
            if m.group(i+2) is not None:
                today[i] = m.group(i+2)
        return today[:3]

    # yyyy-mm-dd_ (yyyy must start with 19 or 20)
    m = re.search("^"+yyyy+mm+dd, fn)
    if m is not None:
        for i in range(2):
            if m.group(i+1) is not None:
                today[i] = m.group(i+1)
        return today[:3]

    return None

def main():
    GetFileDate('195907252004')

if __name__ == '__main__':
    main()
