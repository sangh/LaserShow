Overview of the LaserShow Software Interface
============================================

This interface is for a single laser at J&J's party in Aug.  I'm assuming that a laser can point to a single spot on a 2-D grid at any one time and can be turned on or off at each of those points; **if this assumption is wrong, stop right now and email/call me.**

This isn't a control thing, it's just a set of things that will let one create shapes or frames and transforms (rotation/re-size,etc) and defines an interface for it along with a testing visualisation playground.  The question to you is, ``is it useful for me to write this?''.

The next few sections walk through each of the interfaces proposals starting from the laser class up to the drawing tools.

**I haven't written any code yet, this is me trying to start a discussion of what this should look like.**


Header
------

These are the hard-coded things that _every_ class sees.  Included are:

  * (XGridSize,YGridSize): The grid size, which is a 2-D array with indexes < these values.  I'm thinking the grid will be quadrant one of a Cartesian Plane (the position (0,0) is the bottom-left).
  * DelayMove: The amount of time needed for each position change (not quite sure how to keep track of time yet)
  * DelayOff, DelayOn: The amount of time needd to turn on or off the laser
  * DelayGlow: Amount of time a spot stays lit after the laser moves off it.


Laser Class
-----------

This class models a laser which I expect will be sub-classed with something that actually talks to a real device.  In this implementation I'll just use Pyglet to get a 2-D window that is the grid size and then take in commands to position and turn on of off.

The interface is really simple, it is just:

    laser.move(x,y)
    laser.on()
    laser.off()

It expects that commands be sent approximately every DelayMove, otherwise the window will be blanked in DelayGlow time.  This set up means that the transfer mechanism be relatively robust, and the electronics them-selves pretty stupid, but really reliable, and the smartness is all in software.


Glyph class
-----------

This class defines a list of positions and on off settings that draw a shape or letters or something.  The idea is that this should take up the whole field (it can be made smaller later, making it larger is harder), and be static; that is if it is re-drawn over and over again relatively quickly then it looks like it is not moving (of course since there is a sequence associated with it, this isn't necessary).

I expect to make a Pyglet drawing surface that one can use to easily draw (with the mouse) a glyph they want.


Transform class
---------------

These class is a wrapper (kind of) for a Glyph.  It basically does some sort of transform on it and returns a new shape.  Transforms are things like make it 5% smaller, or rotate it pi/2 rad, or turn it upside down.  Generally the output should also look static (even though it's not) like a glyph.


Sequence class
--------------

This class will take some Transforms (or Glyphs) and send them to the Laser.  The simplest would be to just send the Glyph over and over, but the point is to send more complicated things like:

    x = 0
    while(True):
        <pseudo-code>:
            send transformRotateBy x, glyph
        x = x + .1 * pi
        x = x % (2 * pi)


Future Notes
============

In the end I see this being used by using the graphical glyph creator, and then writing/using some sequences on the glyphs/transforms, looking at the output by using the Pyglet laser class, then hooking up the program to the real laser class and seeing what it looks like.




Pyglet
======

Pyglet is not used in the app, really, it is just used for the glyph creator and the dummy-software-laser-emulator.

The symlink just points to the checked in version dir, which can change, see the header file.





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
