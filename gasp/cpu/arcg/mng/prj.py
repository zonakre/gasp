"""
Manage SRS with ArcGIS
"""

import arcpy


def shpFolder_project(shpFolder, outFolder, outEpsg):
    """
    Execute project for all feature classes in a Folder
    """
    
    import os
    
    arcpy.env.workspace = shpFolder
    
    fcs = arcpy.ListFeatureClasses()
    
    for shp in fcs:
        project(os.path.join(shpFolder, shp), os.path.join(outFolder, shp),
                outEpsg)


def transform_object(geom, outepsg):
    from gasp.fm.api.srorg import get_wkt_esri
    
    srsObj = get_wkt_esri(outepsg)
    
    return geom.projectAs(srsObj)


def transform_geomdict(inGeom, outEpsg, geomK="GEOM"):
    """
    Transform geometries in dict
    """
    
    from gasp.fm.api.srorg import get_wkt_esri
    
    srs_obj = get_wkt_esri(outEpsg)
    
    outGeom = {}
    for k in inGeom:
        outGeom[k] = {
            geomK : inGeom[k][geomK].projectAs(srs_obj)
        }
    
    return outGeom

