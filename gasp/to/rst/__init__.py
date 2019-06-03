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
            from gasp.prop.prj import epsg_to_wkt
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
            from gasp.prop.prj import epsg_to_wkt
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


"""
Change data format
"""

def rst_to_rst(inRst, outRst):
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
    
    import netCDF4;     import os
    from gasp.oss       import list_files
    from gasp.mng.split import gdal_split_bands
    
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
            rst_to_rst(nc, output)
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
                rst_to_rst(
                    'NETCDF:"{n}":{v}'.format(n=nc, v=dts),
                    output
                )
                gdal_split_bands(output, outFolder)


"""
Feature Classes to Raster tools
"""

def shp_to_raster(shp, inSource, cellsize, nodata, outRaster, epsg=None,
                  rst_template=None, api='gdal', snap=None):
    """
    Feature Class to Raster
    
    cellsize will be ignored if rst_template is defined
    
    * API's Available:
    - gdal;
    - arcpy;
    - pygrass;
    - grass;
    """
    
    if api == 'gdal':
        from osgeo        import gdal, ogr
        from gasp.prop.ff import drv_name
    
        if not epsg:
            from gasp.prop.prj import get_shp_sref
            srs = get_shp_sref(shp).ExportToWkt()
        else:
            from gasp.prop.prj import epsg_to_wkt
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
        
        dtRst.SetProjection(str(srs))
    
        bnd = dtRst.GetRasterBand(1)
        bnd.SetNoDataValue(nodata)
    
        gdal.RasterizeLayer(dtRst, [1], lyr, burn_values=[1])
    
        del lyr
        dtShp.Destroy()
    
    elif api == 'arcpy':
        import arcpy
        
        if rst_template:
            tempEnvironment0 = arcpy.env.extent
            arcpy.env.extent = template
        
        if snap:
            tempSnap = arcpy.env.snapRaster
            arcpy.env.snapRaster = snap
        
        obj_describe = arcpy.Describe(shp)
        geom = obj_describe.ShapeType
        
        if geom == u'Polygon':
            arcpy.PolygonToRaster_conversion(
                shp, inField, outRaster, "CELL_CENTER", "NONE", cellsize
            )
        
        elif geom == u'Polyline':
            arcpy.PolylineToRaster_conversion(
                shp, inField, outRaster, "MAXIMUM_LENGTH", "NONE", cellsize
            )
        
        if rst_template:
            arcpy.env.extent = tempEnvironment0
        
        if snap:
            arcpy.env.snapRaster = tempSnap
    
    elif api == 'grass' or api == 'pygrass':
        """
        Vectorial geometry to raster
    
        If source is None, the convertion will be based on the cat field.
    
        If source is a string, the convertion will be based on the field
        with a name equal to the given string.
    
        If source is a numeric value, all cells of the output raster will have
        that same value.
        """
        
        __USE = "cat" if not inSource else "attr" if type(inSource) == str or \
            type(inSource) == unicode else "val" if type(inSource) == int or \
            type(inSource) == float else None
        
        if not __USE:
            raise ValueError('\'source\' parameter value is not valid')
        
        if api == 'pygrass':
            from grass.pygrass.modules import Module
            
            m = Module(
                "v.to.rast", input=shp, output=outRaster, use=__USE,
                attribute_column=inSource if __USE == "attr" else None,
                value=inSource if __USE == "val" else None,
                overwrite=True, run_=False, quiet=True
            )
            
            m()
        
        else:
            from gasp import exec_cmd
            
            rcmd = exec_cmd((
                "v.to.rast input={} output={} use={}{} "
                "--overwrite --quiet"
            ).format(
                shp, outRaster, __USE,
                "" if __USE == "cat" else " attribute_column={}".format(inSource) \
                    if __USE == "attr" else " val={}".format(inSource)
            ))
    
    else:
        raise ValueError('API {} is not available'.format(api))
    
    return outRaster


def rst_to_grs(rst, grsRst, as_cmd=None):
    """
    Raster to GRASS GIS Raster
    """
    
    if not as_cmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            "r.in.gdal", input=rst, output=grsRst, flags='o',
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "r.in.gdal input={} output={} -o --overwrite "
            "--quiet"
        ).format(rst, grsRst))
    
    return grsRst


def grs_to_rst(grsRst, rst, as_cmd=None, allBands=None):
    """
    GRASS Raster to Raster
    """
    
    from gasp.prop.ff import RasterDrivers
    from gasp.oss     import get_fileformat
    
    rstDrv = RasterDrivers()
    rstExt = get_fileformat(rst)
    
    if not as_cmd:
        from grass.pygrass.modules import Module
        
        m = Module(
            "r.out.gdal", input=grsRst, output=rst,
            format=rstDrv[rstExt], flags='c' if not allBands else '',
            createopt="INTERLEAVE=PIXEL,TFW=YES" if allBands else '',
            overwrite=True, run_=False, quiet=True
        )
        
        m()
    
    else:
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "r.out.gdal input={} output={} format={} "
            "{} --overwrite --quiet"
        ).format(
            grsRst, rst, rstDrv[rstExt],
            "-c" if not allBands else "createopt=\"INTERLEAVE=PIXEL,TFW=YES\""
        ))
    
    return rst


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

