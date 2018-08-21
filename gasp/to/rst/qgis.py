"""
To Raster
"""

import processing

def vector_to_raster(vec, rst):
    """
    Feature Class to Raster
    """
    
    processing.runalg(
        "gdalogr:rasterize", vec, "ID", 1, 10, 10, 1,
        "-9999", 4, None, 6, 1, False, 0, True, rst
    )
    
    return rst