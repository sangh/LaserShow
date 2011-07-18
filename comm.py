#!/usr/bin/python

from header import *


def plist(peri=None,cmd=None):
    "List the peripherals.  See the readme."
    if peri is None:
        if cmd is not None:
            print "No peripheral given, but command given, makes no sense."
        else:
            for i in range(len(peripherals)):
                print
                plist(i)
    else:
        if peri >= len(peripherals):
            print "Invalid peripheral: %d."%(peri)
        elif cmd is None:
            print "Peripheral  %3d   %s:"%( peri, peripherals[peri][0] )
            for i in range(len(peripherals[peri][1])):
                plist(peri,i)
        elif cmd >= len(peripherals[peri][1]):
            print "Invaild command \"%d\" for peripheral \"%d\"."%(cmd,peri)
        else:
            print "    Command %3d, %3d   %s."%( peri, cmd, peripherals[peri][1][cmd] )

def setTarget( peri, target ):
    "Send command to set a stepper motor to ths given target number."
    "Use plist() to see what the numbers are for, and the readme for examples."
    "Returns True if it command was sent (probably), False otherwise."

    if peri < 2  or peri >= len(peripherals):
        print "Peripheral %d is not a stepper motor or is invalid."%( peri )
        return False
    if target >= len(peripherals[peri][1]):
        print "Invalid target \"%d\" for peripheral \"%d\"."%( target, peri )
        return False

    return clientThreadSend( chr( peri ) + chr( target ) + '\x00' )


def XYLoadGlyph( peri, slot ):
    "peri = 0 is the fast one, 1, is the slow one."
    "Tell the XY to use whatever glyph is in slot."
    "Return True if (probably) sent, False otherwise."
    if 0 == peri:
        if slot > XYNumSlots:
            print "Slot \"%d\" is invalid for the fast XY."%( slot )
            return False
        return clientThreadSend( '\x00' + chr( slot ) + '\x00' )
    elif 1 == peri:
        if slot > SlowXYNumSlots:
            print "Slot \"%d\" is invalid for the slow XY."%( slot )
            return False
        return clientThreadSend( '\x01' + chr( slot ) + '\x00' )
    else:
        print "Peri \"%d\" is not an XY." %( peri )
        return False



def XYSetGlyph( peri, slot, glyphName ):
    "Send a glyph to an XY."
    return False

def XYStartRotation( peri, dirSpeed ):
    "tell an XY to start rotating."
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
                    print "Problem connecting to ",
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

