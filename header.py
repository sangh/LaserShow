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
del fs


# Hard-coded things (constants), see the readme.
# These should be set to match the real laser.
consts = {
    'XGridSize':    256,    # Number of laser stops (cells) horizontaly
    'YGridSize':    256,    #                           " vertically
    'ExpandPtsXY':  1000,   # How many points to expand a glyph out to.
    'ExpandPtsSlowXY':  500,   # How many points to expand a glyph out to.
    'NumSlotsXY':   3,      # How many slots does the fast XY have.
    'NumSlotsSlowXY':   3,      # How many slots does the slow XY have.

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
slotsXY = [ None for i in range( NumSlotsXY ) ]
slotsSlowXY = [ None for i in range( NumSlotsSlowXY ) ]

# All possible commands
# Right now the key (the byte sent) is random, should decide on real numbers.
# Need to change in the Peripheral list as well.
Commands = {
    3:          "Load glyph from slot 'arg'.",
    ord('T'):   "Set target to `arg'",
    193:        "Send glyph and write into slot `arg'.",  # After this cmd the next ExpandPtsXY sets of 3 bytes sent are the glyph
    112:        "Shrink to `arg',", # If arg is 0 glyph is a point, if 255 it is full-size.
    ord('R'):   "Rotate clockwise `arg' units.", # If arg is 0 then it's upright, 64 or 191 is on it's side, 127 is upside-down
}
# List is the accepted commands from above.
Peripherals = {

    ord('X'):   ("XY, the fast one.",
        ( 3, 193, 112, ord('R'), ), {
        } ),  # No target descriptions.

    ord('x'):   ("Slow XY",
        ( 3, 193, ), {
        } ),  # No target descriptions.

    10:         ("One stepper motor description.",
        ( ord('T'), ), {
            0: "0th target is the XY~s.",
            1: "Target one is ...",
            2: "Target the second is undescribed.",
        } ),
    11:         ("Stepper 2!",
        ( ord('T'), ), {
            0: "XY",
            1: "Unknown 2nd target.",
            8: "Index 2's target",
        } ),
}

def peripheralCommandIsValid( peri, cmd ):
    "Returns True unless peri is not defined above,"
    " or that peri doesn't accept cmd, "
    "arguments are not checked."
    if peri not in Peripherals.keys():
        wrn("Peripheral \"%s\" is not found."%( peri ))
        return False
    if cmd not in Commands.keys():
        wrn("Command \"%s\" is not valid."%( cmd ))
        return False
    if cmd not in Peripherals[peri][1]:
        wrn("Peripheral \"%s (%s)\" does not accept command \"%s (%s)\"." % (
            peri, Peripherals[peri][0], cmd, Commands[cmd] ))
        return False
    return True
