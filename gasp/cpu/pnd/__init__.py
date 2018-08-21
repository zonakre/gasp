"""
Play with GeoDataFrames
"""

def pnt_dfwxy_to_geodf(df, colX, colY, epsg):
    """
    Pandas Dataframe with numeric x, y columns
    to GeoDataframe
    
    Works Only for Points
    """
    
    from geopandas        import GeoDataFrame
    from shapely.geometry import Point
    
    geoms = [Point(xy) for xy in zip(df[colX], df[colY])]
    df.drop([colX, colY], axis=1, inplace=True)
    gdata = GeoDataFrame(
        df, crs={'init' : 'epsg:' + str(epsg)},
        geometry=geoms
    )
    
    return gdata


def regulardf_to_geodf(df, colGeom, epsg):
    """
    Regular Pandas Dataframe To GeoDataframe
    """
    
    from geopandas import GeoDataFrame
    
    return GeoDataFrame(
        df, crs={'init' : 'epsg:{}'.format(epsg)},
        geometry=colGeom
    )

