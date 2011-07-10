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
    'XGridSize':    50,    # Number of laser stops (cells) horizontaly
    'YGridSize':    30,    #                           " vertically
    'SpotRadius':   .9,     # How much of a cell is the laser spot
    'PixPerCell':   10,     # Num pixels per cell edge (det. win. size)

    'DelayOff':     10,     # How many tick to turn laser off
    'DelayOn':      200,    # Num ticks to turn on laser
    'DelayMove':    5,      # How long to move, maybe this is max (?)
    'DelayGlow':    20,     # How long to illuminate a cell in ticks
    'SecPerTick':   .001,   # .001 means one tick is a millisecond
}
# Now unpack so that each string above is it's own variable name.
# So things like ``window.size = PixPerCell * XGridSize'' work.
for k in consts:
    exec('%s = %s'%(k,consts[k]))

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
