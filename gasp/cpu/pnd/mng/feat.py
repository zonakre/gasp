"""
Operations with Features
"""

def orig_dest_to_polyline(srcPoints, srcField, 
                          destPoints, destField, outShp):
    """
    Connect origins to destinations with a polyline which
    length is the minimum distance between the origin related
    with a specific destination.
    
    One origin should be related with one destination.
    These relations should be expressed in srcField and destField
    """
    
    from geopandas        import GeoDataFrame
    from shapely.geometry import LineString
    from gasp.fm.shp      import shp_to_df
    from gasp.to.shp      import df_to_shp
    
    srcPnt = shp_to_df(srcPoints)
    desPnt = shp_to_df(destPoints)
    
    joinDf = srcPnt.merge(destPnt, how='inner',
                          left_on=srcField, right_on=destField)
    
    joinDf["geometry"] = joinDf.apply(
        lambda x: LineString(
            x["geometry_x"], x["geometry_y"]
        ), axis=1
    )
    
    joinDf.drop(["geometry_x", "geometry_y"], axis=1, inplace=True)
    
    a = GeoDataFrame(joinDf)
    
    df_to_shp(joinDf, outShp)
    
    return outShp


def multipart_to_single(inDf, geomType):
    """
    Multipart Geometries to SinglePart Geometries
    """
    
    import geopandas
    import pandas
    
    df_wsingle = df[df.geometry.type == geomType]
    df_wmulti  = df[df.geometry.type == 'Multi' + geomType]
    
    for i, row in df_wmulti.iterrows():
        series_geom = pandas.Series(row.geometry)
        
        ndf = pandas.concat([geopandas.GeoDataFrame(
            row, crs=df_wmulti.crs).T]*len(series_geom), ignore_index=True)
        
        ndf['geometry'] = series_geom
        
        df_wsingle = pandas.concat([df_wsingle, ndf])
    
    df_wsingle.reset_index(inplace=True, drop=True)
    
    return df_wsingle

 