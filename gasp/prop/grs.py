"""
Manage MAPSET Region
"""


def rst_to_region(__raster):
    from grass.pygrass.modules import Module
    
    r = Module(
        "g.region", raster=__raster, run_=False, quiet=True
    )
    
    r()

