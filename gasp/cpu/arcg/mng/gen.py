"""
Manage Geographic data with ArcPy
"""

import arcpy


def merge(lst, outShp):
    """
    Merge Feature Classes into one
    """
    
    arcpy.Merge_management(';'.join(lst), outShp)
    
    return outShp


def append(inShp, targetShp):
    """
    Append inShp into targetShp
    """
    
    arcpy.Append_management(
        inShp, targetShp, "NO_TEST", "", ""
    )


def delete(__file):
    arcpy.Delete_management(__file)


def del_empty_files(folder, file_format):
    """
    List all feature classes in a folder and del the files with
    0 features
    """
    
    from gasp.oss       import list_files
    from gasp.prop.feat import feat_count
    
    fc = list_files(folder, file_format=file_format)
    
    for shp in fc:
        feat_number = feat_count(shp, gisApi='arcpy')
        
        if not feat_number:
            delete(shp)

