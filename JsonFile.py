#-------------------------------------------------------------------------------
# Name: JsonFile
# Purpose: Read and write Json files.
#
# Author: John Eichenberger
#
# Created:     25/08/2020
# Copyright:   (c) John Eichenberger 2020
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import json, os

class JsonFile:
    """ Provides a simple class to read and write files. """
    jsonPathname = None
    verbose = False

    def __init__(self, filename, clean=False, verbose=False):
        """ filename can be a fully qualified pathname or simple filename.
            If desired, any pre-existing json file can be removed during initialization.
            If desired, print messages will occur to detail actions.
        """
        self.jsonPathname = os.path.abspath(os.path.expandvars(os.path.expanduser(filename)))
        self.verbose = verbose
        if clean:
            self.remove()

    def report(self, msg):
        """ print a message if verbose was enabled """
        if self.verbose:
            print("JsonFile " + msg)

    def read(self):
        """ Read a dictionary from a json file """
        try:
            with open(self.jsonPathname) as jf:
                data = json.load(jf)
            self.report("{} read".format(self.jsonPathname))
            return data
        except:
            raise Exception("{} could not be read".format(self.jsonPathname))

    def write(self, data):
        """ Write a dictionary to a json file """
        try:
            with open(self.jsonPathname, 'w') as fh:
                js = json.dumps(data)
                json.dump(js, fh)
            self.report("{} written".format(self.jsonPathname))
        except:
            self.report("{} could not be written".format(self.jsonPathname))

    def remove(self):
        """ Remove any file previously created using this instance """
        try:
            os.remove(self.jsonPathname)
            self.report("{} removed".format(self.jsonPathname))
        except:
            pass # it is not noteworthy that a file to be deleted did not exist

if __name__ == '__main__':
    """ Test this class """
    testfile = "JsonFile.test"
    test = JsonFile(testfile, clean=True, verbose=True)
    try:
        mydict = test.read()
        print("ERROR: Trying to read a file that does not exist should cause an exception")
    except:
        print("OK: Trying to read a file that does not exist causes an exception")
    mydict = {}
    mydict["Results"] = "OK"
    test.write(mydict)
    testdict = test.read()
    if mydict == testdict:
        print(mydict)
    else:
        print("ERROR: dictionary mismatch")

    # Now repeat that process quietly
    test = JsonFile(testfile, clean=True)
    try:
        mydict = test.read()
        print("ERROR: Trying to read a file that does not exist should cause an exception")
    except:
        pass
    mydict = {}
    mydict["Results"] = "OK"
    test.write(mydict)
    testdict = test.read()
    if mydict == testdict:
        print(mydict)
    else:
        print("ERROR: dictionary mismatch")

    # Now read an existing file quietly
    finaltest = JsonFile(testfile)
    finalresult = finaltest.read()
    if finalresult == testdict:
        print(mydict)
    else:
        print("ERROR: dictionary mismatch")

    # Check cleanup verbosely
    finaltest = JsonFile(testfile, clean=True, verbose=True)
