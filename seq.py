
import json
from header import *
from glyph import *

def seqIsValid( s ):
    try:
        gl = glyphList()
        if not isinstance( s[0], str ) or "" == s[0]:
            return False
        lastTime = 0.0
        for t in s[1:]:
            if 3 == len(t):
                if not isinstance( t[2], str ) or "" == t[2]:
                    return False
            elif 2 != len(t):
                return False
            # So len(t) == 2
            ti = float(t[0]) # will throw if not float
            if ti < lastTime:
                return False
            lastTime = ti
            if not isinstance( t[1], tuple ):
                return False
            if 3 != len(t[1]):
                return False
            for i in (0,1,2):
                if not isinstance( t[1][i], int ):
                    return False
                chr(t[1][i]) # betewwn 0 and 255
        return True
    except Exception:
        return False

def seqDump( s ):
    if not seqIsValid( s ):
        raise NameError("Seq is not valid, not storing.")
    fileName = os.path.join("seqs", s[0] + ".json")
    if( os.path.exists( fileName ) ):
        raise NameError("It appears that this seq exists, not storing.")
    f = open( fileName, "w" )
    json.dump(s[1:], f)
    f.close()

def seqLoad( name ):
    fileName = os.path.join("seqs", str(name) + ".json")
    if( not os.path.exists( fileName ) ):
        raise NameError("Seq \"%s\" not found."%(str(name)))
    f = open( fileName, "r" )
    su = json.load(f)
    f.close()
    # Now convert to ascii (from json's unicode).
    # And make everything inside tuples
    for i in range(len(su)):
        if 3 == len(su[i]):
            su[i][2] = su[i][2].encode('ascii')
        su[i][1] = tuple( su[i][1] )
        su[i] = tuple( su[i] )
    su = [ name, ] + su
    if seqIsValid( su ):
        return su
    else:
        raise NameError("Seq \"%s\" is not valid."%(str(name)))

def seqList():
    "Return a list of sequences saved already."
    ls = sorted(os.listdir("seqs"))
    ret = []
    for l in ls:
        if ".json" != l[-5:]:
            wrn("%s is not named correctly."%(l))
        else:
            ret.append( l[:-5] )
    return ret
