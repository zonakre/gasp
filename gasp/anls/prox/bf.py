"""
Buffering Operations
"""

"""
Memory Based
"""
def geoseries_buffer(gseries, dist):
    """
    Buffer of GeoSeries
    """
    
    return gseries.buffer(dist, resolution=16)


def geodf_buffer_to_shp(geoDf, dist, outfile, colgeom='geometry'):
    """
    Execute the Buffer Function of GeoPandas and export
    the result to a new shp
    """
    
    from gasp.to.shp import df_to_shp
    
    __geoDf = geoDf.copy()
    __geoDf["buffer_geom"] = __geoDf[colgeom].buffer(dist, resolution=16)
    
    __geoDf.drop(colgeom, axis=1, inplace=True)
    __geoDf.rename(columns={"buffer_geom" : colgeom}, inplace=True)
    
    df_to_shp(__geoDf, outfile)
    
    return outfile


def draw_buffer(geom, radius):
    return geom.Buffer(int(round(float(radius), 0)))


def coord_to_buffer(x, y, radius):
    from gasp.to.geom import create_point
    
    pnt = create_point(x, y, api='ogr')
    
    return pnt.Buffer(int(round(float(radius), 0)))


"""
File Based
"""
def _buffer(inShp, radius, outShp,
            api='geopandas', dissolve=None, geom_type=None):
    """
    Buffering on Shapefile
    
    API's Available
    * geopandas;
    * saga;
    * grass;
    * pygrass;
    * arcpy;
    """
    
    if api == 'geopandas':
        from gasp.fm import tbl_to_obj
    
        geoDf_ = tbl_to_obj(inShp)
    
        geodf_buffer_to_shp(geoDf_, radius, outShp)
    
    elif api == 'saga':
        """
        A vector based buffer construction partly based on the method supposed by
        Dong et al. 2003. 
        """
        
        from gasp import exec_cmd
        
        distIsField = True if type(radius) == str or type(radius) == unicode \
            else None
        
        c = (
            "saga_cmd shapes_tools 18 -SHAPES {_in} "
            "-BUFFER {_out} {distOption} {d} -DISSOLVE {diss}"
        ).format(
            _in=inShp,
            distOption = "-DIST_FIELD_DEFAULT" if not distIsField else \
                "-DIST_FIELD",
            d=str(radius),
            _out=outShp,
            diss="0" if not dissolve else "1"
        )
        
        outcmd = exec_cmd(c)
    
    elif api=='pygrass':
        from grass.pygrass.modules import Module
        
        if not geom_type:
            raise ValueError((
                'geom_type parameter must have a value when using '
                'pygrass API'
            ))
        
        bf = Module(
            "v.buffer", input=inShp, type=geom_type,
            distance=radius if type(radius) != str else None,
            column=radius if type(radius) == str else None,
            flags='t', output=outShp,
            overwrite=True, run_=False, quiet=True
        )
        
        bf()
    
    elif api == 'grass':
        from gasp import exec_cmd
        
        rcmd = exec_cmd((
            "v.buffer input={} type={} layer=1 {}={} "
            "output={} -t --overwrite --quiet"
        ).format(
            inShp, geom_type,
            "column" if type(radius) == str else "distance",
            str(radius), outShp
        ))
    
    elif api == 'arcpy':
        import arcpy
        
        diss = "NONE" if not dissolve else "LIST" if dissolve != "ALL" and \
            dissolve != "NONE" else dissolve
        
        dissolveCols = None if dissolve != "LIST" else dissolve
        
        arcpy.Buffer_analysis(
            in_features=inShp,
            out_feature_class=outShp,
            buffer_distance_or_field=radius,
            line_side="FULL",
            line_end_type="ROUND",
            dissolve_option=diss,
            dissolve_field=dissolveCols,
            method="PLANAR"
        )
    
    else:
        raise ValueError("{} is not available!".format(api))
    
    return outShp


