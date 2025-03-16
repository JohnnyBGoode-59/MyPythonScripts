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

import glob, re, os, sys
from PIL import Image
from PIL.ExifTags import TAGS
# sudo apt install python3.piexif
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

def GetExifDimensions(pn):
    """ Get the dimensions from a picture using EXIF data """
    exif = get_exif(pn)
    # print(exif)
    width = exif.get('ExifImageWidth')
    if width is None:
        width = exif.get('ImageWidth')
    height = exif.get('ExifImageHeight')
    if height is None:
        height= exif.get('ImageLength')
    if width is None or height is None:
        return None
    return width, height

def GetExifDate(pn):
    """ Get a date from a picture using EXIF data """
    exif = get_exif(pn)
    # print(exif)
    ret = exif.get('DateTimeOriginal')
    if ret is None:
        ret = exif.get('DateTimeDigitized')
    if ret is not None:
        # validate the date returned, it can be corrupt
        " yyyy:mm:dd hh:mm:ss"
        m = re.search("([0-9]{4}):([0-9]{2}):([0-9]{2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})", ret)
        if m is not None and len(m.groups())==6:
            return list(m.groups())
        m = re.search("([0-9]{4}):([0-9]{2}):([0-9]{2})", ret)
        if m is not None:
            return list(m.groups())
        return None
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
    try:
        exif = piexif.load(pn)
    except:
        exif = {}
    dstr = bytes(dstr, 'utf-8')
    for tag in [DATE_TIME_ORIGINAL, DATE_TIME_DIGITIZED]:
        # The next two lines preserves the time found in Exif data
        # But that data can be broken, so let's discard it.
        # if 'Exif' in exif and tag in exif['Exif']:
        #    dstr = dstr[:11]+exif['Exif'][tag][11:]
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
    sep = "[\\-\\._~ ]*?" # optional separators: the dash has to be escaped

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
        for i in range(3):
            if m.group(i+1) is not None:
                today[i] = m.group(i+1)
        return today[:3]

    # mmddyyhhmm[a-f]*.
    mm = dd = yy = hr = min = "([0-9][0-9])"
    m = re.search("^"+mm+dd+yy+hr+min+"[a-f]*([-~(][0-9]*[)]*)*\\.", fn)
    if m is not None:
        today[0] = "20"+m.group(3)
        today[1] = m.group(1)
        today[2] = m.group(2)
        today[3] = m.group(4)
        today[4] = m.group(5)
        return today

    return None

def main():
    GetFileDate('195907252004')

if __name__ == '__main__':
    for arg in sys.argv[1:]:
        if os.path.isdir(arg):
            for pn in glob.glob(glob.escape(arg) + '\\*'):
                if os.path.isfile(pn):
                    dim = GetExifDimensions(pn)
                    if dim is not None:
                        print("Dimensions of {} is {}".format(pn, dim))
                    rootp, fn = os.path.split(pn)
                    date = GetFileDate(fn)
                    if date is not None:
                        print("Date of {} is {}".format(pn, date))

    main()
