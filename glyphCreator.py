#!/usr/bin/python

from header import *
from glyph import *
sys.path.append("pyglet-hg")
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
gridNums = []
def gridNumbers( x, y, num ):
    gridNums.append( pyglet.text.Label(
        str(num),
        color=4*(155,),
        font_name='Times New Roman',
        font_size=9,
        x=x, y=y,
        anchor_x='center', anchor_y='center')
    )
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
    gridNumbers( x, ymin-6, (x-xmin)/PixPerCell )
line( xmax, ymin, xmax, ymax )
for y in range( ymin, ymax, 8*PixPerCell ):
    line( xmin, y, xmax, y )
    gridNumbers( xmin-6, y, (y-ymin)/PixPerCell )
line( xmin, ymax, xmax, ymax )
del line, xmin, ymin, xmax, ymax, gridNumbers
def gridDraw():
    global gridDrawNpts, gridDrawPts, gridNums
    pyglet.gl.glColor4f( .3, .3, .3, .3 )
    pyglet.graphics.draw( gridDrawNpts, pyglet.gl.GL_LINES,
        ( 'v2i', gridDrawPts ) )
    for n in gridNums:
        n.draw()

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

labelSaving = pyglet.text.Label(
    "Close window to enter name and save the glyph (or not).",
    font_name='Times New Roman',
    font_size=18,
    x=window.width//2, y=xpad,
    anchor_x='center', anchor_y='bottom')

def lineDraw( color, c0, c1 ):
    pyglet.gl.glColor4f( *color )
    pyglet.graphics.draw( 2, pyglet.gl.GL_LINES,
        ( 'v2i', cell2pix( *c0 ) + cell2pix( *c1 ) ) )
def litLineDraw( c0, c1 ):
    lineDraw( ( 1, 0, 1, 1 ), c0, c1 )
def blankedLineDraw( c0, c1 ):
    lineDraw( ( .5, .5, .5, .4 ), c0, c1 )

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
                    litLineDraw( lastCell, i )
                else:
                    blankedLineDraw( lastCell, i )
                lastCell = i

pressXY = None
motionLine = None
dragLine = None

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
    global motionLine
    global dragLine
    dragLine = None
    calcLabel(x,y)
    try:
        cx, cy = pix2cell( x, y ) # on sep line for TypeError checking
        motionLine = (g[-1], ( cx, cy ))
    except (IndexError, TypeError):
        motionLine = None

@window.event
def on_mouse_drag( x, y, dx, dy, buttons, modifiers ):
    global dragLine
    global motionLine
    motionLine = None
    calcLabel(x,y)
    try:
        cx, cy = pix2cell( x, y ) # on sep line for TypeError checking
        dragLine = (g[-1], ( cx, cy ))
    except (IndexError, TypeError):
        dragLine = None

@window.event
def on_draw():
    window.clear()
    label.draw()
    labelGridSize.draw()
    labelLitBlanked.draw()
    labelSaving.draw()
    gridDraw()
    #allSpotsDraw(0)
    gDraw()
    if motionLine is not None:
        blankedLineDraw( *motionLine )
    if dragLine is not None:
        litLineDraw( *dragLine )

@window.event
def on_mouse_enter( x, y ):
    pass

@window.event
def on_mouse_leave( x, y ):
    global pressXY
    calcLabel(-1,-1)
    pressXY = None
    dragLine = None
    motionLine = None



#pyglet.clock.schedule_interval(allSpotsDraw, SecPerTick)
pyglet.app.run()

try:
    import readline
    i = raw_input("Enter a name to save the glyph (leave blank to abandon): ")
    if "" == i:
        i = None
except EOFError:
    i = None
if i is not None:
    gs = glyphCreate( str(i), g )
    glyphDump( gs )
    wrn("Saved glyph \"%s\"."%(gs['name']))
else:
    wrn("Not saving.")
