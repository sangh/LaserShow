#!/usr/bin/python

from header import *


def plist( peri = None ):
    "List the peripherals.  See the readme."
    if peri in Peripherals:
        print "Peripheral  %3d   \"%s\":"%(
            peri, Peripherals[peri][0] )
        for cmd in Peripherals[peri][1]:
            print "    Command %3d   \"%s\"."%(
                cmd, Commands[cmd] )
        for t in Peripherals[peri][2]:
            print "      Target%3d   \"%s\"."%(
            t, Peripherals[peri][2][t] )
    elif peri is None:
        for i in Peripherals:
            print
            plist(i)
    else:
        print "Invalid peripheral: %d."%(peri)

def rawSendCmd( peri, cmd, arg ):
    "Send a command to peri with arg.  Everything is 3-byte packets."
    "No error checking is done, only all of peri, cmd, & arg must be"
    "integres between 0 and 255 inclusive."
    "Returns True if it command was sent (probably), False otherwise."
    try:
        return clientThreadSend( chr( peri ) + chr( cmd ) + chr( arg ) )
    except TypeError:
        print "One of ( peri, cmd, arg ) = ",
        print "( %s, %s, %s ) is not an int."%( peri, cmd, arg )
        return False
    except ValueError:
        print "One of ( peri, cmd, arg ) = ",
        print "( %s, %s, %s ) is out of range [0,255]."%( peri, cmd, arg )
        return False

def setTarget( peri, target ):
    "Send command to set a stepper motor to ths given target number."
    "Use plist() to see what the numbers are for, and the readme for examples."
    "Returns True if it command was sent (probably), False otherwise."

    if peripheralCommandIsValid( peri, ord('T') ):
        if target in Peripherals[peri][2]:
            return rawSendCmd( peri, ord('T'), target )
        else:
            print "Invalid target \"%d\" for peripheral \"%d\"."%( target, peri )
            return False


def selectGlyphXY( slot ):
    "Make the fast XY display the glyph in `slot'."
    if slot >= NumSlotsXY:
        print "Slot \"%d\" is invalid for the fast XY."%( slot )
        return False
    return rawSendCmd( ord('X'), 3, slot )

def selectGlyphXYSlow( slot ):
    "Make the slow XY display the glyph in `slot'."
    if slot >= NumSlotsXYSlow:
        print "Slot \"%d\" is invalid for the slow XY."%( slot )
        return False
    return rawSendCmd( ord('x'), 3, slot )

def sendGlyphXY( slot, glyph ):
    "Send glyph to the XY."
    return False

def sendGlyphXYSlow( slot, glyph ):
    "Send glyph to the slow XY."
    return False

def rotateXY( angle ):
    "tell an XY to move to angle."
    return False

def shrinkXY( angle ):
    "tell an XY to shrink."
    return False







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
                    print "Problem connecting to",
                    print "%s at post %d... will keep trying."%( Host, Port )
                    t = 10000
                else:
                    t = t - 1
    while True:
        try:
            clientSocket = getClientSocket( Host, Port )
            print "Connected to %s at post %d."%( Host, Port )
            while True:
                clientSocket.sendall( clientThreadQueue.get( True, None ) )
        except Exception, detail:
            print detail
            print "Caught an exception, re-connecting."
            try:
                clientSocket.shutdown(socket.SHUT_RDWR)
                clientSocket.close()
            except:
                pass

# Queus is only shared, it has a size of one, so if full then, the send failed.
# There is an implicit buffer in that if an item is pulled from the queue and
# the socket is closed, another item can be added to the queue and then the
# when the socket is reestablished the pulled item and the queued one will
# be the first sent.
clientThreadQueue = Queue.Queue(maxsize=1)
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

