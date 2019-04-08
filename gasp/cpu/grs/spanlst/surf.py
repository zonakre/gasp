"""
Raster tools - GRASS GIS

GRASS GIS Tools translated to Python
"""

from grass.pygrass.modules import Module


def viewshed(dem, obsPnt, outRst):
    """
    Compute viewshed
    """
    
    vshd = Module(
        "r.viewshed", input=dem, output=outRst, coordinates="east,north",
        flags="b", overwrite=True, run_=False, quiet=True
    )
    
    vshd()
    
    return outRst

