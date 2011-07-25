#!/usr/bin/python

from header import *
import glyph as glyphModule
import seq as seqModule


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
        return rawSendCmd( peri, ord('T'), target )


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
        SlotsXY[slot] = glyph['name']
        return True
    else:
        return False


def sendGlyphSlowXY( slot, glyph ):
    "Send glyph to the slow XY."
    if slot >= NumSlotsSlowXY:
        wrn("Slot \"%d\" is invalid for the slow XY."%( slot ) )
        return False
    if sendGlyphToPeri( ord('x'), slot, glyph, ExpandPtsSlowXY ):
        SlotsSlowXY[slot] = glyph['name']
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


def seqPlay( s ):
    "Play the given seq, won't return until finished."
    if not seqModule.seqIsValid( s ):
        raise NameError("Given sequence is not valid, not plying.")
    import time
    wrn("Starting to play seq \"%s\"."%(s[0]))
    startTime = time.time()
    for cmd in s[1:]:
        sleepTime = startTime + cmd[0] - time.time()
        if( 0 < sleepTime ):
            time.sleep( sleepTime )
        if 2 == len( cmd ):
            rawSendCmd( *cmd[1] )
        else:
            # Is 3
            if ord('X') == cmd[1][0]:
                sendGlyphXY( cmd[1][1], glyphModule.glyphLoad( cmd[2] ) )
            elif ord('x') == cmd[1][0]:
                sendGlyphSlowXY( cmd[1][1], glyphModule.glyphLoad( cmd[2] ) )
            else:
                wrn('Not loading glyph \"%s\" as the peri \"%d\" is unknown.'%(cmd[2],cmd[1][0]))




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
                    wrn("Problem connecting to " +
                        "%s at port %d... will keep trying."%( h, p ) )
                    t = 10000
                else:
                    t = t - 1
    while True:
        try:
            clientSocket = []
            for h in SendToHosts:
                clientSocket.append( getClientSocket( h[0], h[1] ) )
                wrn("Connected to %s at port %d."%( h[0], h[1] ) )
            while True:
                try:
                    thrownaway = clientThreadQueue.get( False )
                except Queue.Empty:
                    break
            wrn("Dumped queue of anything left from before.")
            while True:
                o = clientThreadQueue.get( True, None )
                for s in clientSocket:
                    s.sendall( o )
        except Exception, detail:
            wrn( detail )
            wrn( "Caught an exception, re-connecting." )
            for s in clientSocket:
                try:
                    s.shutdown(socket.SHUT_RDWR)
                    s.close()
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

