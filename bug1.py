#-------------------------------------------------------------------------------
# Name: bug1.py
# Purpose: illustrate what looks like a bug with glob
# Author: John Eichenberger
#
# Note:
#   glob is documented to handle square brackets in a special way so if reported
#   this might not be considered a bug. But it sure makes it harder to handle
#   folder names containing brackets when you are not thinking about that
#   possibility.
#
#   I found a work-around for glob, so this clearly would not be considered a bug.
#-------------------------------------------------------------------------------

import glob, os, sys, tempfile

def main():
    """ Create a [folder].
        Put a file in it.
        Test glob vs. listdir.
    """
    pn = tempfile.mkdtemp(prefix="[anything]")
    fn = tempfile.mkstemp(dir=pn)
    epn = glob.escape(pn)+'/*'
    print("listdir(pn) returns: {}".format(os.listdir(pn)))
    print("glob.glob(pn) returns: {}".format(glob.glob(pn)))
    print("glob.glob(epn) returns: {}".format(glob.glob(epn)))
    os.close(fn[0])
    os.remove(fn[1])
    os.rmdir(pn)

if __name__ == '__main__':
    main()
