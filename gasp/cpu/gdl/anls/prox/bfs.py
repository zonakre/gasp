"""
OGR Buffering
"""

import os
from osgeo import ogr

def draw_buffer(geom, radius):
    return geom.Buffer(int(round(float(radius), 0)))


def coord_to_buffer(x, y, radius):
    from gasp.cpu.gdl import create_point
    
    pnt = create_point(x, y)
    
    return pnt.Buffer(int(round(float(radius), 0)))


def ogr_buffer(geom, radius, out_file, srs=None):
    """
    For each geometry in the input, this method create a buffer and store it
    in a vetorial file
    
    Accepts files or lists with geom objects as inputs
    """
    
    from gasp.cpu.gdl         import drv_name
    from gasp.cpu.gdl.mng.prj import get_sref_from_epsg
    
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
        
        from gasp.cpu.gdl import create_point
        feat = ogr.Feature(featDefn)
        g = create_point(geom[X], geom[Y])
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


def get_buffer_radius(bfShp, isFile=None):
    """
    Return the radius of a buffer boundary in meters.
    
    The layer must be only one feature
    """
    
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
    
    from gasp.cpu.gdl import get_centroid_boundary
    
    if isFile:
        from gasp.cpu.gdl import get_geom_by_index
        
        BUFFER_GEOM = ogr.CreateGeometryFromWkt(
            get_geom_by_index(buffer_shp, 0)
        )
    
    else:
        BUFFER_GEOM = ogr.CreateGeometryFromWkt(buffer_shp)
    
    # Get x_center, y_center and dist from polygon geometry
    # TODO: Besides 4326, we need to include also the others geographic systems
    if int(epsg_in) == 4326:
        from gasp.cpu.gdl.mng.prj import project_geom
        
        BUFFER_GEOM_R = project_geom(BUFFER_GEOM, epsg_in, 3857)
    
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
    
    from gasp.cpu.gdl         import create_point
    from gasp.cpu.gdl.mng.prj import project_geom    
    
    
    TYPE = type(inArea)
    
    if TYPE == str or TYPE == unicode:
        # Assuming that inArea is a file
        
        # Check if exists
        if os.path.exists(inArea):
            if os.path.isfile(inArea):
                from gasp.cpu.gdl import get_geom_by_index
                
                # Get Geometry object
                BUFFER_GEOM = get_geom_by_index(inArea, 0)
                
                # To outSRS
                if int(inAreaSRS) != outSRS:
                    BUFFER_GEOM = project_geom(
                        ogr.CreateGeometryFromWkt(BUFFER_GEOM),
                        inAreaSRS, outSRS
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
                    create_point(x_center, y_center),
                    inAreaSRS, outSRS
                )
                
                x_center, y_center = (pnt_wgs.GetX(), pnt_wgs.GetY())
    
    elif TYPE == list or TYPE == tuple:
        x_center, y_center, dist = inArea
        
        if inAreaSRS != outSRS:
            pnt_wgs = project_geom(
                create_point(x_center, y_center), inAreaSRS, outSRS
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
    from osgeo                import ogr
    from gasp.cpu.gdl         import drv_name
    from gasp.cpu.gdl.mng.prj import get_sref_from_epsg
    
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
        from gasp.cpu.gdl.mng.fld import add_fields
        
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
