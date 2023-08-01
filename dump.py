#-------------------------------------------------------------------------------
# Name:        dump.py
# Purpose: Display the contents of a file as a hexadecimal dump.
#
# Author:      John Eichenberger
#
# Created:     02/04/2021
# Copyright:   (c) John Eichenberger 2021
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import binascii, glob, os, sys

def main(fn):
    """ Dump the contents of a file """
    print("{}:".format(fn))
    file = open(fn, "rb")
    line = file.read(16)
    while line:
        hex = str(binascii.hexlify(line, ' '))[2:-1]
        print(hex, end=' ')
        print("{}".format(' '*48)[len(line)*3:], end='[')
        for ch in line:
            if ch < 32 or (ch > 127 and ch < 160):
                print('.', end='')
            else:
                print(chr(ch), end='')
        print(']')

        line = file.read(16)
    file.close()

if __name__ == '__main__':
    """ Process command line arguments """

    if len(sys.argv) < 2:
        print("dump [pathname]")
        exit()

    # Process the command line arguments
    for arg in sys.argv[1:]:
        for fn in glob.glob(glob.escape(arg)):
            if os.path.isfile(fn):
                main(fn)
            elif not os.path.isdir(fn):
                print("Cannot dump the contents of {}".format(fn))
                exit()
