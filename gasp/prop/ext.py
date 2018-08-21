# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Deal with data extent
"""

def rst_ext(rst, gisApi='gdal'):
    """
    Return a array with the extent of one raster dataset
    
    array order = Xmin (left), XMax (right), YMin (bottom), YMax (top)
    
    API'S Available:
    * gdal;
    * arcpy;
    * arcpy2;
    """
    
    if gisApi == 'gdal':
        from osgeo import gdal
        
        img = gdal.Open(rst)
        
        lnhs = int(img.RasterYSize)
        cols = int(img.RasterXSize)
        
        left, cellx, z, top, c, celly = img.GetGeoTransform()
        
        right  = left + (cols * cellx)
        bottom = top  - (lnhs * abs(celly))
        
        extent = [left, right, bottom, top]
    
    elif gisApi == 'arcpy':
        import arcpy
        
        extent = ["LEFT", "RIGHT", "BOTTOM", "TOP"]
        
        for i in range(len(extent)):
            v = arcpy.GetRasterProperties_management(
                rst, extent[i]
            )
            
            extent[i] = float(str(v).replace(',', '.'))
    
    elif gisApi == 'arcpy2':
        import arcpy
        
        describe = arcpy.Describe(rst)
        
        extent = [
            describe.extent.XMin, describe.extent.XMax,
            describe.extent.YMin, describe.extent.YMax
        ]
    
    else:
        raise ValueError('The api {} is not available'.format(gisApi))
    
    return extent


"""
Extent of Shapefiles and such
"""

def get_extent(shp, gisApi='ogr'):
    """
    Return extent of a Vectorial file
    
    Return a tuple object with the follow order:
    (left, right, bottom, top)
    
    API'S Available:
    * ogr;
    * arcpy;
    """
    
    if gisApi == 'ogr':
        from osgeo        import ogr
        from gasp.prop.ff import drv_name
        from decimal      import Decimal
    
        dt = ogr.GetDriverByName(drv_name(shp)).Open(shp, 0)
        lyr = dt.GetLayer()
        extent = lyr.GetExtent()
    
        dt.Destroy()
        
        EXT = [Decimal(x) for x in extent]
    
    elif gisApi == 'arcpy':
        import arcpy
        
        descObj = arcpy.Describe(shp)
        
        EXT = [
            descObj.extent.XMin, descObj.extent.XMax,
            descObj.extent.YMin, descObj.extent.YMax
        ]
    
    else:
        raise ValueError('The api {} is not available'.format(gisApi))
    
    return EXT

