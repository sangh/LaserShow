#!/usr/bin/python
"Simple text UI"

import subprocess
import threading
import Queue
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
    '-':    36,
    '=':    37,
    '[':    38,
    ']':    39,
    '\\':   40,
    ';':    41,
    '\'':   42,
    ',':    43,
    '.':    44,
    '/':    45,
    '_':    46,
    '+':    47,
    '{':    48,
    '}':    49,
    '|':    50,
    ':':    51,
    '"':    52,
    '<':    53,
    '>':    54,
    '?':    55,
    'A':    56,
    'B':    57,
    'C':    58,
    'd':    59,
    'E':    60,
    'F':    61,
    'G':    62,
    'H':    63,
    'I':    64,
    'J':    65,
    'K':    66,
    'L':    67,
    'M':    68,
    'N':    69,
    'O':    70,
    'P':    71,
    'Q':    72,
    'R':    73,
    'S':    74,
    'T':    75,
    'U':    76,
    'V':    77,
    'W':    78,
    'X':    79,
    'Y':    80,
    'Z':    81,
    '`':    82,
    '~':    83,
    '!':    84,
    '@':    85,
    '#':    86,
    '$':    87,
    '%':    88,
    '^':    89,
    '&':    90,
    '*':    91,
    '(':    92,
    ')':    93,
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

def selTargetHelper( lasercmd, lc ):
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
    sendCmd( lc[0], lasercmd, lc[1] )
    return lc

def cmdSelTarget( lc = None ):
    return selTargetHelper( 3, lc )

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

def cmdGlyphSelect( lc = None ):
    try:
        if lc is None:
            lc = int(raw_input("Enter a decimal byte for the slot to select, followed by enter: "))
            chr(lc)
        selectGlyphXY( lc )
    except ValueError:
        wrn("Not a decimal byte.")
        return None

def cmdGlyphSlowSelect( lc = None ):
    try:
        if lc is None:
            lc = int(raw_input("Enter a decimal byte for the slot to select, followed by enter: "))
            chr(lc)
        selectGlyphSlowXY( lc )
    except ValueError:
        wrn("Not a decimal byte.")
        return None

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

def cmdGamePad( lc = None ):
    def gp2byte( s ):
        return int((int(s)+32767)*256.0/65536)
    try:
        gamePadProc = subprocess.Popen( [
            "/usr/bin/jstest",
            "--event",
            "/dev/input/by-id/usb-Logitech_Logitech_RumblePad_2_USB-joystick",
            ], shell=False, stdout=subprocess.PIPE )

        wrn("")
        wrn("Press button # 9 to exit.")
        wrn("")
        # Lines from gamepad.
        # Event: type 2, time 17339776, number 1, value 19255
        r=re.compile("^Event: type ([0-9]+), time ([0-9]+), number ([0-9]?[0-9]), value (-?[0-9]+)$")
        while True:
            line = gamePadProc.stdout.readline()
            if "" == line:
                if gamePadProc.poll() is not None:
                    break # proc died.
            rm = r.match(line)
            if rm:
                btype = int(rm.group(1))
                if 1 == btype:
                    if "0" == rm.group(4):
                        continue  # ignore all button releases
                    butt = int(rm.group(3))
                    if 8 == butt:  # Button # 9
                        break # exit button
                    elif 0 == butt:  # button # 1
                        cmdSelTarget((0,0))
                    elif 1 == butt:  # button # 2
                        cmdSelTarget((0,1))
                    elif 2 == butt:  # button # 3
                        cmdSelTarget((0,2))
                    elif 3 == butt:  # button # 4
                        cmdSelTarget((1,0))
                    elif 4 == butt:  # button # 5
                        cmdSelTarget((1,1))
                    elif 5 == butt:  # button # 6
                        cmdSelTarget((1,2))
                    elif 6 == butt:  # button # 6
                        cmdSelTarget((2,0))
                    elif 7 == butt:  # button # 8
                        cmdSelTarget((2,1))
                    elif 9 == butt:  # button # 10
                        cmdSelTarget((2,2))
                elif 2 == btype:
                    butt = int(rm.group(3))
                    if 2 == butt:  # lower right joystick x-axis
                        sendCmd(6, 6, gp2byte( rm.group(4) ) )
                    elif 3 == butt:  # lower right joystick y-axis
                        sendCmd(6, 7, gp2byte( rm.group(4) ) )
                else:  # ignore other types.
                    continue
            else:
                wrn( line.strip() )
    except:
        wrn(sys.exc_info())
    finally:
        try:
            gamePadProc.terminate()
            gamePadProc.kill()
        except:
            pass
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
    global cmdState
    global cmdsRec
    try:
        seqRecorderStart()
        cmdState = cmdsRec
    except:
        wrn(sys.exc_info())
    return None

