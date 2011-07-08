#!/usr/bin/python

from header import *

sys.path.append("pyglet-1.1.4")
import pyglet

pad = 15 # npix boarder

window = pyglet.window.Window(
    width = 2*pad + ( PixPerCell * XGridSize ),
    height= 2*pad + ( PixPerCell * YGridSize ) )

# Print all the events
window.push_handlers(pyglet.window.event.WindowEventLogger())

label = pyglet.text.Label('Hello, world',
    font_name='Times New Roman',
    font_size=36,
    x=window.width//2, y=window.height//2,
    anchor_x='center', anchor_y='center')

def gridDraw():
    xmin = pad
    ymin = pad
    xmax = window.width - pad
    ymax = window.height - pad
    pyglet.gl.glColor4f( .3, .3, .3, .3 )
    def line(x0,y0,x1,y1):
        pyglet.graphics.draw( 2, pyglet.gl.GL_LINES,
            ('v2i', ( x0, y0, x1, y1 ) ) )
    for x in range( xmin, xmax, PixPerCell ):
        line( x, ymin, x, ymax )
    line( xmax, ymin, xmax, ymax )
    for y in range( ymin, ymax, PixPerCell ):
        line( xmin, y, xmax, y )
    line( xmin, ymax, xmax, ymax )

# Take in a cell:
#   (x,y) such that 0 <= x < XGridSize, 0 <= y < YGridSize
# return a pixel coordinate of the center of the cell.
def cell2pix(x,y):
    return (x*PixPerCell + (PixPerCell//2)) , (y*PixPerCell + (PixPerCell//2))

def spotDraw():
    x,y=5,7 # Random spot
    pyglet.graphics.draw( 1, pyglet.gl.GL_POINTS,
        ('v2i', cell2pix(x,y) ) )













@window.event
def on_draw():
    window.clear()
    label.draw()
    gridDraw()
    spotDraw()
    
pyglet.app.run()
