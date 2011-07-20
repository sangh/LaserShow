Overview of the LaserShow Software Interface
============================================

This interface is for a single laser at J&J's party in Aug.


Definitions
-----------

*   *Peripheral* is HW that can take commands, right now this means
    steppes motors, the fast XY, and the slow XY.  (Does the
    diffraction grating count?)
*   *Command* is something you can tell a peripheral to do.
*   *Slot* is a memory space on each XY that can hold ExpandPtsXY
    or ExpandPtsSlowXY triplets making up a glyph.  This glyph
    can be selected to display, and each can be re-loaded from
    the SW at will.
*   *Glyph* is a list of XY positions and flags that make up a
    still image or frame.  This can then be manipulated in time,
    but each XY will just repeat drawing this.  In the case of the
    fast XY it shold look like a complete image, and in the case
    of the slow one each movement may be visable as the image moving
    around the room.
*   *Triplet* is a set of 3 bytes.  Everything is sent in 3 byte
    chunks to the HW.  Apart from when a glyph is being sent to
    a slot (still in 3-byte chunks: XYF where F are flags, right
    now that just 0 for not blanked, 1 for blanked), this is
    PCA, where P=peripheral-ID, C=command, and A=argument.
*   *Tick* is one position of a stepper motor, each will have a
    different number and they are not directly visible in SW.
*   *Index* is a pre-defined place a stepper motor can go defined
    by a byte listed in the Peripheral dictionary.
*   *Target* is a physical place a stepper motor could point to,
    they are not visible from SW, but usually indexes will tell
    one to point to a target.


Header
------

These are the hard-coded things that _every_ class sees.

The big thing in here are the dicts of peripherals and commands.  These
are currently set to random numbers (that are the actual bytes sent to
the HW), so feel free to change them to whatever the HW expects.  There are a few
assumptions I'm making, however.

Each dict key must be [0,255], or stuff will break.

Commands.  I'm assuming the list of Commands is universal, meaning
that any command could (via programmer error) be sent to any
peripheral and it should be smart enough to ignore it if it can't do
it or it doesn't make sense for that peripheral.

Peripherals.  Each one is listed with it's targets in the dict.  When
the configuration changes it should be easy to modify the dict.  The
thing is that there could be multiple hosts that the SW sends commands
to, but everything will go to all of them, so if a peripheral gets a command
for another one it should ignore it.  This shouldn't be hard in most cases
as the first byte of most triplets is the peripheral ID, but when a glyph
is being sent they need to ignore all the bytes sent for it, which means
they have to timeout in an intelligent way if comms fail.



The "comm" or Communications Interface
----------------------------------------

This class takes care of talking to the hardware.  You can try it out by
listening with `netcat`, like this:

    nc -vlp 5555 | xxd -c3 -g1

And then in another terminal go to the LaserShow directory and run python,
then:

    from comm import *

At this point a socket should be open that could spit things to `netcat`.
Now there could be multiple hosts defined in the header, if there are then
each will be connected to and evrey command will go to all of them.  The
actual socket is held open in another thread that reads from a queue.
that means that there is no practical way to know if a packet was sent (if
knowing this is useful I can change it so that each send waits for the ack,
but this'll throw off timming...).

If any of the connections fail, all will be close, the queue dummped and all
will then be re-connected to.



To see what peripherals are known use the function `plist()`, or just look at
the header.py file.

The numbers there are what you can use to refer to them.  Numbers 0 and 1 point
to the fast and slow XY respectively, and the rest are assumed to be stepper
motors that can only be pointed to a target (command).

So if you wanted to point stepper # 3 to target 0, do this:

    setTarget( 3, 0 )

There are functions for a few more examples and you can see the bytes send with
netcat, but they all call `rawSendCmd`. 
If you just want to send 3 bytes you can call `rawSendCmd()` like
this:

    rawSendCmd( 255, 0, 134 )

You should be able to build any functions you want off of this.


A More Complete Description of the Protocol
-------------------------------------------

Every command sent to the hardware is sent in 3 byte chunks.  Which means you
can always read 3 bytes (with a really really short timeout in case something
breaks while reading with a buffer clear) and then do the processing on those
three at a time.

The first byte is the peripheral id, the second is the command, and the third
is the argument to that command.

For peripheral ID~s, see `header.py`.  One ID designates the fast XY, another
the slow one, and the rest are different stepper motors.

Byte number 2 will be the dict key for one of the commands in `Commands`.  The
selected peripheral (the ID in byte number 1) has to accept this command.
Stepper motors take the `target` command (and the move arg ticks, and set tick
to index), the slow XY only `select glyph`
and `load glyph`, and the fast XY takes `select glyph`, `load glyph`, `rotate`,
and `shrink`.

Byte 3 is an argument to command. For target/index it's the index number (see
`header.py`), for rotate it's an angle [0,255], for shrink an amount, for
select glyph it's a memory slot number (in hardware), for load it's a slot
number (in hardware) to write the new glyph into.