def cmdTickClock( lc = None ):
    try:
        if lc is None:
            p = selPeriID()
            if p is None:
                return None
            tic = int(eval(raw_input("Enter num ticks, followed by enter: ")))
            chr(tic)
            lc = ( p, 1, tic )
        sendCmd( *lc )
        return lc
    except:
        wrn(sys.exc_info())
        wrn("Could not tic clock, going back to menu.")
        return None

def cmdTickCounter( lc = None ):
    try:
        if lc is None:
            p = selPeriID()
            if p is None:
                return None
            tic = int(eval(raw_input("Enter num ticks, followed by enter: ")))
            chr(tic)
            lc = ( p, 2, tic )
        sendCmd( *lc )
        return lc
    except:
        wrn(sys.exc_info())
        wrn("Could not tic clock, going back to menu.")
        return None
idxs = [0,0,0]
def cmdMoveToIdx( grb, idx ):
    global idxs
    oldidx = idxs[grb]
    if idx > oldidx:
        for i in range( idx - oldidx ):
            sendCmd(grb, 2, 1)
    else:
        for i in range( oldidx - idx ):
            sendCmd(grb, 1, 1)
    idxs[grb] = idx

def cmdTickIndex( lc = None ):
    return selTargetHelper( 5, lc )

def cmdOpenGlyphCreator( lc = None ):
    try:
        execfile("glyphCreator.py")
    except:
        wrn(sys.exc_info())
        wrn("Could not open it, going back to menu.")
    return None

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

def cmdStopRec( lc = None ):
    global cmdState
    global cmdsNorm
    try:
        s = seqRecorderStop()
        print s
    except:
        wrn(sys.exc_info())
        return None
    cmdState = cmdsNorm
    while True:
        try:
            n = raw_input("Enter a name for the sequence: ")
            seqDump( [n,] + s )
            return None
        except:
            wrn(sys.exc_info())
        n = raw_input("Try to store again ([Yes]/no) ? ")
        if 0 < len(n)  and  "n" == n[0].lower():
            return None








