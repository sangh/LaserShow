#!/usr/bin/python

import time
import threading
from header import *
import glyph as glyphModule
import seq as seqModule


# You almost certainly want to be using ons of the fn below
# instead of this function.
def rawSend( hostPortKey, byte1, byte2, byte3 ):
    """Send these three bytes with no checking, that is
    of course apart from being a real hostPortKey and
    the bytes are ints between 0 and 255."""
    try:
        clientThreadSend(   hostPortKey,
                            '\xff' + chr( byte1 ) + chr( byte2 ) + chr( byte3 ) + '\xff' )
    except TypeError:
        raise TypeError("One of the bytes aren't ints: " +
            "( %s, %s, %s )."%( str(byte1), str(byte2), str(byte3) ) )
    except ValueError:
        raise ValueError("One of the bytes are out of range [0,255]: " +
            "( %s, %s, %s )."%( str(byte1), str(byte2), str(byte3) ) )

# Start recording a seq from all threads at once.
seqRecorderSem = threading.Semaphore(1)
seqRecorder = None
seqRecorderStartTime = 0
def seqRecorderStart():
    global seqRecorderSem
    global seqRecorder
    global seqRecorderStartTime
    seqRecorderSem.acquire()
    if seqRecorder is not None:
        seqRecorderSem.release()
        raise ValueError("Already recording, cannot start again.")
    else:
        seqRecorder = []
        seqRecorderStartTime = time.time()
        seqRecorderSem.release()
def seqRecorderStop():
    global seqRecorderSem
    global seqRecorder
    seqRecorderSem.acquire()
    if seqRecorder is None:
        seqRecorderSem.release()
        raise ValueError("Not recording, so can't stop.")
    else:
        ret = seqRecorder
        seqRecorder = None
        seqRecorderSem.release()
        return ret
def seqRecorderAdd( b1, b2, b3 ):
    global seqRecorderSem
    global seqRecorder
    global seqRecorderStartTime
    seqRecorderSem.acquire()
    if seqRecorder is not None:
        timeDelay = time.time() - seqRecorderStartTime
        seqRecorder.append( ( timeDelay, ( b1, b2, b3, ), ) )
    seqRecorderSem.release()
def seqRecorderAddGlyphNameToLast( gn ):
    global seqRecorderSem
    global seqRecorder
    seqRecorderSem.acquire()
    if seqRecorder is not None:
        seqRecorder[-1] = tuple( list( seqRecorder[-1] ) + [gn,] )
    seqRecorderSem.release()


def sendCmd( peri, cmd, arg ):
    """Send a command to peri with arg.  Everything is 3-byte packets.
    Minimal error checking is done."""
    try:
        rawSend( Peripherals[peri][1], peri, cmd, arg )
        seqRecorderAdd( peri, cmd, arg )
    except KeyError:
        raise KeyError("Peri is invalid: '%s'."%(str(peri)))

def setTarget( peri, target ):
    """Send command to set a stepper motor to ths given target number.
    See header.py for what the numbers are for, and the readme for examples."""
    if target in Targets.keys():
        sendCmd( peri, 3, target )
    else:
        raise NameError("Invaild target (%s)."%(str(target)))

def selectGlyphXY( slot ):
    """Make the fast XY display the glyph in `slot'."""
    if slot >= NumSlotsXY:
        raise NameError("Slot \"%d\" is invalid for the fast XY."%( slot ) )
    sendCmd( 5, 7, slot )

def selectGlyphSlowXY( slot ):
    """Make the slow XY display the glyph in `slot'."""
    if slot >= NumSlotsSlowXY:
        raise NameError("Slot \"%d\" is invalid for the slow XY."%( slot ) )
    sendCmd( 6, 3, slot )

# Use sendGlyphXY or sendGlyphSlowXY instead of this fn.
def sendGlyphToPeri( peri, slot, glyph, expandToThisManyPoints ):
    """Use sendGlyphXY or sendGlyphSlowXY instead of this fn."""
    exGlyph = glyphModule.glyphExpandToPts( expandToThisManyPoints, glyph )
    sendCmd( peri, 30, slot )
    seqRecorderAddGlyphNameToLast( glyph['name'] )
    for p in exGlyph:
        rawSend( Peripherals[peri][1], p[0], p[1], p[2] )

def sendGlyphXY( slot, glyph ):
    """Send glyph to the XY."""
    if slot >= NumSlotsXY:
        raise NameError("Slot \"%d\" is invalid for the fast XY."%( slot ) )
    sendGlyphToPeri( 5, slot, glyph, ExpandPtsXY )
    SlotsXY[slot] = glyph['name']


