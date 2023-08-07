#-------------------------------------------------------------------------------
# Name: CmdFile
# Purpose: Read and write command files.
#
# Author: John Eichenberger
#
# Created:     25/08/2020
# Copyright:   (c) John Eichenberger 2020
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import os
from Logging import logging

class CmdFile:
    """ Provides a simple class to create command files. """
    log = None
    prefixes = None

    def __init__(self, filename, clean=True, prefixes=["Del ", "\n@Rem"], style=[32, 38]):
        """ filename can be a fully qualifed pathname or simple filename.
            If a path is supplied, it will be used. Otherwise the TEMP
            environment variable will be used to construct the pathname.

            If desired, any pre-existing command file can be removed during initialization.

            If desired, print messages will occur to detail actions.
        """
        self.log = logging(filename, clean=False, style=style)
        self.prefixes = prefixes
        if clean:
            self.remove()

    def remark(self, line):
        """ Add a remark to the command file """
        self.log.msg("Rem "+line)

    def command(self, pn1, pn2, prefixes=None):
        """ Add two pathnames to the command file using predefined prefixes for each pathname """
        if prefixes == None:
            prefixes = self.prefixes
        self.log.msg('{} "{}" {} "{}"'.format(prefixes[0], pn1, prefixes[1], pn2))

    def remove(self):
        """ Remove any file previously created using this instance """
        if os.path.exists(self.log.logfile):
            self.log.remove()

if __name__ == '__main__':
    """ Test this class """
    testfile = "test.cmd"
    test = CmdFile(testfile)
    test.remark("This is just a remark added to the logfile: " + testfile)
    test.command(os.getcwd()+"\\local.file",".\\another.file")

    print("----start----")
    with open(test.log.logfile) as lt:
        print(lt.read())
    print("----end----")

    # Prefixes
    testfile = "test.cmd"
    test = CmdFile(testfile, False, ["copy", ""])
    test.remark("Adding more to the same file")
    test.command("c:\\root.file", "\\\\network\\pathname")
    test.command("c:\\root.file", "\\\\network\\pathname", ["fc",""])

    print("----start----")
    with open(test.log.logfile) as lt:
        print(lt.read())
    print("----end----")
