"""
The intent of this file is to be available from _every_ python file in this
project, so it should probably be included as:
    from header import *
"""
# Stuff everyone should have.
import sys
import os
import re

def wrn(s):
    print >> sys.stderr, "%s: %s"%(sys.argv[0].split('/')[-1], s)

def bye(n,s):
    wrn(s)
    sys.exit(n)


# This is done on startup since everything is going to include this file.
fs = os.listdir(".")
if (    'header.py' not in fs
    or  'glyph.py' not in fs
    or  not os.path.isdir("glyphs")
    ):
    bye(1, "Are we not in the src dir?")





# Hard-coded things (constants), see the readme.
# These should be set to match the real laser.
consts = {
    'XGridSize':    100,
    'YGridSize':    100,
    'DelayOff':     10,
    'DelayOn':      200,
    'DelayMove':    5,
    'DelayGlow':    20,
    'SpotRadius':   .5,
}

# Checks if the given dict has all the values above.
def hasAllConsts( d ):
    for key in consts:
        if key not in d:
            wrn("Given dict hasn't a key called '%s'."%(key))
            return False
    return True

# Does the set of constants in the given dict match the current ones?
def doAllConstsMatch( d ):
    if not hasAllConsts( d ):
        return False
    for key in consts:
        if consts[key] != d[key]:
            wrn("'%s' in dict (%s) does not match constants (%s)." % (
                key,
                str(d[key]),
                str(consts[key]) ) )
            return False
    return True
