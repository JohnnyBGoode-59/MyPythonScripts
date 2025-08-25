#-------------------------------------------------------------------------------
# Name: porting
# Purpose: Simple procedures to simplify porting from Windows to Linux (Ubuntu)
#
# Author: John Eichenberger
#
# Created:     13/03/2025
# Copyright:   (c) John Eichenberger 2025
# Licence:     GNU GENERAL PUBLIC LICENSE Version 3, 29 June 2007
#-------------------------------------------------------------------------------

import os
from os.path import pathsep

def abspath(pn):
    """ Take all abbreviations and shortcuts out of a pathname. """
    return os.path.abspath(os.path.expandvars(os.path.expanduser(pn)))

def addpath(*args):
    return os.sep.join(args)
