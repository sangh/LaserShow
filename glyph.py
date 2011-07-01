import json
from header import *

# This used to be a class, but I want to use json w/o all the
# manual mangling needed, so it's just going to be a dictionary.
# It must have all the consts (for type checking) and keys for
# the 'name' and a 'path' (list of (x,y) points or "on"/"off" cmds).

def pointIsValid( pt ):
    if "on" == pt  or  "off" == pt:
        return True
    if (    pt[0] < 0
        or  pt[0] >= consts['XGridSize']
        or  pt[1] < 0
        or  pt[1] >= consts['YGridSize']
        ):
        return False
    return True

def pathIsValid( path ):
    try:
        for pt in path:
            if not pointIsValid( pt ):
                return False
    except:
        return False
    return True

def glyphIsValid( g ):
    if not doAllConstsMatch( g ):
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
    return g

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
    for k in consts:
        d[k] = consts[k]
    return d
