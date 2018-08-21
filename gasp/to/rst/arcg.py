"""
Something to raster using ArcGIS tools
"""

import arcpy


"""
Feature Class to Raster
"""

def shp_to_raster(inShp, inField, outRst, CellSize, template=None, snap=None):
    if template:
        tempEnvironment0 = arcpy.env.extent
        arcpy.env.extent = template
    
    if snap:
        tempSnap = arcpy.env.snapRaster
        arcpy.env.snapRaster = snap
    
    obj_describe = arcpy.Describe(inShp)
    geom = obj_describe.ShapeType
    
    if geom == u'Polygon':
        arcpy.PolygonToRaster_conversion(
            inShp, inField, outRst, "CELL_CENTER", "NONE", CellSize
        )
    elif geom == u'Polyline':
        arcpy.PolylineToRaster_conversion(
            inShp, inField, outRst, "MAXIMUM_LENGTH", "NONE", CellSize
        )
    
    if template:
        arcpy.env.extent = tempEnvironment0
    
    if snap:
        arcpy.env.snapRaster = tempSnap
    
    return outRst


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


