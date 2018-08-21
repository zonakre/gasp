"""
Manage MAPSET Region
"""

from grass.pygrass.modules import Module


def rst_to_region(__raster):
    r = Module(
        "g.region", raster=__raster, run_=False, quiet=True
    )
    
    r()