def sendGlyphSlowXY( slot, glyph ):
    """Send glyph to the slow XY."""
    if slot >= NumSlotsSlowXY:
        raise NameError("Slot \"%d\" is invalid for the slow XY."%( slot ) )
    sendGlyphToPeri( 6, slot, glyph, ExpandPtsSlowXY )
    SlotsSlowXY[slot] = glyph['name']

# Really just an example for the rest of the commands.
def rotateXY( angle ):
    """Tell fast XY to move to angle:
    0.0 is normal (upright),
    0.25 is 90 degrees on the right (clockwise) side,
    0.5 is upside-down,
    0.74 is 90 degrees on the left side."""
    sendCmd( 5, 41, int(255*angle) )

def shrinkXY( size ):
    """Tell fast XY to shrink to size: 
    0.0 is shrink to nothing,
    1.0 is keep it full size,
    0.5 is make it half size."""
    sendCmd( 5, 40, int(255*size) )


def seqPlay( s ):
    """Play the given seq, won't return until finished."""
    if not seqModule.seqIsValid( s ):
        raise NameError("Given sequence is not valid, not plying.")
    wrn("Starting to play seq \"%s\"."%(s[0]))
    startTime = time.time()
    for cmd in s[1:]:
        sleepTime = startTime + cmd[0] - time.time()
        if( 0 < sleepTime ):
            time.sleep( sleepTime )
        if 2 == len( cmd ):
            sendCmd( *cmd[1] )
        else:
            # Is 3
            if 5 == cmd[1][0]:
                sendGlyphXY( cmd[1][1], glyphModule.glyphLoad( cmd[2] ) )
            elif 6 == cmd[1][0]:
                sendGlyphSlowXY( cmd[1][1], glyphModule.glyphLoad( cmd[2] ) )
            else:
                wrn('Not loading glyph \"%s\" as the peri \"%d\" is unknown.'%(cmd[2],cmd[1][0]))




###
### This is all the socket stuff below.
###
import socket
import Queue
# Thread for a single socket/queue
def clientThreadRun( hostPort, clientQueue ):
    "hostPort could be a string, a file to use."
    def getClientSocket( hostPort ):
        "Return 2 fn, to send and close."
        t = 0
        while True:
            try:
                if isinstance( hostPort, str ):
                    f = open( hostPort, "a" )
                    def sendfn( s ):
                        f.write( s )
                        f.flush()
                    return ( sendfn, f.close )
                else:  # should be a tuple, ( host, port )
                    s = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
                    s.connect( hostPort )
                    def closefn():
                        soc.shutdown(socket.SHUT_RDWR)
                        soc.close()
                    return ( s.sendall, closefn )
            except:
                if 0 == t:
                    wrn(sys.exc_info())
                    wrn("Problem connecting to " +
                        "%s... will keep trying."%( str( hostPort ) ) )
                    t = 30000
                else:
                    t = t - 1
    while True:
        try:
            sendfn, closefn = getClientSocket( hostPort )
            wrn("Connected to %s."%( str( hostPort ) ) )
            while True:
                try:
                    thrownaway = clientQueue.get( False )
                except Queue.Empty:
                    break
            wrn("%s: Queue dumped."%(str(hostPort)))
            while True:
                sendfn( clientQueue.get( True, None ) )
        except Exception, detail:
            wrn( detail )
            wrn( "Caught an exception, re-connecting." )
            try:
                closefn()
            except:
                pass

# Queue is only shared var for each unique host/port defined in Peripheral.
# There is no real way for the app to tell if something get sent, unless
# we want each call to block until successful.
clientThreadQueues = {}
for p in Peripherals:
    clientThreadQueues[ Peripherals[p][1] ] = None
QueueMaxSize = 2 * max( ExpandPtsSlowXY, ExpandPtsXY )
clientThreads = {}
for p in clientThreadQueues:
    clientThreadQueues[p] = Queue.Queue( maxsize = QueueMaxSize )
    clientThreads[p] = threading.Thread(
        name = "clientThread: %s"%(str(p)),
        target = clientThreadRun,
        args = ( p, clientThreadQueues[p] ),
    )
    clientThreads[p].daemon = True # Exit if main thread exits.
    clientThreads[p].start()
# Fn to send it.
def clientThreadSend( hostPort, s ):
    global clientThreadQueues
    try:
        clientThreadQueues[hostPort].put( s, False )
    except Queue.Full:
        wrn("Queue full for %s."%(str(hostPort)))
### End of all thread stuff.

