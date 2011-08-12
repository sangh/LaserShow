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
    return selTargetHelper( ord('T'), lc )

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
    def gamePadThreadFn(q):
        try:
            p = subprocess.Popen( [
                "/usr/bin/jstest",
                "--event",
                "/dev/input/by-id/usb-Logitech_Logitech_RumblePad_2_USB-joystick",
                ], shell=False, stdout=subprocess.PIPE )
            while True:
                q.put(p.stdout.readline(),False)
        except:
            print sys.exc_info()
        finally:
            try:
                p.terminate()
                p.kill()
            except:
                pass
    gamePadQ = Queue.Queue(maxsize=100)
    gamePadThread = threading.Thread(target=gamePadThreadFn,args=(gamePadQ,))
    keyBoardThread = threading.Thread(target=lambda: raw_input())
    gamePadThread.daemon = True
    keyBoardThread.daemon = True
    gamePadThread.start()
    keyBoardThread.start()

    try: # Clear the queue of header, needs except if thread died.
        while True: jq.get(True,.01)
    except:
        pass
    # Lines from gamepad.
    # Event: type 2, time 17339776, number 1, value 19255
    r=re.compile("^Event: type ([0-9]), time ([0-9]+), number ([0-9]?[0-9]), value (-?[0-9]+)$")
    # Until Enter is pressed.
    while kt.isAlive() and jt.isAlive():
        print "Press enter on the keyboard to go back to the menu."
        try:
            l = jq.get(True, .2)
            rm = r.match(l)
            if rm:
                t = int(rm.group(1))
                ti = int(rm.group(2))
                n = int(rm.group(3))
                v = int(rm.group(4))
                print l.strip()
                print "t=%d  time=%d  num=%d  val=%d"%(t,ti,n,v)
            else:
                print "No.::%s::"%(l)
                break
        except Queue.Empty:
            pass
        except:
            print sys.exc_info()

























    try:
        p = subprocess.Popen( [
            "/usr/bin/jstest",
            "--event",
            "/dev/input/by-id/usb-Logitech_Logitech_RumblePad_2_USB-joystick",
            ], shell=False, stdout=subprocess.PIPE )
        print p.stdout.poll()
    except:
        wrn(sys.exc_info())
    try:
        p.terminate()
        p.kill()
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
            lc = ( p, 99, tic )
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
            lc = ( p, 12, tic )
        sendCmd( *lc )
        return lc
    except:
        wrn(sys.exc_info())
        wrn("Could not tic clock, going back to menu.")
        return None

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
    ('m', 'Move peripheral to target index', cmdSelTarget),
    ('[', 'Set step "10" to index "0"', lambda(lc): cmdSelTarget((10,0))),
    (']', 'Set step "10" to index "1"', lambda(lc): cmdSelTarget((10,1))),
    ('\\','Set step "10" to index "2"', lambda(lc): cmdSelTarget((10,2))),
    ('l', 'Set step "11" to index "0"', lambda(lc): cmdSelTarget((11,0))),
    (';', 'Set step "11" to index "1"', lambda(lc): cmdSelTarget((11,1))),
    ('\'','Set step "11" to index "2"', lambda(lc): cmdSelTarget((11,2))),
    (',', 'Set step "99" to index "0"', lambda(lc): cmdSelTarget((99,0))),
    ('.', 'Set step "99" to index "1"', lambda(lc): cmdSelTarget((99,1))),
    ('/', 'Set step "99" to index "2"', lambda(lc): cmdSelTarget((99,2))),
    ('o', 'Set XY rotation', cmdSetRotation),
    ('h', 'Shrink current glyph', cmdShrink),
    ('d', 'Display glyph in a slot on the XY', cmdGlyphSelect),
    ('D', 'Display glyph in a slot on the Slow XY', cmdGlyphSlowSelect),
    ('g', 'Send a glyph to a slot on the XY', cmdGlyphSend),
    ('G', 'Send a glyph to a slot on the slow XY', cmdGlyphSlowSend),
    ('P', 'Open the gamepad controller', cmdGamePad),
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
    ('b', 'Send 3 arbitrary bytes', cmdSendBytes),
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
