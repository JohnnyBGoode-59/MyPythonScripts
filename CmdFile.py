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

class CmdFile:
    """ Provides a simple class to create command files. """
    pathname = None
    verbose = False
    prefix = ""

    def __init__(self, filename, prefix=None, verbose=False, clean=False):
        """ filename can be a fully qualifed pathname or simple filename.
            If a path is supplied, it will be used. Otherwise the TEMP
            environment variable will be used to construct the pathname.

            If desired, any pre-existing command file can be removed during initialization.

            If desired, print messages will occur to detail actions.
        """
        rootp, fn = os.path.split(filename)
        if rootp == '':
            rootp = os.environ.get('TEMP')
            if rootp is None:
                raise Exception("TEMP environment variable is not defined")

        self.pathname = os.path.abspath(rootp + '\\' + fn)
        self.verbose = verbose
        self.prefix = prefix
        if self.prefix != None:
            self.verbose = True
        if clean:
            self.remove()

    def report(self, msg):
        """ print a message if verbose was enabled """
        if self.verbose:
            print("{}: {}".format(self.prefix, msg))

    def write(self, line):
        """ Add a line to the command file """
        try:
            with open(self.pathname, 'a') as cf:
                cf.write(self.prefix + line + '\n')
            self.report(line)
        except:
            raise Exception("{} could not be written".format(self.pathname))

    def remove(self):
        """ Remove any file previously created using this instance """
        try:
            os.remove(self.pathname)
            self.report("{} removed".format(self.pathname))
        except:
            pass # it is not noteworthy that a file to be deleted did not exist

if __name__ == '__main__':
    """ Test this class """
    testfile = "CmdFile.test"
    test = CmdFile(testfile, "Test1 ", clean=True)
    test.write("line1:" + testfile)
    test.write("line2:" + testfile)
    print("---------")
    with open(test.pathname) as lt:
        print(lt.read())
    print("---------")

    # Test messages
    test = CmdFile(testfile, clean=True, verbose=True, prefix="Test2")
    test = CmdFile(testfile, clean=True)
