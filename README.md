Overview of the LaserShow Software Interface
============================================

This interface is for a single laser at J&J's party in Aug.



Header
------

These are the hard-coded things that _every_ class sees.



The ``comm'' or Communications Interface
----------------------------------------

This class takes care of talking to the hardware.  You can try it out by
listening with netcat, like this:

    nc -vlp 555 | xxd -c3 -g1

And then in another terminal go to the LaserShow directory and run python,
then:

    from comm import *

At this point a socket should be open that could spit things to netcat.
To see what peripherals are known use the function plist:

    plist()

The numbers there are what you can use to refer to them.  Numbers 0 and 1
point to the fast and slow XY respectivly, and the rest are assumed to be
stepper motors that can only be pointed to a target (command).

So if you wanted to point stepper # 3 to target 0, do this:

    setTarget( 3, 0 )

There are functions (stubs) for the rest and you can see the bytes send with netcat.



Pyglet
======

Pyglet is not used in the app, really, it is just used for the glyph creator and the dummy-software-laser-emulator.






Comments from J
===============


A few more comments (now that I'm for the moment thinking about it).

You're thinking primarily about the drawing X-Y component, which is 
actually something I'm more focused on for the next (post august) 
generation.  There is a lot of X-Y-ness however:  Let do a rundown of 
the projector apparatuses.

There would be 2,3,4 projection units that each receive a command stream 
via wifi and likey udp on their own unique IP addresses.  There are 2-3 
laser sources per projector, and for each laser, there is a choice of 
pre-programmed positions along a single axis (stepper motor indices).  
The number of target positions in the past was 6, but this is pretty 
arbitrary.  They would point the beam to one of n points along a frame 
on the ceiling (or in this case on the pateo) that had mirrors mounted 
to it pointing to other mirrors pointing to other mirrors or broken 
glass, etc.  Secondary or tertiary targets were often first set as 
primary targets of other indices.  This creates a bright changeable web 
of beams overhead where nobody can get their face in the path as there's 
no scanning.  One of the stepper indices places the stepper mirror just 
so that the beam misses it entirely and goes into a +-15 degree open 
loop X-Y scanner.  This has no feedback, but is indeed indexed as you 
describe (in the past it was an 8 bit dac, but this will likely be 
higher res this time).  This scanner can only draw simple crude patterns 
and has a frequency response of about 150 Hz.  It is mainly for shapes 
meant to be seen in 3D such as sheets, triangles, often rotating 
slowly.  I would not want to send the live points in the comm's stream.  
There would be a buffer listing a sequence of points stored in the 
projector's memory, and this could be (re) loaded at runtime so that the 
PC can still generate new patterns or allow infinite pattern storage.  I 
would just want to keep some kind of ram buffer of a few indexable 
patterns stored in the projector's RAM.  This could be a structure that 
begins with a header describing the update speed and the total number of 
points.  The update speed would be bound to a range appropriate for a 
timer interrupt on the Arm.  Creating effects will require tuning, so 
being able to dynamically send over a structure will be helpful.  As far 
as rotational animations, I was planning to just do a linear xform in 
the projector (it is a 32 bit 50 MHz machine) with a speed and 
direction, settable/updatable via commands sent to the projector.  The 
output of this X-Y scanner then is reflected off of a slow X-Y mirror 
controlled by PWM model servos.  This final X-Y arrangement permits 
broad slow sweeping of the X-Y effect around the room in a range much 
much wider than the relatively narrow +-15 degree higher speed X-Y.  
When you think about it, both X-Y's can be modeled exactly the same way 
with the same structures for patterns, but the PWM servos one is a 
couple of orders of magnitude lower speed.

Blanking
This is new, but some of my lasers' power supplies have it, but some 
definitely don't.  Some lasers will have a brightness input as well.  
The timing and agility of these controls remains to be seen.
