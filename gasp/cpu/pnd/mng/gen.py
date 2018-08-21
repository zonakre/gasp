"""
Operations
"""

def merge_shp(shps, outShp):
    """
    Merge shps into a new shp
    """
    
    from gasp.fm.shp import shp_to_df
    from gasp.to.shp import df_to_shp
    
    if type(shps) != list:
        raise ValueError('shps should be a list with paths for Feature Classes')
    
    dfs = [shp_to_df(shp) for shp in shps]
    
    result = dfs[0]
    
    for df in dfs[1:]:
        result = result.append(df, ignore_index=True, sort=True)
    
    df_to_shp(result, outShp)
    
    return outShp


def pnd_dissolve(shp, field, outShp):
    """
    Dissolve using GeoPandas
    """
    
    from gasp.fm.shp import shp_to_df
    from gasp.to.shp import df_to_shp
    
    df = shp_to_df(shp)
    
    dissDf = df.dissolve(by=field)
    
    return df_to_shp(df, outShp)

