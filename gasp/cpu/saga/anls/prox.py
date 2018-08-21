"""
SAGA GIS Proximity Tools
"""

from gasp import exec_cmd

def _buffer(inShp, dist, out, distIsField=None, dissolve=None):
    """
    A vector based buffer construction partly based on the method supposed by
    Dong et al. 2003. 
    """
    
    c = (
        "saga_cmd shapes_tools 18 -SHAPES {_in} "
        "-BUFFER {_out} {distOption} {d} -DISSOLVE {diss}"
    ).format(
        _in=inShp,
        distOption = "-DIST_FIELD_DEFAULT" if not distIsField else \
            "-DIST_FIELD",
        d=str(dist),
        _out=out,
        diss="0" if not dissolve else "1"
    )
    
    outcmd = exec_cmd(c)
    
    return out


def pnts_dist(inShp, nearShp, outTbl, maxDist=None):
    """
    Computes distances between pairs of points.
    """
    
    c = (
        "saga_cmd shapes_points 3 -POINTS {} -NEAR {} -DISTANCES {} "
        "-FORMAT 1{}"
    ).format(
        inShp, nearShp, outTbl,
        "" if not maxDist else " -MAX_DIST {}".format(maxDist)
    )
    
    outcmd = exec_cmd(c)
    
    return outTbl

