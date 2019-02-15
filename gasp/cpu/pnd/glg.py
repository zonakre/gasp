"""
Google Maps
"""


def find_places(inShp, epsg, radius, output, keyword=None, type=None):
    """
    Extract places from Google Maps
    """
    
    import pandas;              import time
    from gasp.fm.api.glg.places import get_places_by_radius
    from gasp.fm.shp            import shp_to_df
    from gasp.cpu.pnd           import pnt_dfwxy_to_geodf
    from gasp.cpu.pnd.mng.prj   import project_df
    from gasp.cpu.pnd.mng.fld   import listval_to_newcols
    from gasp.to.shp            import df_to_shp
    
    pntDf = shp_to_df(inShp)
    pntDf = project_df(pntDf, 4326) if epsg != 4326 else pntDf
    
    pntDf['latitude']  = pntDf.geometry.y.astype(str)
    pntDf['longitude'] = pntDf.geometry.x.astype(str)
    
    DATA = 1
    def get_places(row):
        places = get_places_by_radius(
            row.latitude, row.longitude, radius, keyword, type
        )
        
        if type(DATA) == int:
            DATA = pandas.DataFrame(places['results'])
        
        else:
            DATA = DATA.append(
                pandas.DataFrame(places['results']),
                ignore_index=True
            )
    
    a = pntDf.apply(lambda x: get_places(x), axis=1)
    
    DATA = listval_to_newcols(DATA, 'geometry')
    fldsToDelete = ['viewport', 'opening_hours', 'icon', 'plus_code', 'photos']
    realDeletion = [x for x in fldsToDelete if x in DATA.columns.values]
    DATA.drop(realDeletion, axis=1, inplace=True)
    
    DATA = listval_to_newcols(DATA, 'location')
    
    DATA = pnt_dfwxy_to_geodf(DATA, 'lng', 'lat', 4326)
    
    if eps != 4326:
        DATA = project_df(DATA, epsg)
    
    DATA["types"] = DATA.types.astype(str)
    
    df_to_shp(DATA, output)
    
    return output

