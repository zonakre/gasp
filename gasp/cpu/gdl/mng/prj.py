"""
Manage spatial reference systems of any geometry or feature class with OGR
"""


import os
from osgeo        import osr
from osgeo        import ogr
from osgeo        import gdal
from gasp.prop.ff import drv_name


def epsg_to_wkt(epsg):
    s = osr.SpatialReference()
    s.ImportFromEPSG(epsg)
    
    return s.ExportToWkt()


def get_sref_from_epsg(epsg):
    s = osr.SpatialReference()
    s.ImportFromEPSG(epsg)
    
    return s 

def get_epsg_raster(rst):
    """
    Return the EPSG Code of the Spatial Reference System of a Raster
    """
    
    d    = gdal.Open(rst)
    proj = osr.SpatialReference(wkt=d.GetProjection())
    
    return int(proj.GetAttrValue('AUTHORITY',1))


def get_trans_param(in_epsg, out_epsg, export_all=None):
    """
    Return transformation parameters for two Spatial Reference Systems
    """
    
    i = osr.SpatialReference()
    i.ImportFromEPSG(in_epsg)
    o = osr.SpatialReference()
    o.ImportFromEPSG(out_epsg)
    t = osr.CoordinateTransformation(i, o)
    if not export_all:
        return t
    else:
        return {'input': i, 'output': o, 'transform': t}


def ogr_def_proj(shp, epsg=None, template=None):
    """
    Create/Replace the prj file of a ESRI Shapefile
    """
    
    prj_file = '{}.prj'.format(
        os.path.join(
            os.path.dirname(shp),
            os.path.splitext(os.path.basename(shp))[0]
        )
    )
    if epsg and not template:
        s = osr.SpatialReference()
        s.ImportFromEPSG(int(epsg))
        s.MorphToESRI()
        prj = open(prj_file, 'w')
        prj.write(s.ExportToWkt())
        prj.close()
        return prj_file
    
    elif not epsg and template:
        prj_template = '{}.prj'.format(
            os.path.splitext(os.path.basename(template))[0]
        )
        
        if not os.path.exists(prj_template):
            return 0
        
        try:
            os.remove(prj_file)
            shutil.copyfile(prj_template, prj_file)
        except:
            shutil.copyfile(prj_template, prj_file)
        
        return prj_file


def get_shp_sref(shp):
    """
    Get Spatial Reference Object from Feature Class/Lyr
    """
    
    if type(shp) == ogr.Layer:
        lyr = shp
        
        c = 0
    
    else:
        data = ogr.GetDriverByName(
            drv_name(shp)).Open(shp)
        
        lyr = data.GetLayer()
        c = 1
    
    spref = lyr.GetSpatialRef()
    
    if c:
        del lyr
        data.Destroy()
    
    return spref


def project_geom(geom, inEpsg, outEpsg):
    """
    Change SRS of an OGR Geometry
    """
    
    __geom = ogr.CreateGeometryFromWkt(geom.ExportToWkt())
    
    __geom.Transform(get_trans_param(inEpsg, outEpsg))
    
    return __geom


# Transform data in a geogile using ogr2ogr
def ogr2ogr_transform_to_file(inShp, inEpsg, outEpsg, outFile,
                              sql=None):
    """
    Transform SRS of any OGR Compilant Data. Save the transformed data
    in a new file
    
    TODO: DB - only works with sqlite
    """
    
    from gasp import exec_cmd
    
    cmd = (
        'ogr2ogr -f "{}" {} {}{} -s_srs EPSG:{} -t_srs:{}'
    ).format(
        drv_name(outFile), outFile, inShp,
        '' if not sql else ' -dialect sqlite -sql "{}"'.format(sql),
        str(inEpsg), str(outEpsg)
    )
    
    outcmd = exec_cmd(cmd)


