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


def selPeriID():
    print "Peripherals: "
    pindexes = Peripherals.keys()
    for i in range( len( pindexes ) ):
        print "  %s: %s"%(i2c(i),Peripherals[pindexes[i]][0])
    print "Choose a peripheral by entering a char: ",
    c = getch()
    print c
    try:
        return pindexes[ c2i[ c ] ]
    except IndexError:
        wrn("Not a valid choice, going back to menu.")
        return None

# These are the commands to run.
def cmdSelTarget( lc = None ):
    if lc is None:
        p = selPeriID()
        if p is None:
            return None
        tindexes = Targets.keys()
        for i in range( len( tindexes ) ):
            print "  %s: %s"%(i2c(i),Targets[tindexes[i]])
        print "Choose a target index by entering a char: ",
        c = getch()
        print c
        try:
            ti = tindexes[ c2i[ c ] ]
        except IndexError:
            wrn("Not a valid choice, going back to menu.")
            return None
        else:
            lc = ( p, ti )
    setTarget( *lc )
    return lc

def cmdSetRotation( lc = None ):
    if lc is None:
        print( rotateXY.__doc__ )
        try:
            lc = float(raw_input("Enter a float in the range [0,1), followed by enter: "))
            if lc < 0  or lc >= 1:
                raise ValueError
        except ValueError:
            wrn("Not a float greater than or equal to 0 and less than 1.")
            return None
    rotateXY( lc )
    return lc

def cmdShrink( lc = None ):
    if lc is None:
        print( shrinkXY.__doc__ )
        try:
            lc = float(raw_input("Enter a float in the range [0,1], followed by enter: "))
            if lc < 0  or lc > 1:
                raise ValueError
        except ValueError:
            wrn("Not a float greater than or equal to 0 and less than or equal to 1.")
            return None
    shrinkXY( lc )
    return lc

def glyphSendHelper( fn, lc = None ):
    "Select and send a glyph"
    if lc is None:
        ss = glyphList()
        if len(ss) > nIndexes:
            wrn("Truncating num glyph to %d."%(nIndexes))
            ss = ss[:nIndexes]
        print "Glyphs: "
        for i in range( len( ss ) ):
            print "  %s: %s"%(i2c(i),ss[i])
        print "Enter a char to select a glyph: ",
        c = getch()
        print c
        try:
            glyphToSend = glyphLoad( ss[ c2i[ c ] ] )
        except IndexError:
            wrn("Not a valid choice, going back to menu.")
            return None
        except:
            wrn(sys.exc_info())
            wrn("Could not load glyph,  going back to menu.")
            return None
        try:
            slt = int(raw_input("Enter a decimal byte for the slot to load into, followed by enter: "))
            chr(slt)
        except ValueError:
            wrn("Not a decimal byte.")
            return None
        lc = ( slt, glyphToSend )
    try:
        fn( *lc )
    except:
        wrn(sys.exc_info())
        wrn("Could not send glyph, going back to menu.")
        return None
    return lc

def cmdGlyphSend( lc = None ):
    return glyphSendHelper( sendGlyphXY, lc )

def cmdGlyphSlowSend( lc = None ):
    return glyphSendHelper( sendGlyphSlowXY, lc )

def cmdSendBytes( lc = None ):
    try:
        if lc is None:
            p = selPeriID()
            if p is None:
                return None
            ret = eval(raw_input("Enter 3 decimal bytes separated by commans, followed by enter: "))
            if len(ret) != 3:
                raise ValueError
            lc = ( Peripherals[p][1], int(ret[0]), int(ret[1]), int(ret[2]) )
        rawSend( *lc )
        return lc
    except:
        wrn(sys.exc_info())
        wrn("Could not send raw cmd, going back to menu.")
        return None

def cmdPass( lc = None ):
    wrn("Doing nothing.")
    return None

def cmdRepeat( lc = None ):
    global cmdLast
    print "-->", cmdLast[1], "with arguments", lc
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
        print "Enter a char to select a sequence: ",
        c = getch()
        print c
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

def cmdStartRec( lc = None ):
    wrn("Not implemented yet.")
    return lc

def cmdTickClock( lc = None ):
    wrn("Not implemented yet.")
    return lc

def cmdTickCounter( lc = None ):
    wrn("Not implemented yet.")
    return lc

def cmdTickIndex( lc = None ):
    wrn("Not implemented yet.")
    return lc

def cmdOpenGlyphCreator( lc = None ):
    wrn("Not implemented yet.")
    return lc

def cmdStopRec( lc = None ):
    wrn("Not implemented yet.")
    return lc













# List the char to sel, fn, & desc.
# Cmds unique across all three tulpes.
cmdsBoth = (
    ('m', 'Move peripheral to target index', cmdSelTarget),
    ('o', 'Set XY rotation', cmdSetRotation),
    ('h', 'Shrink current glyph', cmdShrink),
    ('g', 'Send a glyph to a slot on the XY', cmdGlyphSend),
    ('G', 'Send a glyph to a slot on the slow XY', cmdGlyphSlowSend),
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
    print c
    try:
        cmdToRun = (cmd for cmd in (cmdsBoth + cmdState) if c == cmd[0]).next()
    except StopIteration:
        print "Cmd '%s' not found."%(str(c))
    else:
        print "Running '%s'..."%(cmdToRun[1])
        if ' ' == cmdToRun[0]:  # If repeat.
            cmdLastArg = cmdToRun[2]( lc = cmdLastArg )
        else:
            cmdLastArg = cmdToRun[2]( lc = None )
            cmdLast = cmdToRun
