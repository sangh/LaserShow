#!/usr/bin/python
"Simple text UI"

from pprint import pprint
from glyph import *
from seq import *
from comm import *

# This is to read a single char on win/unix
class _Getch:
    """Get one char from stdin.  Doesn't echo."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()
    def __call__(self): return self.impl()
class _GetchUnix:
    def __init__(self):
        import tty, sys
    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
class _GetchWindows:
    def __init__(self):
        import msvcrt
    def __call__(self):
        import msvcrt
        return msvcrt.getch()
getch = _Getch()
# End 1 char getter

# Convert from single keypress to index and back.
# Will need to add more at some point.
c2i = {
    '1':    0,
    '2':    1,
    '3':    2,
    '4':    3,
    '5':    4,
    '6':    5,
    '7':    6,
    '8':    7,
    '9':    8,
    '0':    9,
    'a':    10,
    'b':    11,
    'c':    12,
    'd':    13,
    'e':    14,
    'f':    15,
    'g':    16,
    'h':    17,
    'i':    18,
    'j':    19,
    'k':    20,
    'l':    21,
    'm':    22,
    'n':    23,
    'o':    24,
    'p':    25,
    'q':    26,
    'r':    27,
    's':    28,
    't':    29,
    'u':    30,
    'v':    31,
    'w':    32,
    'x':    33,
    'y':    34,
    'z':    35,
}
nIndexes = len( c2i )
def i2c( i ):
    for c in c2i:
        if i == c2i[c]:
            return c
    raise KeyError("No i 2 c mapping.")


# These are the commands to run.
def cmdSelTarget( lc = None ): pass
def cmdSetRotation( lc = None ): pass
def cmdShrink( lc = None ): pass
def cmdGlyphSend( lc = None ): pass
def cmdSendBytes( lc = None ): pass

def cmdPass( lc = None ):
    return None

def cmdRepeat( lc = None ):
    global cmdLast
    return cmdLast[2]( lc = lc )

def cmdQuit( lc = None ):
    bye(0,'OK, quitting.')

def cmdPlaySeq( lc = None ):
    "Select and play a sequence"
    if lc is None:
        ss = seqList()
        if len(ss) > nIndexes:
            wrn("Truncating num seq to %d."%(nIndexes))
            ss = ss[:nIndexes]
        print "Sequences: "
        for i in range( len( ss ) ):
            print "  %s: %s"%(i2c(i),ss[i])
        print "Enter a char to select sequences: ",
        c = getch()
        print
        try:
            seqToPlay = seqLoad( ss[ c2i[ c ] ] )
        except IndexError:
            wrn("Not a valid choice, going back to menu.")
            return None
        except:
            wrn(sys.exc_info())
            wrn("Could not load sequence,  going back to menu.")
            return None
    else:
        seqToPlay = lc
    try:
        seqPlay( seqToPlay )
        wrn("Done playing seq.")
        return seqToPlay
    except: 
        wrn(sys.exc_info())
        wrn("Could not play seq, going back to menu.")
        return None

def cmdStartRec( lc = None ): pass
def cmdTickClock( lc = None ): pass
def cmdTickCounter( lc = None ): pass
def cmdTickIndex( lc = None ): pass
def cmdOpenGlyphCreator( lc = None ): pass
def cmdStopRec( lc = None ): pass












# List the char to sel, fn, & desc.
# Cmds unique across all three tulpes.
cmdsBoth = (
    ('m', 'Move peripheral to target index', cmdSelTarget),
    ('o', 'Set XY rotation', cmdSetRotation),
    ('h', 'Shrink current glyph', cmdShrink),
    ('g', 'Send a glyph to a slot', cmdGlyphSend),
    ('b', 'Send 3 arbitrary bytes', cmdSendBytes),
    ('0', 'Do nothing', cmdPass),
    (' ', '(spacebar) repeat last command', cmdRepeat),
    ('q', 'Quit or exit', cmdQuit),
)
cmdsNorm = (
    ('p', 'Play sequence', cmdPlaySeq),
    ('s', 'Start recording sequence', cmdStartRec),
    ('t', 'Move peripheral x ticks clockwise', cmdTickClock),
    ('T', 'Move peri x ticks counterclockwise', cmdTickCounter),
    ('y', 'Set current tick to index', cmdTickIndex),
    ('c', 'Open the glyph creator', cmdOpenGlyphCreator),
)
cmdsRec = (
    ('S', 'Stop recording sequence', cmdStopRec),
)
cmdLast = (cmd for cmd in cmdsBoth if '0' == cmd[0]).next()
cmdLastArg = None
cmdState = cmdsNorm
tmp = []
for i in cmdsBoth + cmdsNorm + cmdsRec:
    if i[0] in tmp:
        bye(2,'Char "%s" is reused.'%(str(i[0])))
    tmp.append( i[0] )
del tmp

# And finally loop until exit.
while True:
    print "Commands:"
    for cmd in cmdsBoth + cmdState:
        print "  Press '%s' to '%s'."%( str(cmd[0]), cmd[1] )
    print "? ",
    c = getch()
    print
    try:
        cmdToRun = (cmd for cmd in (cmdsBoth + cmdState) if c == cmd[0]).next()
    except StopIteration:
        print "Cmd '%s' not found."%(str(c))
    print "Running '%s'..."%(cmdToRun[1])
    cmdLastArg = cmdToRun[2]( lc = cmdLastArg )
    if ' ' != cmdToRun[0]:  # If not repeat.
        cmdLast = cmdToRun
