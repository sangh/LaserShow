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
    'XGridSize':    256,    # Number of laser stops (cells) horizontaly
    'YGridSize':    256,    #                           " vertically
    'XYExpandPts':  1000,   # How many points to expand a glyph out to.
    'SlowXYExpandPts':  1000,   # How many points to expand a glyph out to.
    'XYNumSlots':   3,      # How many slots does the fast XY have.
    'SlowXYNumSlots':   3,      # How many slots does the slow XY have.

    'SpotRadius':   .9,     # How much of a cell is the laser spot
    'PixPerCell':   2,     # Num pixels per cell edge (det. win. size)

    'DelayOff':     10,     # How many tick to turn laser off
    'DelayOn':      200,    # Num ticks to turn on laser
    'DelayMove':    5,      # How long to move, maybe this is max (?)
    'DelayGlow':    20,    # How many tick to fade out.
    'SecPerTick':   .1,    # .1 means one tick is a tenth of a second

    'Host':         "localhost",
    'Port':         5555,
}
# Now unpack so that each string above is it's own variable name.
# So things like ``window.size = PixPerCell * XGridSize'' work.
for k in consts:
    if isinstance( consts[k], str ):
        exec('%s = """%s"""'%(k,consts[k]))
    else:
        exec('%s = %s'%(k,consts[k]))

# Checks if the given dict has all the values above.
# Used to check if glyphs are vaild for this set up.
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


# This holds what is currently in the slots.
XYSlots = []
for i in range( XYNumSlots ):
    XYSlots.append( None )
SlowXYSlots = []
for i in range( SlowXYNumSlots ):
    SlowXYSlots.append( None )

# This is the list of devices: stepper motors and the two XY~s.
# The index into the tuple is the number, and what is sent over
# the socket as it's id.
# I'm not set on the interface, but to have a terminal, I need something.
# For the steppers it's just the position that is sent (2 bytes, 3rd is unused),
# And for the XY~s 3 bytes at a time are sent for each command.
# The `N' below refers to the 3rd byte sent.
peripherals = (
    ("XY, the fast one.", (  # N is the 3rd byte as an argument.
        "Send new glyph and write into slot N (so then the next XYExpandPts sets of 3 bytes sent are the glyph)",
        "Load glyph from slot N",  # This includes blanking information.
        "Rotate with dir/speed N (need to figure out how to represent)",
        "Grow/shrink with size/speed N (need to figure out how to represent)",
    )),
    ("SlowXY", (
        "Send new glyph and write into slot N (so then the next SlowXYExpandPts sets of 3 bytes sent are the glyph)",
        "Load glygh from slot N",
    )),
    ("One stepper motor description.", (
        "0th target is the XY~s.",
        "Target one is ...",
        "Target the second is undescribed.",
    )),
    ("Stepper 2!", (
        "XY",
        "Unknown 2nd target.",
        "Index 2's target",
    )),
)

