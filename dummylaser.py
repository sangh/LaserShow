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

# We only want to calculate once.
gridDrawNpts = 0
gridDrawPts = ()
xmin = pad
ymin = pad
xmax = window.width - pad
ymax = window.height - pad
def line(x0,y0,x1,y1):
    global gridDrawNpts, gridDrawPts
    gridDrawPts = gridDrawPts + ( x0, y0, x1, y1 )
    gridDrawNpts = gridDrawNpts + 2
for x in range( xmin, xmax, PixPerCell ):
    line( x, ymin, x, ymax )
line( xmax, ymin, xmax, ymax )
for y in range( ymin, ymax, PixPerCell ):
    line( xmin, y, xmax, y )
line( xmin, ymax, xmax, ymax )
del line, xmin, ymin, xmax, ymax
def gridDraw():
    global gridDrawNpts, gridDrawPts
    pyglet.gl.glColor4f( .3, .3, .3, .3 )
    pyglet.graphics.draw( gridDrawNpts, pyglet.gl.GL_LINES,
        ( 'v2i', gridDrawPts ) )

# Take in a cell:
#   (x,y) such that 0 <= x < XGridSize, 0 <= y < YGridSize
# return a pixel coordinate of the center of the cell.
def cell2pix( x, y ):
    t = pad + PixPerCell // 2
    cx = x * PixPerCell + t
    cy = y * PixPerCell + t
    return ( cx, cy )
def pix2cell( px, py ):
    px = px - pad
    if 0 > px: return None
    py = py - pad
    if 0 > py: return None
    x = int( float(px) / PixPerCell )
    if x >= XGridSize: return None
    y = int( float(py) / PixPerCell )
    if y >= YGridSize: return None
    return ( x, y )
def spotDraw( x, y, i ):
    x, y = cell2pix( x, y )
    # Draw middle
    pyglet.gl.glColor4f( i, i, i, i )
    pyglet.graphics.draw( 1, pyglet.gl.GL_POINTS,
        ('v2i', ( x, y ) ) )
    # SpotRadius * PixPerCell is pixle radius
    npr = int( SpotRadius * PixPerCell )
    fracDec = float(i)/npr
    for j in range(1, npr+1,1):
        pts = []
        i = i - fracDec

        for xt,yt in ((x+j, y),(x-j,y),(x+j,y+j),(x-j,y-j),(x-j,y+j),(x+j,y-j),(x,y+j),(x,y-j)):
            pts.append( xt )
            pts.append( yt )

        pyglet.gl.glColor4f( i, i, i, i )
        pyglet.graphics.draw( 8, pyglet.gl.GL_POINTS,
            ('v2i', pts ) )



spotsGrid = []
for x in range(XGridSize):
    tmp = []
    for y in range(YGridSize):
        tmp.append(0)
    spotsGrid.append(tmp)

def allSpotsDraw(dt):
    global spotsGrid
    for x in range(XGridSize):
        for y in range(YGridSize):
            if 0 < spotsGrid[x][y]:
                spotDraw( x, y, spotsGrid[x][y] )
                spotsGrid[x][y] = spotsGrid[x][y] - ( dt / SecPerTick / DelayGlow )

pyglet.clock.schedule_interval(allSpotsDraw, SecPerTick)

@window.event
def on_mouse_motion(x, y, dx, dy):
    ret = pix2cell(x,y)
    if ret is not None:
        spotsGrid[ ret[0] ][ ret[1] ] = 1.0

@window.event
def on_draw():
    #window.clear()
    #label.draw()
    gridDraw()
    allSpotsDraw(0)



pyglet.app.run()
