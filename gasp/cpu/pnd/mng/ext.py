"""
Manage GeoData using their extent
"""


def buffer_extent(inShp, inEpsg, meterTolerance, outShp):
    """
    For all geometries, calculate the boundary given by 
    the sum between the feature extent and the Tolerance variable
    """
    
    from shapely.geometry  import Polygon
    from geopandas         import GeoDataFrame
    from gasp.fm.shp       import shp_to_df
    from gasp.cpu.pnd.prop import add_geom_ext
    from gasp.to.shp       import df_to_shp
    
    inDf = shp_to_df(inShp)
    
    inDf = add_geom_ext(inDf, "geometry")
    
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

