"""
Processing Raster data with GDAL
"""

def clip_rst(raster, clipShp, outRst, nodataValue=None):
    """
    Clip Raster using GDAL WARP
    """
    
    from gasp         import exec_cmd
    from gasp.prop.ff import drv_name
    
    outcmd = exec_cmd((
        "gdalwarp {ndata}-cutline {clipshp} -crop_to_cutline "
        "-of {ext} {inraster} -overwrite {outrst}"
    ).format(
        clipshp=clipShp, inraster=raster, outrst=outRst,
        ext=drv_name(outRst),
        ndata="-dstnodata {} ".format(
            str(nodataValue)) if nodataValue else ""
    ))
    
    return outRst


def raster_rotation(inFolder, template, outFolder, img_format='.tif'):
    """
    Invert raster data
    """
    
    import os
    from osgeo         import gdal
    from gasp.oss      import list_files
    from gasp.fm.rst   import rst_to_array
    from gasp.prop.rst import get_nodata
    from gasp.to.rst   import array_to_raster
    
    rasters = list_files(inFolder, file_format=img_format)
    
    for rst in rasters:
        a  = rst_to_array(rst)
        nd = get_nodata(rst, gisApi='gdal')
        
        array_to_raster(
            a[::-1],
            os.path.join(outFolder, os.path.basename(rst)),
            template, None, gdal.GDT_Float32, noData=nd,
            gisApi='gdal'
        )

