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

    def remark(self, line, prefix="Rem ", silent=False):
        """ Add a remark to the command file """
        self.log.msg(prefix+line, silent)

    def command(self, pn1, pn2=None, prefixes=None, silent=False):
        """ Add two pathnames to the command file using predefined prefixes for each pathname """
        if prefixes == None:
            prefixes = self.prefixes
        if pn2 != None:
            self.log.command(prefixes[0], pn1, prefixes[1], pn2, silent)
        else:
            self.log.command(prefixes[0], pn1, silent=silent)

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
