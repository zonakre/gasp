"""
Something to raster using ArcGIS tools
"""

import arcpy


"""
TIN TO RASTER
"""

def tin_to_raster(tin, cs, out, template=None, snapRst=None):
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
    
    if snapRst:
        tempSnap = arcpy.env.snapRaster
        arcpy.env.snapRaster = snapRst
    
    arcpy.TinRaster_3d(
        tin, out, "FLOAT", "LINEAR", "CELLSIZE {}".format(str(cs)), "1"
    )
    
    if template:
        arcpy.env.extent = tempEnvironment0
    
    if snapRst:
        arcpy.env.snapRaster = tempSnap
    
    return out


