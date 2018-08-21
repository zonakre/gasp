# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
Data Management Tools > General
"""

"""
Pandas Objects Tools
"""

def merge_df(dfs, ignIndex=True):
    """
    Merge Multiple DataFrames into one
    """
    
    if type(dfs) != list:
        raise ValueError('dfs should be a list with Pandas Dataframe')
    
    result = dfs[0]
    
    for df in dfs[1:]:
        result = result.append(df, ignore_index=ignIndex, sort=True)
    
    return result

"""
Tools to process GIS Data in files
"""

def copy_feat(inShp, outShp, gisApi='arcpy'):
    """
    Copy Features to a new Feature Class
    """
    
    if gisApi == 'arcpy':
        import arcpy
        
        arcpy.CopyFeatures_management(inShp, outShp, "", "", "", "")
    
    else:
        raise ValueError('Sorry, API {} is not available'.format(gisApi))
    
    return outShp