def buffer_shpFolder(inFolder, outFolder, dist_or_field, fc_format='.shp'):
    """
    Create buffer polygons for all shp in one folder
    """
    
    import os
    from gasp.oss import list_files
    
    lst_fc = list_files(inFolder, file_format=fc_format)
    
    for fc in lst_fc:
        _buffer(
            fc, dist_or_field, os.path.join(outFolder, os.path.basename(fc)),
            api='arcpy' 
        )


def ogr_buffer(geom, radius, out_file, srs=None):
    """
    For each geometry in the input, this method create a buffer and store it
    in a vetorial file
    
    Accepts files or lists with geom objects as inputs
    """
    
    from osgeo         import ogr
    from gasp.mng.prj  import ogr_def_proj
    from gasp.prop.ff  import drv_name
    from gasp.prop.prj import get_sref_from_epsg
    
    # Create output
    buffer_shp = ogr.GetDriverByName(
        drv_name(out_file)).CreateDataSource(out_file)
    
    buffer_lyr = buffer_shp.CreateLayer(
        os.path.splitext(os.path.basename(out_file))[0],
        get_sref_from_epsg(srs) if srs else None,
        geom_type=ogr.wkbPolygon
    )
    
    featDefn = buffer_lyr.GetLayerDefn()
    
    if type(geom) == list:
        for g in geom:
            feat = ogr.Feature(featDefn)
            feat.SetGeometry(draw_buffer(g, radius))
            
            buffer_lyr.CreateFeature(feat)
            
            feat = None
        
        buffer_shp.Destroy()
    
    elif type(geom) == dict:
        if 'x' in geom and 'y' in geom:
            X='x'; Y='y'
        elif 'X' in geom and 'Y' in geom:
            X='X'; Y='Y'
        else:
            raise ValueError((
                'Your geom dict has invalid keys. '
                'Please use one of the following combinations: '
                'x, y; '
                'X, Y'
            ))
        
        from gasp.to.geom import create_point
        feat = ogr.Feature(featDefn)
        g = create_point(geom[X], geom[Y], api='ogr')
        feat.SetGeometry(draw_buffer(g, radius))
        
        buffer_lyr.CreateFeature(feat)
        
        feat = None
        
        buffer_shp.Destroy()
        
        if srs:
            ogr_def_proj(out_file, epsg=srs)
    
    elif type(geom) == str or type(geom) == unicode:
        # Check if the input is a file
        if os.path.exists(geom):
            inShp = ogr.GetDriverByName(drv_name(geom)).Open(geom, 0)
            
            lyr = inShp.GetLayer()
            for f in lyr:
                g = f.GetGeometryRef()
                
                feat = ogr.Feature(featDefn)
                feat.SetGeometry(draw_buffer(g, radius))
                
                buffer_lyr.CreateFeature(feat)
                
                feat = None
            
            buffer_shp.Destroy()
            inShp.Destroy()
            
            if srs:
                ogr_def_proj(out_file, epsg=srs)
            else:
                ogr_def_proj(out_file, template=geom)
            
        else:
            raise ValueError('The given path does not exist')
    
    else:
        raise ValueError('Your geom input is not valid')
    
    return out_file


"""
Buffer Properties
"""

def get_buffer_radius(bfShp, isFile=None):
    """
    Return the radius of a buffer boundary in meters.
    
    The layer must be only one feature
    """
    
    from osgeo import ogr
    
    if isFile:
        bfshp = ogr.GetDriverByName(drv_name(bfShp)).Open(bfShp, 0)
    
        bfLyr = bfShp.GetLayer()
    
        feat = bfLyr[0]; geom = feat.GetGeometryRef()
    
    else:
        geom = ogr.CreateGeometryFromWkt(bfShp)
    
    center = geom.Centroid()
    c=0
    for pnt in geom:
        if c==1:
            break
        pnt_aux = pnt
        c+=1
    
    x_center, y_center = (center.GetX(), center.GetY())
    x_aux, y_aux = (pnt_aux.GetX(), pnt_aux.GetY())
    
    dist = (
        (pnt_aux.GetX() - x_center)**2 + (pnt_aux.GetY() - y_center)**2
    )**0.5
    
    del center
    if isFile:
        bfShp.Destroy()
    
    return round(dist, 0)


