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
