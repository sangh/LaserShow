#!/usr/bin/python

from header import *

sys.path.append("pyglet-1.1.4")
import pyglet

xpad = 15 # npix boarder
ypad = 100
PixPerCell = 3
SecPerTick = .1
SpotRadius = 1
DelayGlow = 4

window = pyglet.window.Window(
    width = 2*xpad + ( PixPerCell * XGridSize ),
    height= 2*ypad + ( PixPerCell * YGridSize ) )

# Print all the events
#window.push_handlers(pyglet.window.event.WindowEventLogger())

# We only want to calculate once.
gridDrawNpts = 0
gridDrawPts = ()
xmin = xpad
ymin = ypad
xmax = window.width - xpad
ymax = window.height - ypad
def line(x0,y0,x1,y1):
    global gridDrawNpts, gridDrawPts
    gridDrawPts = gridDrawPts + ( x0, y0, x1, y1 )
    gridDrawNpts = gridDrawNpts + 2
for x in range( xmin, xmax, 8*PixPerCell ):
    line( x, ymin, x, ymax )
line( xmax, ymin, xmax, ymax )
for y in range( ymin, ymax, 8*PixPerCell ):
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
    tx = xpad + PixPerCell // 2
    ty = ypad + PixPerCell // 2
    cx = x * PixPerCell + tx
    cy = y * PixPerCell + ty
    return ( cx, cy )
def pix2cell( px, py ):
    px = px - xpad
    if 0 > px: return None
    py = py - ypad
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

def calcLabel(px,py):
    cxy = pix2cell(px,py)
    if cxy is None:
        t = "At pixel (   ,   )."
    else:
        t = "At pixel (%3d,%3d)."%( cxy[0], cxy[1] )
    global label
    label = pyglet.text.Label(
        t,
        font_name='Times New Roman',
        font_size=18,
        x=xpad, y=window.height-xpad,
        anchor_x='left', anchor_y='top')
label = None
calcLabel(-1,-1)

labelGridSize = pyglet.text.Label(
    "Each grid square is 8 by 8 pixels.",
    font_name='Times New Roman',
    font_size=18,
    x=window.width-xpad, y=window.height-xpad,
    anchor_x='right', anchor_y='top')

labelLitBlanked = pyglet.text.Label(
    "Drag for lit line, click ends for blanked line.",
    font_name='Times New Roman',
    font_size=18,
    x=window.width//2, y=window.height-xpad-30,
    anchor_x='center', anchor_y='top')

# This is the glyph so far
g = []
def gDraw():
    lit = True
    lastCell = None
    for i in g:
        if "on" == i:
            lit = True
        elif "off" == i:
            lit = False
        else:
            if lastCell is None:
                lastCell = i
            else:
                if lit:
                    pyglet.gl.glColor4f( .5, .5, 1, .8 )
                else:
                    pyglet.gl.glColor4f( .5, .5, .5, .5 )
                x0,y0 = cell2pix(lastCell[0],lastCell[1])
                x1,y1 = cell2pix(i[0],i[1])
                pyglet.graphics.draw( 2, pyglet.gl.GL_LINES,
                    ( 'v2i', ( x0, y0, x1, y1 ) ) )
                lastCell = i

pressXY = None

@window.event
def on_mouse_press( px, py, button, modifiers ):
    tmp = pix2cell( px, py )
    if tmp is None:
        return
    x = tmp[0]
    y = tmp[1]
    global pressXY
    if pressXY is None:
        pressXY = ( x, y )
    elif pressXY[0] == x and pressXY[1] == y:
        return
    else:
        g.append( "off" )
        g.append( pressXY )
        g.append( (x,y), )
        pressXY = ( x, y )

@window.event
def on_mouse_release( px, py, button, modifiers ):
    tmp = pix2cell( px, py )
    if tmp is None:
        return
    x = tmp[0]
    y = tmp[1]
    global pressXY
    if pressXY is None:
        return
    elif pressXY[0] == x and pressXY[1] == y:
        return
    else:
        g.append( "on" )
        g.append( pressXY )
        g.append( (x,y), )
        pressXY = ( x, y )
        

@window.event
def on_mouse_motion(x, y, dx, dy):
    calcLabel(x,y)
    ret = pix2cell(x,y)
    if ret is not None:
        spotsGrid[ ret[0] ][ ret[1] ] = 1.0

@window.event
def on_mouse_drag( x, y, dx, dy, buttons, modifiers ):
    calcLabel(x,y)

@window.event
def on_draw():
    window.clear()
    label.draw()
    labelGridSize.draw()
    labelLitBlanked.draw()
    gridDraw()
    allSpotsDraw(0)
    gDraw()
    print len(g)

@window.event
def on_mouse_enter( x, y ):
    pass

@window.event
def on_mouse_leave( x, y ):
    global pressXY
    calcLabel(-1,-1)
    pressXY = None



pyglet.app.run()
