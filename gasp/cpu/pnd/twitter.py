"""
Extract Geodata from Twitter using OGR
"""


def geotweets_location(inGeom, epsg_in, keyword=None, epsg_out=4326,
                       onlySearchAreaContained=True, keyToUse=None):
    """
    Search data in Twitter and array with that data
    
    inGeom cloud be a shapefile with a single buffer feature or a dict like:
    inGeom = {
        x: x_value,
        y: y_value,
        r: dist (in meters)
    }
    or a list or a tuple:
    inGeom = [x, y, radius]
    """
    
    from shapely.geometry           import Polygon, Point
    from geopandas                  import GeoDataFrame
    from gasp.cpu.gdl.anls.prox.bfs import getBufferParam
    from gasp.fm.api.twitter        import search_tweets
    
    x_center, y_center, dist = getBufferParam(inGeom, epsg_in, outSRS=4326)
    
    # Extract data from Twitter
    data = search_tweets(
        lat=y_center, lng=x_center, radius=float(dist) / 1000,
        keyword=keyword, NR_ITEMS=500, only_geo=True, key=keyToUse
    )
    
    try:
        if not data:
            return 0
    except:
        pass
    
    # Pandas to GeoPandas
    geoms = [Point(xy) for xy in zip(data.longitude, data.latitude)]
    data.drop(["latitude", "longitude"], axis=1, inplace=True)
    gdata = GeoDataFrame(data, crs={'init' : 'epsg:4326'}, geometry=geoms)
    
    if onlySearchAreaContained:
        from shapely.wkt                import loads
        from gasp.cpu.gdl.mng.prj       import project_geom
        from gasp.cpu.gdl.anls.prox.bfs import coord_to_buffer
        
        # Check if all retrieve points are within the search area
        _x_center, _y_center, _dist = getBufferParam(
            inGeom, epsg_in, outSRS=3857)
        
        search_area = coord_to_buffer(
            float(_x_center), float(_y_center), float(_dist)
        )
        search_area = project_geom(search_area, 3857, 4326)
        search_area = loads(search_area.ExportToWkt())
        
        gdata["tst_geom"] = gdata["geometry"].intersects(search_area)
        gdata = gdata[gdata["tst_geom"] == True]
        
        gdata.reset_index(drop=True, inplace=True)
    
    gdata.drop("tst_geom", axis=1, inplace=True)
    
    if epsg_out != 4326:
        gdata = gdata.to_crs({'init' : 'epsg:{}'.format(str(epsg_out))})
    
    return gdata


def tweets_to_shp(buffer_shp, epsg_in, outshp, keyword=None,
                  epsg_out=4326, __encoding__='plain_str', keyAPI=None):
    """
    Search data in Twitter and create a vectorial file with that data
    """
    
    from gasp.to.shp import df_to_shp
    
    tweets = geotweets_location(
        buffer_shp, epsg_in, keyword=keyword,
        epsg_out=epsg_out, keyToUse=keyAPI,
        onlySearchAreaContained=None
    )
    
    try:
        if not tweets:
            return 0
    except:
        pass
    
    df_to_shp(tweets, outshp)
    
    return outshp


def tweets_to_df(keyword=None, inGeom=None, epsg=None, LANG='pt',
                 NTWEETS=1000, tweetType='mixed', apiKey=None):
    """
    Search for Tweets and Export them to XLS
    """
    
    from gasp.fm.api.twitter import search_tweets
    
    if not inGeom and not keyword:
        raise ValueError('inGeom or keyword, one of them are required')
    
    if inGeom and not epsg:
        raise ValueError('inGeom implies epsg')
    
    if inGeom:
        from gasp.cpu.gdl.anls.prox.bfs import getBufferParam
        
        x, y, dist = getBufferParam(inGeom, epsg, outSRS=4326)
        
        dist = float(dist) / 1000
    
    else:
        x, y, dist = None, None, None
        
    data = search_tweets(
        lat=y, lng=x, radius=dist,
        keyword=keyword, NR_ITEMS=NTWEETS, only_geo=None, __lang=LANG,
        resultType=tweetType, key=apiKey
    )
    
    try:
        if not data:
            return 0
    except:
        pass
    
    if keyword:
        data["keyword"] = keyword
    
    else:
        data["keyword"] = 'nan'
    
    return data


def tweets_to_xls(outxls, searchword=None, searchGeom=None, srs=None, lng='pt',
                  NTW=1000, twType='mixed', Key=None):
    """
    Search for Tweets and Export them to XLS
    """
    
    from gasp.to.xls import df_to_xls
    
    data = tweets_to_df(
        keyword=searchword, inGeom=searchGeom, epsg=srs,
        LANG=lng, NTWEETS=NTW, tweetType=twType, apiKey=Key
    )
    
    try:
        if not data:
            return 0
    except:
        pass
    
    df_to_xls(data, outxls, sheetsName='twitter')
    
    return outxls

