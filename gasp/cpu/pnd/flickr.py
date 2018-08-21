"""
Extract Geodata from flickr using OGR
"""


def photos_location(buffer_shp, epsg_in, keyword=None, epsg_out=4326,
                    onlySearchAreaContained=True, keyToUse=None):
    """
    Search for data in Flickr and return a array with the same data
    
    buffer_shp cloud be a shapefile with a single buffer feature or a dict
    like:
    buffer_shp = {
        x: x_value,
        y: y_value,
        r: dist (in meters)
    }
    or a list or a tuple:
    buffer_shp = [x, y, radius]
    """
    
    import pandas
    from shapely.geometry           import Polygon, Point
    from shapely.wkt                import loads
    from geopandas                  import GeoDataFrame
    from gasp.fm.api.flickr         import search_photos
    from gasp.cpu.gdl.anls.prox.bfs import coord_to_buffer
    from gasp.cpu.gdl.anls.prox.bfs import getBufferParam
    from gasp.cpu.gdl.mng.prj       import project_geom
    
    x_center, y_center, dist = getBufferParam(buffer_shp, epsg_in, outSRS=4326)
    
    # Retrive data from Flickr
    photos = search_photos(
        lat=y_center, lng=x_center, radius=float(dist) / 1000,
        keyword=keyword, apiKey=keyToUse
    )
    
    try:
        if not photos:
            # Return noData
            return 0
    except:
        pass
    
    photos['longitude'] = photos['longitude'].astype(float)
    photos['latitude']  = photos['latitude'].astype(float)
    
    geoms = [Point(xy) for xy in zip(photos.longitude, photos.latitude)]
    gdata = GeoDataFrame(photos, crs={'init' : 'epsg:4326'}, geometry=geoms)
    
    if onlySearchAreaContained:
        _x_center, _y_center, _dist = getBufferParam(
            buffer_shp, epsg_in, outSRS=3857)
        # Check if all retrieve points are within the search area
        search_area = coord_to_buffer(
            float(_x_center), float(_y_center), float(_dist))
        search_area = project_geom(search_area, 3857, 4326)
        search_area = loads(search_area.ExportToWkt())
        
        gdata["tst_geom"] = gdata["geometry"].intersects(search_area)
        gdata = gdata[gdata["tst_geom"] == True]
        
        gdata.reset_index(drop=True, inplace=True)
    
    gdata["fid"] = gdata["id"]
    
    if "url_l" in gdata.columns.values:
        gdata["url"] = gdata["url_l"]
    else:
        gdata["url"] = 'None'
    
    gdata["description"] = gdata["_content"]
        
    # Drop irrelevant fields
    cols = list(gdata.columns.values)
    delCols = []
    
    for col in cols:
        if col != 'geometry' and  col != 'description' and \
            col != 'fid' and col != 'url' and col != 'datetaken' \
            and col != 'dateupload' and col != 'title':
            delCols.append(col)
        else:
            continue
    
    gdata.drop(delCols, axis=1, inplace=True)
    
    if epsg_out != 4326:
        gdata = gdata.to_crs({'init' : 'epsg:{}'.format(str(epsg_out))})
    
    return gdata


def photos_to_shp(buffer_shp, epsg_in, outshp, keyword=None,
                  epsg_out=4326, apikey=None, onlyInsideInput=True):
    """
    Search for data in Flickr and return a Shapefile with the 
    data.
    """
    
    from gasp.to.shp import df_to_shp
    
    photos = photos_location(
        buffer_shp, epsg_in, keyword=keyword, epsg_out=epsg_out,
        keyToUse=apikey, onlySearchAreaContained=onlyInsideInput
    )
    
    try:
        if not photos: return 0
    except: pass
    
    df_to_shp(photos, outshp)
    
    return outshp

