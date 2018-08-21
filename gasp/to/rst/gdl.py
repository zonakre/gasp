"""
Feature Class to Raster Dataset
"""

def shp_to_raster(shp, cellsize, nodata, outRaster, epsg=None,
                  rst_template=None):
    """
    Feature Class to Raster
    
    cellsize will be ignored if rst_template is defined
    """
    
    from osgeo        import gdal, ogr
    from gasp.prop.ff import drv_name
    
    if not epsg:
        from gasp.cpu.gdl.mng.prj import get_shp_sref
        srs = get_shp_sref(shp).ExportToWkt()
    else:
        from gasp.cpu.gdl.mng.prj import epsg_to_wkt
        srs = epsg_to_wkt(epsg)
    
    # Get Extent
    dtShp = ogr.GetDriverByName(
        drv_name(shp)).Open(shp, 0)
    
    lyr = dtShp.GetLayer()
    
    if not rst_template:
        x_min, x_max, y_min, y_max = lyr.GetExtent()
        x_res = int((x_max - x_min) / cellsize)
        y_res = int((y_max - y_min) / cellsize)
    
    else:
        from gasp.fm.rst import rst_to_array
        
        img_temp = gdal.Open(rst_template)
        geo_transform = img_temp.GetGeoTransform()
        
        y_res, x_res = rst_to_array(rst_template).shape
    
    # Create output
    dtRst = gdal.GetDriverByName(drv_name(outRaster)).Create(
        outRaster, x_res, y_res, gdal.GDT_Byte
    )
    
    if not rst_template:
        dtRst.SetGeoTransform((x_min, cellsize, 0, y_max, 0, -cellsize))
    
    else:
        dtRst.SetGeoTransform(geo_transform)
    dtRst.SetProjection(srs)
    
    bnd = dtRst.GetRasterBand(1)
    bnd.SetNoDataValue(nodata)
    
    gdal.RasterizeLayer(dtRst, [1], lyr, burn_values=[1])
    
    del lyr
    dtShp.Destroy()
    
    return outRaster


def shape_to_rst_wShapeCheck(inShp, maxCellNumber, desiredCellsizes, outRst,
                             inEPSG):
    """
    Convert one Feature Class to Raster using the cellsizes included
    in desiredCellsizes. For each cellsize, check if the number of cells
    exceeds maxCellNumber. The raster with lower cellsize but lower than
    maxCellNumber will be the returned raster
    """
    
    import os
    from gasp          import goToList
    from gasp.prop.rst import rst_shape
    
    desiredCellsizes = goToList(desiredCellsizes)
    if not desiredCellsizes:
        raise ValueError(
            'desiredCellsizes does not have a valid value'
        )
    
    workspace = os.path.dirname(outRst)
    
    RASTERS = [shp_to_raster(
        inShp, cellsize, -1, os.path.join(
            workspace, 'tst_cell_{}.tif'.format(cellSize)
        ), inEPSG
    ) for cellSize in desiredCellsizes]
    
    tstShape = rst_shape(RASTERS, gisApi='gdal')
    
    for rst in tstShape:
        NCELLS = tstShape[rst][0] * tstShape[rst][1]
        tstShape[rst] = NCELLS
    
    NICE_RASTER = None
    for i in range(len(desiredCellsizes)):
        if tstShape[RASTERS[i]] <= maxCellNumber:
            NICE_RASTER = RASTERS[i]
            break
        
        else:
            continue
    
    if not NICE_RASTER:
        return None
    
    else:
        os.rename(NICE_RASTER, outRst)
        
        for rst in RASTERS:
            if os.path.isfile(rst) and os.path.exists(rst):
                os.remove(rst)
        
        return outRst


"""
Change data format
"""

def gdal_translate(inRst, outRst):
    """
    Convert a raster file to another raster format
    """
    
    from gasp         import exec_cmd
    from gasp.prop.ff import drv_name
    
    outDrv = drv_name(outRst)
    cmd = 'gdal_translate -of {drv} {_in} {_out}'.format(
        drv=outDrv, _in=inRst, _out=outRst
    )
    
    cmdout = exec_cmd(cmd)
    
    return outRst


def folder_nc_to_tif(inFolder, outFolder):
    """
    Convert all nc existing on a folder to GTiff
    """
    
    import netCDF4;           import os
    from gasp.oss             import list_files
    from gasp.cpu.gdl.mng.rst import gdal_split_bands
    
    # List nc files
    lst_nc = list_files(inFolder, file_format='.nc')
    
    # nc to tiff
    for nc in lst_nc:
        # Check the number of images in nc file
        datasets = []
        _nc = netCDF4.Dataset(nc, 'r')
        for v in _nc.variables:
            if v == 'lat' or v == 'lon':
                continue
            lshape = len(_nc.variables[v].shape)
            if lshape >= 2:
                datasets.append(v)
        # if the nc has any raster
        if len(datasets) == 0:
            continue
        # if the nc has only one raster
        elif len(datasets) == 1:
            output = os.path.join(
                outFolder,
                os.path.basename(os.path.splitext(nc)[0]) + '.tif'
            )
            gdal_translate(nc, output)
            gdal_split_bands(output, outFolder)
        # if the nc has more than one raster
        else:
            for dts in datasets:
                output = os.path.join(
                    outFolder,
                    '{orf}_{v}.tif'.format(
                        orf = os.path.basename(os.path.splitext(nc)[0]),
                        v = dts
                    )
                )
                gdal_translate(
                    'NETCDF:"{n}":{v}'.format(n=nc, v=dts),
                    output
                )
                gdal_split_bands(output, outFolder)

