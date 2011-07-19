#!/usr/bin/python

from header import *
import glyph as glyphModule


def plist( peri = None ):
    "List the peripherals.  See the readme."
    if peri in Peripherals:
        wrn("Peripheral  %3d   \"%s\":"%(
            peri, Peripherals[peri][0] ))
        for cmd in Peripherals[peri][1]:
            wrn("    Command %3d   \"%s\"."%(
                cmd, Commands[cmd] ))
        for t in Peripherals[peri][2]:
            wrn("      Target%3d   \"%s\"."%(
            t, Peripherals[peri][2][t] ))
    elif peri is None:
        for i in Peripherals:
            wrn("")
            plist(i)
    else:
        wrn("Invalid peripheral: %d."%(peri))

def rawSendCmd( peri, cmd, arg ):
    "Send a command to peri with arg.  Everything is 3-byte packets."
    "No error checking is done, only all of peri, cmd, & arg must be"
    "integres between 0 and 255 inclusive."
    "Returns True if it command was sent (probably), False otherwise."
    try:
        return clientThreadSend( chr( peri ) + chr( cmd ) + chr( arg ) )
    except TypeError:
        wrn("One of ( peri, cmd, arg ) = " +
            "( %s, %s, %s ) is not an int."%( peri, cmd, arg ) )
        return False
    except ValueError:
        wrn("One of ( peri, cmd, arg ) = " +
            "( %s, %s, %s ) is out of range [0,255]."%( peri, cmd, arg ) )
        return False

def setTarget( peri, target ):
    "Send command to set a stepper motor to ths given target number."
    "Use plist() to see what the numbers are for, and the readme for examples."
    "Returns True if it command was sent (probably), False otherwise."

    if peripheralCommandIsValid( peri, ord('T') ):
        if target in Peripherals[peri][2]:
            return rawSendCmd( peri, ord('T'), target )
        else:
            wrn("Invalid target \"%d\" for peripheral \"%d\"."%( target, peri ) )
            return False


def selectGlyphXY( slot ):
    "Make the fast XY display the glyph in `slot'."
    if slot >= NumSlotsXY:
        wrn("Slot \"%d\" is invalid for the fast XY."%( slot ) )
        return False
    return rawSendCmd( ord('X'), 3, slot )

def selectGlyphSlowXY( slot ):
    "Make the slow XY display the glyph in `slot'."
    if slot >= NumSlotsSlowXY:
        wrn("Slot \"%d\" is invalid for the slow XY."%( slot ) )
        return False
    return rawSendCmd( ord('x'), 3, slot )

def sendGlyphToPeri( peri, slot, glyph, expandToThisManyPoints ):
    "Use sendGlyphXY or sendGlyphSlowXY instead of this fn."
    exGlyph = glyphModule.glyphExpandToPts( expandToThisManyPoints, glyph )
    if( not rawSendCmd( peri, 193, slot ) ):
        return False
    for p in exGlyph:
        if( not rawSendCmd( p[0], p[1], p[2] ) ):
            return False
    return True

def sendGlyphXY( slot, glyph ):
    "Send glyph to the XY."
    if slot >= NumSlotsXY:
        wrn("Slot \"%d\" is invalid for the fast XY."%( slot ) )
        return False
    if sendGlyphToPeri( ord('X'), slot, glyph, ExpandPtsXY ):
        slotsXY[slot] = glyph['name']
        return True
    else:
        return False


def sendGlyphSlowXY( slot, glyph ):
    "Send glyph to the slow XY."
    if slot >= NumSlotsSlowXY:
        wrn("Slot \"%d\" is invalid for the slow XY."%( slot ) )
        return False
    if sendGlyphToPeri( ord('x'), slot, glyph, ExpandPtsSlowXY ):
        slotsSlowXY[slot] = glyph['name']
        return True
    else:
        return False

def rotateXY( angle ):
    "Tell fast XY to move to angle:"
    "0.0 is no change (upright),"
    "0.25 is 90 degrees on the right (clockwise) side,"
    "0.5 is upside-down,"
    "0.74 is 90 degreer on the left side."
    return rawSendCmd( ord('X'), ord('R'), int(255*angle) )

def shrinkXY( size ):
    "Tell fast XY to shrink to size: "
    "0.0 is shrink to nothing,"
    "1.0 is keep it full size,"
    "0.5 is make it half size."
    return rawSendCmd( ord('X'), 112, int(255*size) )







###
### This is all the socket stuff below.
###
import socket
import threading
import Queue
def clientThreadRun():
    global clientThreadQueue
    def getClientSocket(h,p):
        t = 0
        while True:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((h,p))
                return s
            except:
                if 0 == t:
                    wrn("Problem connecting to" +
                        "%s at post %d... will keep trying."%( Host, Port ) )
                    t = 10000
                else:
                    t = t - 1
    while True:
        try:
            clientSocket = getClientSocket( Host, Port )
            wrn("Connected to %s at post %d."%( Host, Port ) )
            while True:
                clientSocket.sendall( clientThreadQueue.get( True, None ) )
        except Exception, detail:
            wrn( detail )
            wrn( "Caught an exception, re-connecting." )
            try:
                clientSocket.shutdown(socket.SHUT_RDWR)
                clientSocket.close()
            except:
                pass

# Queus is only shared, it has a size of at leat expand pts size, so if full
# then, the send failed.  There is an implicit buffer in that if an item is
# pulled from the queue and
# the socket is closed, another item can be added to the queue and then the
# when the socket is reestablished the pulled item and the queued one will
# be the first sent.
clientThreadQueue = Queue.Queue( maxsize = max( ExpandPtsSlowXY, ExpandPtsXY ) )
clientThread = threading.Thread( target = clientThreadRun, name="clientThread")
clientThread.daemon = True # Exit if main thread exits.
clientThread.start()
def clientThreadSend( s ):
    "Send an item to comm, ret true if it (probably) was sent."
    global clientThreadQueue
    try:
        clientThreadQueue.put( s, False )
        return True
    except Queue.Full:
        return False
### End of all thread stuff.

