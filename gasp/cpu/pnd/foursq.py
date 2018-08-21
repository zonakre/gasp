"""
Querying by location and extract data location
"""


def venues_by_query(radialShp, epsgIn, epsgOut=4326, onlySearchAreaContained=True):
    """
    Get absolute location of foursquare data using the Foursquare API and
    Pandas to validate data.
    
    buffer_shp cloud be a shapefile with a single buffer feature
    or a dict like:
    buffer_shp = {
        x: x_value,
        y: y_value,
        r: dist
    }
    
    or a list or a tuple:
    buffer_shp = [x, y, r]
    """
    
    import pandas
    from shapely.geometry           import Polygon, Point
    from geopandas                  import GeoDataFrame
    from gasp.cpu.gdl.anls.prox.bfs import getBufferParam
    from gasp.fm.api.foursq         import search_places
    
    x, y, radius = getBufferParam(radialShp, epsgIn, outSRS=4326)
    
    data = search_places(y, x, radius)
    
    try:
        if not data:
            # Return 0
            return 0
    
    except:
        pass
    
    geoms = [Point(xy) for xy in zip(data.lng, data.lat)]
    data.drop(['lng', 'lat'], axis=1, inplace=True)
    gdata = GeoDataFrame(data, crs={'init' : 'epsg:4326'}, geometry=geoms)
    
    if onlySearchAreaContained:
        from shapely.wkt                import loads
        from gasp.cpu.gdl.mng.prj       import project_geom
        from gasp.cpu.gdl.anls.prox.bfs import coord_to_buffer
        
        _x, _y, _radius = getBufferParam(radialShp, epsgIn, outSRS=3857)
        searchArea = coord_to_buffer(float(_x), float(_y), float(_radius))
        searchArea = project_geom(searchArea, 3857, 4326)
        searchArea = loads(searchArea.ExportToWkt())
        
        gdata["tst_geom"] = gdata.geometry.intersects(searchArea)
        gdata = gdata[gdata.tst_geom == True]
        
        gdata.reset_index(drop=True, inplace=True)
        
        gdata.drop('tst_geom', axis=1, inplace=True)
    
    if epsgOut != 4326:
        from gasp.cpu.pnd.mng.prj import project_df
        gdata = project_df(gdata, epsgOut)
    
    return gdata


def venues_to_shp(inShp, inEpsg, outShp, outSRS=4326, onlyInsidePnt=None):
    """
    FourSquare Venues to ESRI Shapefile
    """
    
    from gasp.to.shp import df_to_shp
    
    df = venues_by_query(
        inShp, inEpsg, epsgOut=outSRS, onlySearchAreaContained=onlyInsidePnt
    )
    
    return df_to_shp(df, outShp)


