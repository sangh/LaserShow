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
    'ExpandPtsSlowXY':  500,#                           " for the slow one.
    'NumSlotsXY':   3,      # How many slots does the fast XY have.
    'NumSlotsSlowXY':   3,  # How many slots does the slow XY have.
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
SlotsXY = [ None for i in range( NumSlotsXY ) ]
SlotsSlowXY = [ None for i in range( NumSlotsSlowXY ) ]

# All possible commands
# Right now the key (the byte sent) is random, should decide on real numbers.
# Need to change in the Peripheral list as well.
Commands = {
    0:          "reset index counters",
    1: 			"tick CW without updating index",	# For hand-zeroing
    2:			"tick CCW without updating index",	# For hand-zeroing
    3:			"move to index slot",	# Not implemented on MCU
    4:			"move to index raw count",
    5:			"set target slots",	# The three byte command structure doesn't make it easy to do this
    6:			"set target slots, continued",  # all targets have to be loaded if any are loaded
    7:            "sel glyph in slot.",
    30:         "Send glyph and write it into slot `arg'.",  # After this cmd the next ExpandPtsXY sets of 3 bytes sent are the glyph
    40:         "Shrink current glyph to `arg',", # If arg is 0 glyph is a point, if 255 it is full-size.
    41:   		"set rotation to 'arg' where 255=360 degrees", # If arg is 0 then it's upright, 64 or 191 is on it's side, 127 is upside-down
 
    50:			"Set speed of DG wheel- signed 8 bit number 0= still",

    60:			"Go to X position",
    61:			"Go to Y position",
    
    100:         "Move `arg' ticks clockwise", # That is ticks on the stepper motor.
    101:         "Move `arg' ticks counterclockwise", # That is ticks on the stepper motor.
    102:		 "attempt to auto-zero",
}
# List is the accepted commands from above.
# One thread/queue for each _unique_ host/port.
laser1 = ("Laser1", 2000)
#laser1 = ('localhost, 5555)
#Or if you want to write to a file:
#laser1 = "/dev/cu.XXXXX"
Peripherals = {
    0:   ("Green Stepper", laser1 ),	# accepts tune +- commands plus go-to-index#
    1:   ("Red Stepper", laser1 ),		# accepts tune +- commands plus go-to-index#
    2:   ("Blue Stepper", laser1 ),		# accepts tune +- commands plus go-to-index#
    3:   ("DG 6track speed", laser1 ),	# accepts only a speed as a signed number indicating direction
    4:   ("DG sector select", laser1 ),	# accepts a sector number to select, like a slot select for a glyph- same command
    5:   ("HS XY", laser1 ),			# accepts many commands, play glyph, go to position
    6:   ("LS XY", laser1 ),			# same as above, but an order of magnitude slower
    7:   ("Green Blanking", laser1 ),	# accepts just an on/off to turn the green laser on or off
    8:   ("Red Blanking", laser1 ),		# same as above 
}

Targets = {
    0:  "Beamnet1",
    1:  "Beamnet2",
    2:  "Beamnet3...",
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
    return True


def plist( peri = None ):
    "Print out the peripherals, but you could just look at header.py"
    for peri in Peripherals:
        wrn("")
        wrn("Peripheral  %3d   \"%s\":"%(
            peri, Peripherals[peri][0] ))
        for t in Peripherals[peri][1]:
            wrn("      Target%3d   \"%s\"."%(
            t, Peripherals[peri][1][t] ))
    wrn("")
    for cmd in Commands:
        wrn("Command     %3d   \"%s\"."%(
            cmd, Commands[cmd] ))

