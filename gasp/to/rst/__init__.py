# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
To raster tools
"""


"""
Array to Raster
"""

def array_to_raster(inArray, outRst, template, epsg, data_type, noData=None,
                    gisApi='gdal'):
    """
    Send Array to Raster
    
    API Available:
    * gdal;
    * arcpy
    """
    
    if gisApi == 'gdal':
        from osgeo        import gdal, osr
        from gasp.prop.ff import drv_name
    
        img_template  = gdal.Open(template)
        geo_transform = img_template.GetGeoTransform()
        rows, cols    = inArray.shape
        driver        = gdal.GetDriverByName(drv_name(outRst))
        out           = driver.Create(outRst, cols, rows, 1, data_type)
        out.SetGeoTransform(geo_transform)
        outBand       = out.GetRasterBand(1)
    
        if noData:
            outBand.SetNoDataValue(noData)
        
        outBand.WriteArray(inArray)
    
        if epsg:
            from gasp.cpu.gdl.mng.prj import epsg_to_wkt
            srs = epsg_to_wkt(epsg)
            out.SetProjection(srs)
    
        outBand.FlushCache()
    
    elif gisApi == 'arcpy':
        import arcpy
        
        xmin  = arcpy.GetRasterProperties_management(template, "LEFT")
        cellx = arcpy.GetRasterProperties_management(template, "CELLSIZEX")
        celly = arcpy.GetRasterProperties_management(template, "CELLSIZEY")
        
        new_rst = arcpy.NumPyArrayToRaster(
            array, float(str(xmin).replace(',', '.')),
            float(str(cellx).replace(",", ".")),
            float(str(celly).replace(",", "."))
        )
        
        new_rst.save(outRst)
    
    else:
        raise ValueError('The api {} is not available'.format(gisApi))
    
    return outRst


"""
Raster to Raster tools
"""

def composite_bnds(rsts, outRst, epsg=None, gisAPI='gdal'):
    """
    Composite Bands
    
    API's Available:
    * gdal;
    """
    
    if gisAPI == 'gdal':
        """
        Using GDAL
        """
        
        from osgeo         import gdal
        from gasp.fm.rst   import rst_to_array
        from gasp.prop.ff  import drv_name
        from gasp.prop.rst import rst_dataType, get_nodata
        
        # Get Arrays
        _as = [rst_to_array(r) for r in rsts]
        
        # Get nodata values
        nds = [get_nodata(r, gisApi='gdal') for r in rsts]
        
        # Open template and get some metadata
        img_temp = gdal.Open(rsts[0])
        geo_tran = img_temp.GetGeoTransform()
        band     = img_temp.GetRasterBand(1)
        dataType = rst_dataType(band)
        rows, cols = _as[0].shape
        
        # Create Output
        drv = gdal.GetDriverByName(drv_name(outRst))
        out = drv.Create(outRst, cols, rows, len(_as), dataType)
        out.SetGeoTransform(geo_tran)
        
        if epsg:
            from gasp.cpu.gdl.mng.prj import epsg_to_wkt
            srs = epsg_to_wkt(epsg)
            out.SetProjection(srs)
        
        # Write all bands
        for i in range(len(_as)):
            outBand = out.GetRasterBand(i + 1)
            
            outBand.SetNoDataValue(nds[i])
            outBand.WriteArray(_as[i])
            
            outBand.FlushCache()
    
    else:
        raise ValueError('The api {} is not available'.format(gisAPI))
    
    return outRst

