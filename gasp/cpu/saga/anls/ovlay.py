"""
SAGA GIS Topology Tools
"""


from gasp import exec_cmd


def intersection(lyrA, lyrB, out):
    """
    Calculates the geometric intersection of the overlayed polygon layers,
    i.e. layer A and layer B.
    """
    
    cmdout = exec_cmd((
        "saga_cmd shapes_polygons 14 -A {} -B {} -RESULT {} -SPLIT 1"
    ).format(lyrA, lyrB, out))
    
    return out


def erase(inShp, eraseFeatures, outShp, splitMultiPart=None):
    """
    Difference between two feature classes
    
    It appears to be very slow
    """
    
    cmd = (
        'saga_cmd shapes_polygons 15 -A {in_shp} -B {erase_shp} '
        '-RESULT {output} -SPLIT {sp}'
    ).format(
        in_shp=inShp, erase_shp=eraseFeatures,
        output=outShp,
        sp='0' if not splitMultiPart else '1'
    )
    
    outcmd = exec_cmd(cmd)
    
    return outShp


def self_intersection(polygons, output):
    """
    Create a result with the self intersections
    """
    
    cmd = (
        'saga_cmd shapes_polygons 12 -POLYGONS {in_poly} -INTERSECT '
        '{out}'
    ).format(in_poly=polygons, out=output)
    
    outcmd = exec_cmd(cmd)
    
    return output


def snap_points_to_lines(points, lines, result, movesShp=None):
    """
    Snap Points to Lines
    """
    
    cmd = (
        "saga_cmd shapes_points 19 -INPUT {pnt} -SNAP {lnh} "
        "-OUTPUT {out}{mv}"
    ).format(
        pnt=points, lnh=lines, out=result,
        mv="" if not movesShp else " -MOVES {}".format(movesShp)
    )
    
    outcmd = exec_cmd(cmd)
    
    return result