def buffer_properties(buffer_shp, epsg_in, isFile=None):
    """
    Return the centroid and radius distance of one buffer geometry
    
    Centroid X, Y in the units of the buffer_shp;
    Radius in meters.
    
    Object return will be something like this:
    o = {
        'X': x_value,
        'Y': y_value,
        'R': radius_value
    }
    """
    
    from gasp.prop.feat import get_centroid_boundary
    
    if isFile:
        from gasp.anls.exct import get_geom_by_index
        
        BUFFER_GEOM = ogr.CreateGeometryFromWkt(
            get_geom_by_index(buffer_shp, 0)
        )
    
    else:
        BUFFER_GEOM = ogr.CreateGeometryFromWkt(buffer_shp)
    
    # Get x_center, y_center and dist from polygon geometry
    # TODO: Besides 4326, we need to include also the others geographic systems
    if int(epsg_in) == 4326:
        from gasp.mng.prj import project_geom
        
        BUFFER_GEOM_R = project_geom(BUFFER_GEOM, epsg_in, 3857, api='ogr')
    
    else:
        BUFFER_GEOM_R = BUFFER_GEOM
    
    dist   = get_buffer_radius(BUFFER_GEOM_R.ExportToWkt(), isFile=None)
    center = get_centroid_boundary(BUFFER_GEOM, isFile=None)
    
    return {
        'X': center.GetX(), 'Y': center.GetY(), 'R': dist
    }


def getBufferParam(inArea, inAreaSRS, outSRS=4326):
    """
    Get Buffer X, Y Center and radius in any SRS (radius in meteres).
    
    Check the type of the 'inArea' Object and return the interest values.
    
    inArea could be a file, dict, list or tuple
    """
    
    import os
    
    from gasp.to.geom import create_point
    from gasp.mng.prj import project_geom    
    
    
    TYPE = type(inArea)
    
    if TYPE == str or TYPE == unicode:
        # Assuming that inArea is a file
        
        # Check if exists
        if os.path.exists(inArea):
            if os.path.isfile(inArea):
                from gasp.anls.exct import get_geom_by_index
                
                # Get Geometry object
                BUFFER_GEOM = get_geom_by_index(inArea, 0)
                
                # To outSRS
                if int(inAreaSRS) != outSRS:
                    BUFFER_GEOM = project_geom(
                        ogr.CreateGeometryFromWkt(BUFFER_GEOM),
                        inAreaSRS, outSRS, api='ogr'
                    ).ExportToWkt()
                
                # Get x_center, y_center and radius
                xyr = buffer_properties(BUFFER_GEOM, outSRS, isFile=None)
                x_center, y_center, dist = str(
                    xyr['X']), str(xyr['Y']), str(xyr['R'])
            
            else:
                raise ValueError(
                    'The given path exists but it is not a file'
                )
    
        else:
            raise ValueError('The given path doesn\'t exist')
    
    elif TYPE == dict:
        X = 'x' if 'x' in inArea else 'X' if 'X' in inArea else \
            'lng' if 'lng' in inArea else None
        
        Y = 'y' if 'x' in inArea else 'Y' if 'Y' in inArea else \
            'lat' if 'lat' in inArea else None
        
        R = 'r' if 'r' in inArea else 'R' if 'R' in inArea else \
            'rad' if 'rad' in inArea else 'RADIUS' if 'RADIUS' in inArea \
            else 'radius' if 'radius' in inArea else None
        
        if not X or not Y or not R:
            raise ValueError((
                'The keys used to identify the buffer properties '
                'are not valid! '
                'Please choose one of the following keys groups: '
                'x, y, r; '
                'X, Y, R; '
                'lat, lng, rad'
            ))
        
        else:
            x_center, y_center, dist = (
                str(inArea[X]), str(inArea[Y]), str(inArea[R])
            )
            
            if inAreaSRS != outSRS:
                pnt_wgs = project_geom(
                    create_point(x_center, y_center, api='ogr'),
                    inAreaSRS, outSRS, api='ogr'
                )
                
                x_center, y_center = (pnt_wgs.GetX(), pnt_wgs.GetY())
    
    elif TYPE == list or TYPE == tuple:
        x_center, y_center, dist = inArea
        
        if inAreaSRS != outSRS:
            pnt_wgs = project_geom(
                create_point(x_center, y_center, api='ogr'),
                inAreaSRS, outSRS, api='ogr'
            )
            
            x_center, y_center = (pnt_wgs.GetX(), pnt_wgs.GetY())
    
    else:
        raise ValueError((
            'Please give a valid path to a shapefile or a tuple, dict or '
            'list with the x, y and radius values'
        ))
    
    return x_center, y_center, dist


