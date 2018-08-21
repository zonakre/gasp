# -*- coding: utf-8 -*-
from __future__ import unicode_literals

def dissolve(inShp, outShp, fld,
             statistics="", geomMultiPart=True, api='arcpy'):
    """
    Dissolve Geometries
    
    API's Available:
    * arcpy;
    * qgis;
    """
    
    if api == 'arcpy':
        """
        Dissoling geometries with ArcGIS
        """
        
        import arcpy
    
        MULTIPART = "MULTI_PART" if geomMultiPart else "SINGLE_PART"
    
        arcpy.Dissolve_management(inShp, outShp, fld, statistics, MULTIPART, "")
    
    elif api == 'qgis':
        import processing
        
        processing.runalg("qgis:dissolve", inShp, False, fld, outShp)
    
    else:
        raise ValueError('The api {} is not available'.format(api))
    
    return outShp