"""
GDAL Reclass Rasters
"""

from osgeo import gdal


def rcls_raster(inRaster, outRaster, rclsRules):
    """
    Reclassify a raster (categorical and floating points)
    """
    
    """
    Example to guide on the construction of the real script
    gdalData = gdal.Open(Input_raster) 
    raster = gdalData.ReadAsArray()
    #reclassify raster values equal 16 to 7 using Numpy
    class_num = [float(numeric_string) for numeric_string in Output_classes.split(',')]
    #create a copy of raster
    raster_temp=copy(raster)
    #Here we suppose that the class_in are sequential
    class_in=0.
    for i in class_num:
        mask=(raster==class_in)
        raster_temp[mask]=i
        class_in = class_in+1
    # write results to file (but at first check if we are able to write this format)
    format = "GTiff"
    driver = gdal.GetDriverByName(format)
    outData = driver.CreateCopy(Output_raster, gdalData, 0)
    outData.GetRasterBand(1).WriteArray(raster_temp)
    mask=None
    raster=None
    raster_temp=None
    gdalData=None
    """
    
    return outRaster

