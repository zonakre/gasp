"""
Data to ESRI Shapefile
"""

def shp_to_shp(inShp, outShp, gisApi='ogr', supportForSpatialLite=None):
    """
    Convert a vectorial file to another with other file format
    
    API's Available:
    * ogr;
    * arcpy;
    
    When using gisApi='ogr' - Set supportForSpatialLite to True if outShp is
    a sqlite db and if you want SpatialLite support for that database.
    """
    
    import os
    
    if gisApi == 'ogr':
        from gasp         import exec_cmd
        from gasp.prop.ff import drv_name
        
        out_driver = drv_name(outShp)
    
        if out_driver == 'SQLite' and supportForSpatialLite:
            splite = ' -dsco "SPATIALITE=YES"'
        else:
            splite = ''
    
        cmd = 'ogr2ogr -f "{drv}" {out} {_in}{lite}'.format(
            drv=out_driver, out=outShp, _in=inShp,
            lite=splite
        )
    
        # Run command
        cmdout = exec_cmd(cmd)
    
    elif gisApi == 'arcpy':
        """
        Feature Class to Feature Class using ArcGIS
        """
        
        import arcpy
        
        arcpy.FeatureClassToFeatureClass_conversion(
            inShp, os.path.dirname(outShp), os.path.basename(outShp),
            "", "", ""
        )
    
    else:
        raise ValueError('Sorry, API {} is not available'.format(gisApi))
    
    return outShp


def foldershp_to_foldershp(inFld, outFld, destiny_file_format,
                           file_format='.shp', useApi='ogr'):
    """
    Execute shp_to_shp for every file in inFld (path to folder)
    
    useApi options:
    * ogr;
    """
    
    import os
    from gasp.oss import list_files, get_filename
    
    if not os.path.exists(outFld):
        from gasp.oss.ops import create_folder
        create_folder(outFld)
    
    geo_files = list_files(inFld, file_format=file_format)
    
    for f in geo_files:
        shp_to_shp(f, os.path.join(outFld, '{}.{}'.format(
            get_filename(f), destiny_file_format if \
                destiny_file_format[0] == '.' else '.' + destiny_file_format
        )), gisApi=useApi)
    
    return outFld


def df_to_shp(indf, outShp):
    """
    Pandas Dataframe to ESRI Shapefile
    """
    
    import geopandas
    
    indf.to_file(outShp)
    
    return outShp


def obj_to_shp(dd, geomkey, srs, outshp):
    from gasp.to.obj import obj_to_geodf
    
    geodf = obj_to_geodf(dd, geomkey, srs)
    
    return df_to_shp(geodf, outshp)


def pointXls_to_shp(xlsFile, outShp, x_col, y_col, epsg, sheet=None):
    """
    Excel table with Point information to ESRI Shapefile
    """
    
    from gasp.fm.xls  import xls_to_df
    from gasp.cpu.pnd import pnt_dfwxy_to_geodf
    from gasp.to.shp  import df_to_shp
    
    # XLS TO PANDAS DATAFRAME
    dataDf = xls_to_df(xlsFile, sheet=sheet)
    
    # DATAFRAME TO GEO DATAFRAME
    geoDataDf = pnt_dfwxy_to_geodf(dataDf, x_col, y_col, epsg)
    
    # GEODATAFRAME TO ESRI SHAPEFILE
    df_to_shp(geoDataDf, outShp)
    
    return outShp


"""
PostgreSQL to Feature Class
"""

def psql_to_shp(conParam, table, outshp, api='pandas',
                epsg=None, geom_col='geom', tableIsQuery=None):
    """
    PostgreSQL table to ESRI Shapefile using Pandas or PGSQL2SHP
    """
    
    if api == 'pandas':
        from gasp.fm.psql import psql_to_geodf
        from gasp.to.shp  import df_to_shp
    
        q = "SELECT * FROM {}".format(table) if not tableIsQuery else table
    
        df = psql_to_geodf(conParam, q, geomCol=geom_col, epsg=epsg)
    
        outsh = df_to_shp(df, outshp)
    
    elif api == 'pgsql2shp':
        from gasp import exec_cmd
        
        cmd = (
            'pgsql2shp -f {out} -h {hst} -u {usr} -p {pt} -P {pas}{geom} '
            '{bd} {t}'
        ).format(
            hst=conParam['HOST'], usr=conParam['USER'], pt=conParam['PORT'],
            pas=conParam['PASSWORD'], bd=conParam['DATABASE'],
            t=table if not tableIsQuery else '"{}"'.format(table),
            out=outshp, geom="" if not geom_col else " -g {}".format(geom_col)
        )
        
        outcmd = exec_cmd(cmd)
    
    else:
        raise ValueError('api value must be \'pandas\' or \'pgsql2shp\'')
    
    return outshp


"""
Raster to Feature Class
"""

def rst_to_polyg(inRst, outShp, rstColumn=None, gisApi='gdal', epsg=None):
    """
    Raster to Polygon Shapefile
    
    Api's Available:
    * arcpy;
    * gdal;
    * qgis;
    * pygrass;
    * grasscmd
    """
    
    if gisApi == 'arcpy':
        rstField = 'Value' if not rstColumn else rstColumn
        
        import arcpy
        
        arcpy.RasterToPolygon_conversion(
            in_raster=inRst, 
            out_polygon_features=outShp, 
            simplify=None, 
            raster_field=rstField
        )
    
    elif gisApi == 'gdal':
        if not epsg:
            raise ValueError((
                'Using GDAL, you must specify the EPSG CODE of the '
                'Spatial Reference System of input raster.'
            ))
        
        import os
        from osgeo        import gdal, ogr, osr
        from gasp.prop.ff import drv_name
        from gasp.oss     import get_filename
        
        src = gdal.Open(inRst)
        bnd = src.GetRasterBand(1)
        
        output = ogr.GetDriverByName(drv_name(ouShp)).CreateDataSource(outShp)
        
        srs = osr.SpatialReference()
        srs.ImportFromEPSG(epsg)
        
        lyr = output.CreateLayer(get_filename(outShp, forceLower=True), srs)
        
        lyr.CreateField(ogr.FieldDefn('VALUE', ogr.OFTInteger))
        gdal.Polygonize(bnd, None, lyr, 0, [], callback=None)
        
        output.Destroy()
    
    elif gisApi == 'qgis':
        import processing
        
        processing.runalg(
            "gdalogr:polygonize", inRst, "value", outShp
        )
    
    elif gisApi == 'pygrass':
        from grass.pygrass.modules import Module
        
        rstField = "value" if not rstColumn else rstColumn
        
        rtop = Module(
            "r.to.vect", input=inRst, output=outShp, type="area",
            column=rstField, overwrite=True, run_=False, quiet=True
        )
        rtop()
    
    elif gisApi == 'grasscmd':
        from gasp import exec_cmd
        
        rstField = "value" if not rstColumn else rstColumn
        
        rcmd = exec_cmd((
            "r.to.vect input={} output={} type=area column={} "
            "--overwrite --quiet"
        ).format(inRst, outShp, rstField))
    
    else:
        raise ValueError('Sorry, API {} is not available'.format(gisApi))
    
    return outShp

