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
        result = result.append(df, ignore_index=ignIndex)#, sort=True)
    
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


def merge_feat(shps, outShp, api="ogr2ogr"):
    """
    Get all features in several Shapefiles and save them in one file
    """
    
    if api == "ogr2ogr":
        from gasp         import exec_cmd
        from gasp.prop.ff import drv_name
        
        out_drv = drv_name(outShp)
        
        # Create output and copy some features of one layer (first in shps)
        cmdout = exec_cmd('ogr2ogr -f "{}" {} {}'.format(
            out_drv, outShp, shps[0]
        ))
        
        # Append remaining layers
        lcmd = [exec_cmd(
            'ogr2ogr -f "{}" -update -append {} {}'.format(
                out_drv, outShp, shps[i]
            )
        ) for i in range(1, len(shps))]
    
    else:
        raise ValueError(
            "{} API is not available"
        )
    
    return outShp

