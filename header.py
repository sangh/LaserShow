"""
The intent of this file is to be available from _every_ python file in this
project, so it should probably be included as:
    from header import *
"""

# Hard-coded things see the readme.
XGridSize, YGridSize = 100, 100
DelayOff, DelayOn = 10, 200
DelayMove = 5
DelayGlow = 20

# Stuff everyone should have.
import sys
import os
import re

def wrn(s):
    print >> sys.stderr, "%s: %s"%(sys.argv[0].split('/')[-1], s)

def bye(n,s):
    wrn(s)
    sys.exit(n)
