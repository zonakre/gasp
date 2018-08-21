"""
Manage data with gdal
"""


def gdal_split_bands(inRst, outFolder):
    """
    Export all bands of a raster to a new dataset
    
    TODO: this could be done using gdal_translate
    """
    
    from osgeo import gdal
    import numpy; import os
    from gasp.prop.rst import get_nodata
    from gasp.to.rst import array_to_raster
    
    rst = gdal.Open(inRst)
    
    if rst.RasterCount == 1:
        return
    
    nodata = get_nodata(inRst, gisApi='gdal')
    
    for band in range(rst.RasterCount):
        band += 1
        src_band = rst.GetRasterBand(band)
        if src_band is None:
            continue
        else:
            # Convert to array
            array = numpy.array(src_band.ReadAsArray())
            array_to_raster(
                array,
                os.path.join(
                    outFolder,
                    '{r}_{b}.tif'.format(
                        r=os.path.basename(os.path.splitext(inRst)[0]),
                        b=str(band)
                    )
                ),
                inRst,
                None,
                gdal.GDT_Float32, noData=nodata, gisApi='gdal'
            )

