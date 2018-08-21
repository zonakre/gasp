"""
Open Elevation API Tools
"""

def get_points_elv(pntShp, output, epsg, elevationColumn="openelv"):
    """
    Extract elevation for several points
    """
    
    import pandas
    from threading                 import Thread
    from gasp.fm.api.openelv       import locations_elev
    from gasp.fm.shp               import shp_to_df
    from gasp.cpu.pnd.mng          import split_df
    from gasp.cpu.pnd.mng.prj      import project_df
    from gasp.cpu.pnd.mng.geomattr import pointxy_to_cols
    from gasp.mng.gen              import merge_df
    from gasp.prop.feat            import df_geom_type
    from gasp.to.obj               import df_to_list
    from gasp.to.shp               import df_to_shp
    
    # SHP TO DF
    df = shp_to_df(pntShp)
    
    # Check Geometry - shape should be of type point
    dfGeom = get_geom_type(df, geomCol="geometry", gisApi='pandas')
    if dfGeom != 'Point' and dfGeom != 'MultiPoint':
        raise ValueError('Geometries must be of type point')
    
    # Re-project GeoDataframes if needed
    if epsg != 4326:
        df = project_df(df, 4326)
    
    df  = pointxy_to_cols(
        df, geomCol="geometry", colX="longitude", colY="latitude"
    )
    
    df2 = df.drop([
        c for c in df.columns.values
        if c != "longitude" and c != "latitude"
    ], axis=1, inplace=False)
    
    dfs = split_df(df2, 200)
    
    RESULTS = []
    # Go to the net and extract elevation
    def extraction(pntDf):
        locations = df_to_list(pntDf)
        
        __result = locations_elev({"locations" : locations})
        
        RESULTS.append(pandas.DataFrame(__result["results"]))
    
    thrds = []
    for i in range(len(dfs)):
        thrds.append(Thread(
            name="elvt{}".format(str(i)), target=extraction,
            args=(dfs[i],)
        ))
    
    for t in thrds:
        t.start()
    
    for t in thrds:
        t.join()
    
    finalDf = merge_df(RESULTS, ignIndex=True)
    finalDf.rename(columns={"elevation" : elevationColumn}, inplace=True)
    
    # Join with Original Shape
    df["long_join"] = df.longitude.round(6) * 1000000
    df["long_join"] = df.long_join.astype(int)
    df[ "lat_join"] = df.latitude.round(6) * 1000000
    df[ "lat_join"] = df.lat_join.astype(int)
    finalDf["jlat"] = finalDf.latitude.round(6) * 1000000
    finalDf["jlat"] = finalDf.jlat.astype(int)
    finalDf["jlng"] = finalDf.longitude.round(6) * 1000000
    finalDf["jlng"] = finalDf.jlng.astype(int)
    
    newDf = df.merge(
        finalDf, how="outer",
        left_on  = ["long_join", "lat_join"],
        right_on = ["jlng", "jlat"]
    )
    
    if epsg != 4326:
        newDf = project_df(newDf, epsg)
    
    newDf.drop([
        "longitude_x", "longitude_y", "latitude_x", "latitude_y",
        "long_join", "lat_join", "jlng", "jlat"
    ], axis=1, inplace=True)
    
    return df_to_shp(newDf, output)

