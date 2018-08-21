"""
Raster tools - GRASS GIS

GRASS GIS Tools translated to Python
"""


def grow_distance(inRst, outRst, ascmd=None):
    """
    Generates a raster map containing distance to nearest raster features
    """
    
    if not ascmd:
        from grass.pygrass.modules import Module
    
        m = Module(
            'r.grow.distance', input=inRst, distance=outRst, metric='euclidean',
            overwrite=True, quiet=True, run_=False
        )
    
        m()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "r.grow.distance input={} distance={} metric=euclidean "
            "--overwrite --quiet"
        ).format(inRst, outRst))
    
    return outRst

