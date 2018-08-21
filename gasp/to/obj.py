# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Python Object To Python Object
"""

def df_to_dict(df, colsIsIndex=None, valueIsList=None):
    """
    Pandas Dataframe to Dict
    """
    
    if not colsIsIndex:
        if not valueIsList:
            return df.to_dict(orient="index")
        else:
            return df.T.to_dict(orient="list")
    
    else:
        return df.to_dict(orient="list")


def df_to_list(df):
    """
    Pandas Dataframe to List Like Array with dicts as values
    """
    
    return df.to_dict(orient="records")


def series_to_list(pndS):
    """
    Pandas series to List
    """
    
    return pndS.tolist()


def dict_to_df(df):
    """
    Dict to index
    """
    
    import pandas
    
    return pandas.DataFrame.from_dict(df, orient="index")


def obj_to_geodf(d, geom, epsg):
    """
    Dict to GeoDataFrame
    """
    
    from geopandas import GeoDataFrame
    
    return GeoDataFrame(
        d, crs={'init' : 'epsg:{}'.format(epsg)},
        geometry=geom
    )

def dict_to_geodf(d, geom, epsg):
    """
    Dict to GeoDataframe
    """
    
    from pandas       import DataFrame
    from gasp.cpu.pnd import regulardf_to_geodf
    
    df = DataFrame.from_dict(d, orient='index')
    
    return regulardf_to_geodf(df, colGeom=geom, epsg=epsg)

def json_obj_to_geodf(json_obj, epsg):
    """
    Json Object to GeoDataFrame
    """
    
    from geopandas import GeoDataFrame
    
    return GeoDataFrame.from_features(json_obj['features'], {
        'init' : 'epsg:{}'.format(epsg)
    })

