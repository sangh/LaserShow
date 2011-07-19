
from header import *

import json
import math

# This used to be a class, but I want to use json w/o all the
# manual mangling needed, so it's just going to be a dictionary.
# It must have X and Y grid points and keys for
# the 'name' and a 'path' (list of (x,y) points or "on"/"off" cmds).

def pointIsValid( pt ):
    try:
        if "on" == pt  or  "off" == pt:
            return True
        if (    pt[0] < 0
            or  pt[0] >= XGridSize
            or  pt[1] < 0
            or  pt[1] >= YGridSize
            ):
            return False
        return True
    except:
        return False

def pathIsValid( path ):
    try:
        for pt in path:
            if not pointIsValid( pt ):
                return False
        return True
    except:
        return False

def glyphIsValid( g ):
    if not XGridSize == g['XGridSize']:
        return False
    if not YGridSize == g['YGridSize']:
        return False
    if 'name' not in g:
        wrn("Glyph does not have a name.")
        return False
    if 'path' not in g:
        wrn("Glyph \"%s\" does not have a path."%(str(g['name'])))
        return False
    if not pathIsValid( g['path'] ):
        wrn("Path malformed in \"%s\"."%(str(g['name'])))
        return False
    return True

def glyphDump( g ):
    if not glyphIsValid( g ):
        wrn("Glyph is not valid, not storing.")
        return
    fileName = os.path.join("glyphs", str(g['name']) + ".json")
    if( os.path.exists( fileName ) ):
        wrn("It appears that this glyph exists, not storing.")
        return
    f = open( fileName, "w" )
    json.dump(g, f)
    f.close()

def glyphLoad( name ):
    fileName = os.path.join("glyphs", str(name) + ".json")
    if( not os.path.exists( fileName ) ):
        raise NameError("Glyph \"%s\" not found."%(str(name)))
    f = open( fileName, "r" )
    gu = json.load(f)
    f.close()
    # Now convert to ascii (from json's unicode).
    # Will break if there are other things in here.
    g = {}
    for k in gu:
        v = gu[k]
        if isinstance( v, unicode ):
            v = v.encode('ascii')
        g[k.encode('ascii')] = v
    # Above will encode the value of 'name'.
    p = []
    for pt in g['path']:
        if isinstance( pt, unicode ):
            p.append( pt.encode('ascii') )
        else:
            p.append( pt )
    g['path'] = p
    if glyphIsValid( g ):
        return g
    else:
        raise NameError("Glyph \"%s\" is not valid."%(str(name)))

def glyphCreate( name, path ):
    if not pathIsValid( path ):
        raise SyntaxError("Path is invalid.")
    newpath = []
    for v in path:
        if isinstance( v, list ):
            newpath.append( tuple( v ) )
        elif isinstance( v, unicode ):
            newpath.append( v.encode('ascii') )
        else:
            newpath.append( v )
    d = { 'name': str(name), 'path': newpath }
    d['XGridSize'] = XGridSize
    d['YGridSize'] = YGridSize
    return d

def distanceEuclidean( lpt, pt ):
    if lpt is None:
        return 0.0
    else:
        y = float( pt[0] - lpt[0] )
        x = float( pt[1] - lpt[1] )
        return math.sqrt( ( x * x ) + ( y * y ) )

def interpolateEvenSpacedPtsOnALine( nPts, pt1, pt2 ):
    "Return a list of nPts between pt1 and pt2 not inc. pt1 but inc. pt2."
    "So pt2 is always the last pt in the list, and the list is nPts long."
    expath = []
    xOffset = float( pt2[0] - pt1[0] ) / nPts
    yOffset = float( pt2[1] - pt1[1] ) / nPts
    for i in range( 1, nPts ):
        newX = int(( i * xOffset + pt1[0] ) // 1 )
        newY = int(( i * yOffset + pt1[1] ) // 1 )
        expath.append( ( newX, newY ) )
    expath.append( pt2 )
    return expath


def glyphExpandToPts( nPoints, glyph ):
    "Return the glyph expanded to nPoints triplets."
    # The general alg is to count the total path lenght, and then divede
    # by the segment lengths.  We want the glyph to be as sharp as possible
    # so for now we only expand the lit parts.
    lenTot = 0.0
    lit = True
    lpt = None
    dummyPts = 0 # Pts that're off or duped.
    # Calc total (lit) path lenght.
    # We don't use the sqrt b/c it's computationally expensive and
    # we don't cars about the number, only the ratios of the paths.
    for pt in glyph['path']:
        if "on" == pt:
            lit = True
        elif "off" == pt:
            lit = False
        else:
            if( lit ):
                d = distanceEuclidean( lpt, pt )
                if 0.0 == d:
                    dummyPts = dummyPts + 1
                lenTot = lenTot + d
            else:
                dummyPts = dummyPts + 1
            lpt = pt
    # Now we iterate again adding points to the lit parts.
    expandToPts = nPoints - dummyPts
    if len(filter(lambda p:not isinstance(p,str),glyph['path']))>=expandToPts:
        raise SyntaxError("nPoints bigger than point-points in path?!?")
    def ptToTriplet( lit, pt ):
        if lit: blanked = 0
        else:   blanked = 1
        return ( pt[0], pt[1], blanked )
    expath = []  # This has the triplets.
    lit = True
    lpt = None
    for pt in glyph['path']:
        if "on" == pt:
            lit = True
        elif "off" == pt:
            lit = False
        else:
            if( ( lpt is None )  or  ( not lit ) ):
                expath.append( ptToTriplet( lit, pt ) )
            else:
                dist = distanceEuclidean( lpt, pt )
                nPtsToAdd = int(( expandToPts * dist / lenTot ) // 1 )
                if( 0 < nPtsToAdd ):
                    interPts = interpolateEvenSpacedPtsOnALine( nPtsToAdd, lpt, pt )
                    expath = expath + map(lambda p: ptToTriplet( lit, p ), interPts )
                else:
                    expath.append( ptToTriplet( lit, pt ) )
            lpt = pt
    # We add pts if the flooring interpalate did not add enough
    # rather than spread them out we just repeat the last point.
    le = len(expath)
    if( le > nPoints ):
        wrn("Truncated %d from glyph, the glyphExpandToPts fn is broken."%(le-nPoints))
        return expath[0:nPoints]
    elif( le < nPoints ):
        return expath + (nPoints-le) * [expath[-1]]
    else:
        return expath