def dic_buffer_array_to_shp(arrayBf, outShp, epsg, fields=None):
    """
    Array with dict with buffer proprieties to Feature Class
    """
    
    import os
    from osgeo         import ogr
    from gasp.prop.ff  import drv_name
    from gasp.prop.prj import get_sref_from_epsg
    
    # Get SRS for output
    srs = get_sref_from_epsg(epsg)
    
    # Create output DataSource and Layer
    outData = ogr.GetDriverByName(drv_name(outShp)).CreateDataSource(outShp)
    
    lyr = outData.CreateLayer(
        os.path.splitext(os.path.basename(outShp))[0],
        srs, geom_type=ogr.wkbPolygon
    )
    
    # Create fields
    if fields:
        from gasp.mng.fld import add_fields
        
        add_fields(lyr, fields)
    
    lyrDefn = lyr.GetLayerDefn()
    for _buffer in arrayBf:
        newFeat = ogr.Feature(lyrDefn)
        
        geom = coord_to_buffer(_buffer["X"], _buffer["Y"], _buffer["RADIUS"])
        
        newFeat.SetGeometry(geom)
        
        for field in fields:
            if field in _buffer.keys():
                newFeat.SetField(field, _buffer[field])
        
        lyr.CreateFeature(newFeat)
        
        newFeat.Destroy()
    
    del lyrDefn
    outData.Destroy()
    
    return outShp


def get_sub_buffers(x, y, radius):
    """
    Get Smaller Buffers for each cardeal point (North,
    South, East, West, Northeast, Northwest,
    Southwest and Southeast)
    """
    
    sub_buf = ['north', 'northeast', 'east', 'southeast',
               'south', 'southwest', 'west', 'northwest']
    
    lstSubBuffer = []
    
    for cardeal in sub_buf:
        if cardeal == 'north':
            _y = y + (radius / 2)
        
        elif cardeal == 'northeast' or cardeal == 'northwest':
            _y =  y + ((radius)**2 / 8.0)**0.5
        
        elif cardeal == 'south':
            _y = y - (radius / 2)
        
        elif cardeal == 'southwest' or cardeal == 'southeast':
            _y = y - ((radius)**2 / 8.0)**0.5
        
        else:
            _y = y
        
        if cardeal == 'west':
            _x = x - (radius / 2)
        
        elif cardeal == 'southwest' or cardeal == 'northwest':
            _x = x - ((radius)**2 / 8.0)**0.5
        
        elif cardeal == 'east':
            _x = x + (radius / 2)
        
        elif cardeal == 'southeast' or cardeal == 'northeast':
            _x = x + ((radius)**2 / 8.0)**0.5
        
        else:
            _x = x
        
        lstSubBuffer.append({
            'X' : _x, 'Y' : _y,
            'RADIUS' : radius / 2,
            'cardeal' : cardeal
        })
    
    return lstSubBuffer