def ogr2ogr_transform_inside_sqlite(sqliteDb, table, inEpsg,
                                    outEpsg, newTable,
                                    sql=None):
    """
    Transform SRS of a SQLITE DB table. Save the transformed data in a
    new table
    """
    
    import os
    from gasp import exec_cmd
    
    # TODO: Verify if database is sqlite
    
    sql = 'SELECT * FROM {}'.format(table) if not sql else sql
    cmd = (
        'ogr2ogr -update -append -f "SQLite" {db} -nln "{nt}" '
        '-dialect sqlite -sql "{_sql}" -s_srs EPSG:{inepsg} '
        '-t_srs EPSG:{outepsg} {db}'
    ).format(
        db=sqliteDb, nt=newTable, _sql=sql, inepsg=str(inEpsg),
        outepsg=str(outEpsg)
    )
    
    outcmd = exec_cmd(cmd)

"""
Manage spatial reference systems of any raster dataset
"""

def set_proj(rst, epsg):
    """
    Define Raster projection
    """
    
    from osgeo import osr
    
    img = gdal.Open(rst, 1)
    
    srs = osr.SpatialReference()
    srs.ImportFromEPSG(epsg)
    
    img.SetProjection(srs.ExportToWkt())
    
    img.FlushCache()


def gdal_reproject_raster(inRst, outRst, inEPSG, outEPSG):
    """
    Reproject Raster dataset using gdalwarp
    """
    
    import sys
    from gasp import exec_cmd
    
    cmd = (
        'gdalwarp -overwrite {inrst} {outrst} -s_srs EPSG:{inepsg} '
        '-t_srs EPSG:{outepsg}'
    ).format(
        inrst=inRst, inepsg=inEPSG,
        outrst=outRst, outepsg=outEPSG
    )
    
    codecmd = exec_cmd(cmd)
    
    return outRst


def reproject_raster(inRst, inEpsg, outEpsg, outRst, pixel_spacing=5000.0,
                     data_type=gdal.GDT_Float32):
    """
    TODO: SEE WHY THIS IS NOT WORKING

    CELLSIZE CALCULATED IS 0 - THIS NUMBER MUST BE MAJOR THAN 0
    """
    """
    A sample function to reproject and resample a GDAL dataset from within 
    Python. The idea here is to reproject from one system to another, as well
    as to change the pixel size. The procedure goes like this:

    1. Set up the two Spatial Reference systems.
    2. Open the original dataset, and get the geotransform
    3. Calculate bounds of new geotransform by projecting the UL corners 
    4. Calculate the number of pixels with the new projection & spacing
    5. Create an in-memory raster dataset
    6. Perform the projection
    """

    #from pysage.tools_thru_api.gdal.gdal import GDAL_GetDriverName

    # Get transformation parameters
    transform_dic = get_trans_param(inEpsg, outEpsg, export_all=True)
    transform_p = transform_dic['transform']

    # Up to here, all  the projection have been defined, as well as a 
    # transformation from the from to the  to :)
    # We now open the dataset
    g = gdal.Open(inRst)
    # Get the Geotransform vector
    geo_t = g.GetGeoTransform()
    x_size = g.RasterXSize # Raster xsize
    y_size = g.RasterYSize # Raster ysize
    # Work out the boundaries of the new dataset in the target projection
    (ulx, uly, ulz) = transform_p.TransformPoint(geo_t[0], geo_t[3])
    (lrx, lry, lrz) = transform_p.TransformPoint(
        geo_t[0] + geo_t[1]*x_size, geo_t[3] + geo_t[5]*y_size )

    # Now, we create an output raster
    mem_drv = gdal.GetDriverByName(GDAL_GetDriverName(outRst))
    # The size of the raster is given the new projection and pixel spacing
    # Using the values we calculated above. Also, setting it to store one band
    # and to use Float32 data type.
    dest = mem_drv.Create(outRst, int((lrx - ulx)/pixel_spacing),
                          int((uly - lry)/pixel_spacing), 1, data_type)
    
    # Calculate the new geotransform
    new_geo = (ulx, pixel_spacing, geo_t[2], 
               uly, geo_t[4], -pixel_spacing )
    # Set the geotransform
    dest.SetGeoTransform(new_geo)
    dest.SetProjection(transform_dic['output'].ExportToWkt())
    # Perform the projection/resampling 
    res = gdal.ReprojectImage(
        g, dest, transform_dic['input'].ExportToWkt(),
        transform_dic['output'].ExportToWkt(), 
        gdal.GRA_Bilinear
    )

