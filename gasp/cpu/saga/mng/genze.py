"""
SAGA GIS Analysis Tools
"""

from gasp import exec_cmd

def dissolve(inShp, field, outShp):
    """
    Dissolve vectorial data by field
    
    This algorithm doesn't allow self intersections
    """
    
    cmd = (
        'saga_cmd shapes_polygons 5 -POLYGONS {in_poly} -FIELDS {fld} '
        '-DISSOLVED {out_shp}'
    ).format(
        in_poly=inShp, fld=field, out_shp=outShp
    )
    
    outcmd = exec_cmd(cmd)
    
    return outShp


def dissolve_lines(inLines, field, outLines):
    """
    Dissolve Lines using SAGA GIS
    """
    
    cmd = (
        'saga_cmd shapes_lines 5 -LINES {} -FIELD_1 {} -DISSOLVED {} '
        '-ALL 0'
    ).format(inLines, field, outLines)
    
    outcmd = exec_cmd(cmd)
    
    return outLines

