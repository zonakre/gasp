"""
Operations based on extent
"""

"""
GeoPandas Related
"""


def df_add_ext(df, geomCol):
    """
    Add minx, miny, maxx, maxy to dataframe
    """
    
    return df.merge(
        df[geomCol].bounds, how='inner',
        left_index=True, right_index=True
    )


def df_buffer_extent(inShp, inEpsg, meterTolerance, outShp):
    """
    For all geometries, calculate the boundary given by 
    the sum between the feature extent and the Tolerance variable
    """
    
    from shapely.geometry import Polygon
    from geopandas        import GeoDataFrame
    from gasp.fm          import tbl_to_obj
    from gasp.to.shp      import df_to_shp
    
    inDf = tbl_to_obj(inShp)
    
    inDf = df_add_ext(inDf, "geometry")
    
    inDf['minx'] = inDf.minx - meterTolerance
    inDf['miny'] = inDf.miny - meterTolerance
    inDf['maxx'] = inDf.maxx + meterTolerance
    inDf['maxy'] = inDf.maxy + meterTolerance
    
    # Produce new geometries
    geoms = [Polygon([
        [ext[0], ext[3]], [ext[1], ext[3]],
        [ext[1], ext[2]], [ext[0], ext[2]],
        [ext[0], ext[3]]
    ]) for ext in zip(inDf.minx, inDf.maxx, inDf.miny, inDf.maxy)]
    
    inDf.drop([
        'minx', 'miny', 'maxx', 'maxy', 'geometry'
    ], axis=1, inplace=True)
    
    result = GeoDataFrame(inDf, crs={
        'init' : 'epsg:{}'.format(inEpsg)
    }, geometry=geoms)
    
    return df_to_shp(inDf, outShp)