# List the char to sel, fn, & desc.
# Cmds unique across all three tulpes.
cmdsBoth = (
    ('M', 'Move peripheral to target index', cmdSelTarget),
    ('1', 'Move green 1 idx left', lambda(lc): cmdTickCounter((0,2,1))),
    ('2', 'Move green 1 idx right', lambda(lc): cmdTickClock((0,1,1))),
    ('3', 'Move red 1 idx left', lambda(lc): cmdTickCounter((1,2,1))),
    ('4', 'Move red 1 idx right', lambda(lc): cmdTickClock((1,1,1))),
    ('5', 'Move blue 1 idx left', lambda(lc): cmdTickClock((2,1,1))),
    ('6', 'Move blue 1 idx right', lambda(lc): cmdTickCounter((2,2,1))),
    ('q', 'Green idx 0', lambda(lc): cmdMoveToIdx(0,0)),
    ('w', 'Green idx 1', lambda(lc): cmdMoveToIdx(0,1)),
    ('e', 'Green idx 2', lambda(lc): cmdMoveToIdx(0,2)),
    ('r', 'Green idx 3', lambda(lc): cmdMoveToIdx(0,3)),
    ('t', 'Green idx 4', lambda(lc): cmdMoveToIdx(0,4)),
    ('y', 'Green idx 5', lambda(lc): cmdMoveToIdx(0,5)),
    ('u', 'Green idx 6', lambda(lc): cmdMoveToIdx(0,6)),
    ('i', 'Green idx 7', lambda(lc): cmdMoveToIdx(0,7)),
    ('o', 'Green idx 8', lambda(lc): cmdMoveToIdx(0,8)),
    ('p', 'Green idx 9', lambda(lc): cmdMoveToIdx(0,9)),
    ('[', 'Green idx 10', lambda(lc): cmdMoveToIdx(0,10)),
    ('a', 'Red idx 0', lambda(lc): cmdMoveToIdx(1,0)),
    ('s', 'Red idx 1', lambda(lc): cmdMoveToIdx(1,1)),
    ('d', 'Red idx 2', lambda(lc): cmdMoveToIdx(1,2)),
    ('f', 'Red idx 3', lambda(lc): cmdMoveToIdx(1,3)),
    ('g', 'Red idx 4', lambda(lc): cmdMoveToIdx(1,4)),
    ('h', 'Red idx 5', lambda(lc): cmdMoveToIdx(1,5)),
    ('j', 'Red idx 6', lambda(lc): cmdMoveToIdx(1,6)),
    ('k', 'Red idx 7', lambda(lc): cmdMoveToIdx(1,7)),
    ('l', 'Red idx 8', lambda(lc): cmdMoveToIdx(1,8)),
    (';', 'Red idx 9', lambda(lc): cmdMoveToIdx(1,9)),
    ('\'', 'Red idx 10', lambda(lc): cmdMoveToIdx(1,10)),
    ('z', 'Blue idx 0', lambda(lc): cmdMoveToIdx(2,0)),
    ('x', 'Blue idx 1', lambda(lc): cmdMoveToIdx(2,1)),
    ('c', 'Blue idx 2', lambda(lc): cmdMoveToIdx(2,2)),
    ('v', 'Blue idx 3', lambda(lc): cmdMoveToIdx(2,3)),
    ('b', 'Blue idx 4', lambda(lc): cmdMoveToIdx(2,4)),
    ('n', 'Blue idx 5', lambda(lc): cmdMoveToIdx(2,5)),
    ('m', 'Blue idx 6', lambda(lc): cmdMoveToIdx(2,6)),
    (',', 'Blue idx 7', lambda(lc): cmdMoveToIdx(2,7)),
    ('.', 'Blue idx 8', lambda(lc): cmdMoveToIdx(2,8)),
    ('/', 'Blue idx 9', lambda(lc): cmdMoveToIdx(2,9)),
    #('O', 'Set XY rotation', cmdSetRotation),
    #('H', 'Shrink current glyph', cmdShrink),
    #('F', 'Display glyph in a slot on the XY', cmdGlyphSelect),
    #('D', 'Display glyph in a slot on the Slow XY', cmdGlyphSlowSelect),
    #('T', 'Send a glyph to a slot on the XY', cmdGlyphSend),
    #('G', 'Send a glyph to a slot on the slow XY', cmdGlyphSlowSend),
    #('P', 'Open the gamepad controller', cmdGamePad),
    ('0', 'Do nothing', cmdPass),
    (' ', '(spacebar) repeat last command', cmdRepeat),
    ('Q', 'Quit or exit', cmdQuit),
)
cmdsNorm = (
    ('L', 'Play sequence', cmdPlaySeq),
    ('S', 'Start recording sequence', cmdStartRec),
    ('Z', 'Move peripheral x ticks clockwise', cmdTickClock),
    ('X', 'Move peri x ticks counterclockwise', cmdTickCounter),
    ('Y', 'Set current tick to index', cmdTickIndex),
    ('C', 'Open the glyph creator', cmdOpenGlyphCreator),
    ('B', 'Send 3 arbitrary bytes', cmdSendBytes),
)
cmdsRec = (
    ('A', 'Stop recording sequence', cmdStopRec),
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
recSeq = []  # seq to rec

# And finally loop until exit.
while True:
    print "Slots:"
    print "  SlotsXY: ", SlotsXY
    print "  SlotsSlowXY: ", SlotsSlowXY
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
