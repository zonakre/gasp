"""
Elevation data extraction
"""

def elevation_to_pntshp(pnt_shp, epsg, fld_name='ELEVATION'):
    """
    Add an elevation attribute to a point feature class
    """
    
    from gasp.fm.api.glg.elev import pnts_elev
    from gasp.fm.shp          import shp_to_df
    from gasp.prop.feat       import get_geom_type
    from gasp.cpu.pnd.mng.prj import project_df
    from gasp.cpu.pnd.mng     import split_df
    from gasp.to.obj          import df_to_dict
    from gasp.to.shp          import df_to_shp
    
    # Check Geometries type - shapes should be of type point
    geomt = get_geom_type(pnt_shp, name=True, gisApi='ogr')
    if geomt != 'POINT' and geomt != 'MULTIPOINT':
        raise ValueError('All input geometry must be of type point')
    
    src = shp_to_df(pnt_shp)
    if epsg != 4326:
        src = project_df(src, 4326)
    
    # Get str with coords
    src["coords"] = src["geometry"].y.astype(str) + "," + \
        src["geometry"].x.astype(str)
    
    # Split dataframe
    dfs = split_df(src, 250)
    
    for df in dfs:
        coord_str = str(df.coords.str.cat(sep="|"))
        
        elvd = pnts_elev(coord_str)
    
    data = elvd
        
    return data