The only deviation from the ( peripheral id, command, argument ) set is when a
`load glyph into slot` command is given, then the next `XYExpantPts`, a
constant in `header.py` (which is exactly how many points each and every glyph
has), are 3-bytes sets of XY+flag points.  There is no terminator, so the
read-socket timeout function should clear out the buffer.

Each point of a glyph is 3-bytes.  Byte 1 is the X, ranged [0,255], with 0 on
the right, 255 on the left.  Byte 2 is Y, ranged [0,255], with 0 on the bottom
and 255 on the top.  Byte 3 is either 0 or 1, 0 for normal, and 1 for blanked.




Pyglet
======

Pyglet is not used in the app, really, it is just used for the glyph creator
and the dummy-software-laser-emulator.






Comments from J
===============


A few more comments (now that I'm for the moment thinking about it).

You're thinking primarily about the drawing X-Y component, which is actually
something I'm more focused on for the next (post august) generation.  There is
a lot of X-Y-ness however:  Let do a rundown of the projector apparatuses.

There would be 2,3,4 projection units that each receive a command stream via
wifi and likey udp on their own unique IP addresses.  There are 2-3 laser
sources per projector, and for each laser, there is a choice of pre-programmed
positions along a single axis (stepper motor indices).  The number of target
positions in the past was 6, but this is pretty arbitrary.  They would point
the beam to one of n points along a frame on the ceiling (or in this case on
the pateo) that had mirrors mounted to it pointing to other mirrors pointing to
other mirrors or broken glass, etc.  Secondary or tertiary targets were often
first set as primary targets of other indices.  This creates a bright
changeable web of beams overhead where nobody can get their face in the path as
there's no scanning.  One of the stepper indices places the stepper mirror just
so that the beam misses it entirely and goes into a +-15 degree open loop X-Y
scanner.  This has no feedback, but is indeed indexed as you describe (in the
past it was an 8 bit dac, but this will likely be higher res this time).  This
scanner can only draw simple crude patterns and has a frequency response of
about 150 Hz.  It is mainly for shapes meant to be seen in 3D such as sheets,
triangles, often rotating slowly.  I would not want to send the live points in
the comm's stream.  There would be a buffer listing a sequence of points stored
in the projector's memory, and this could be (re) loaded at runtime so that the
PC can still generate new patterns or allow infinite pattern storage.  I would
just want to keep some kind of ram buffer of a few indexable patterns stored in
the projector's RAM.  This could be a structure that begins with a header
describing the update speed and the total number of points.  The update speed
would be bound to a range appropriate for a timer interrupt on the Arm.
Creating effects will require tuning, so being able to dynamically send over a
structure will be helpful.  As far as rotational animations, I was planning to
just do a linear xform in the projector (it is a 32 bit 50 MHz machine) with a
speed and direction, settable/updatable via commands sent to the projector.
The output of this X-Y scanner then is reflected off of a slow X-Y mirror
controlled by PWM model servos.  This final X-Y arrangement permits broad slow
sweeping of the X-Y effect around the room in a range much much wider than the
relatively narrow +-15 degree higher speed X-Y.  When you think about it, both
X-Y's can be modeled exactly the same way with the same structures for
patterns, but the PWM servos one is a couple of orders of magnitude lower
speed.

Blanking This is new, but some of my lasers' power supplies have it, but some
definitely don't.  Some lasers will have a brightness input as well.  The
timing and agility of these controls remains to be seen.
